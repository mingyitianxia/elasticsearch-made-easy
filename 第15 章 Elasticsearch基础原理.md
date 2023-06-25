## 15.1 Elasticsearch文档版本原理

### 15.1.1 Elasticsearch版本冲突复现
```
DELETE my_index_1501
# 执行创建并写入
PUT my_index_1501/_create/1
{
  "@timestamp": "2099-11-15T13:12:00",
  "message": "GET /search HTTP/1.1 200 1070000",
  "user": {
    "id": "kimchy"
  }
}
 
# 再次执行会报版本冲突错误。
# 报错信息：[1]: version conflict, document already exists (current version [1])
PUT my_index_1501/_create/1
{
  "@timestamp": "2099-11-15T13:12:00",
  "message": "GET /search HTTP/1.1 200 1070000",
  "user": {
    "id": "kimchy"
  }
}
```

- 1.场景1：create场景冲突
```
#!/bin/sh
while true; do
    s=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 10)
    curl -u elastic:changeme -s -X POST '172.21.0.14:29200/test/_bulk' -H 'Content-Type: application/x-ndjson' -d \
    '{ "index": { "_index": "test", "_id": "1" } }
     { "name": "update", "foo": "'$s'" } 
    { "index": { "_index": "test", "_id": "2" } }
    { "name": "update", "foo": "'$s'" } 
    { "index": { "_index": "test", "_id": "3" } }
    { "name": "update", "foo": "'$s'" } 
'
    echo ''
done
```
- 2.场景2：批量更新场景冲突
```
#!/bin/sh
while true; do
    s=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 10)
    curl -u elastic:changeme -s -X POST '172.21.0.14:29200/test/_update_by_query' -H 'Content-Type: application/json' -d \
   '{
    "query": {
        "match": {
            "name": {
                "query": "update"
            }
        }
    },
    "script": {
        "lang": "painless",
        "source": "ctx._source['"'foo'"'] = '"'$s'"'"
    }
   }'
    echo ''
    sleep 1
done
```
- 3.场景3：批量删除场景冲突
```
#!/bin/sh
while true; do
    s=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 10)
    curl -u elastic:changeme -s -X POST '172.21.0.14:29200/test/_delete_by_query' -H 'Content-Type: application/json' -d \
   '{
    "query": {
        "match": {
            "name": {
                "query": "update"
            }
        }
    }
   }'
    echo ''
    sleep 1
done
```

### 15.1.2 Elasticsearch文档版本定义

```
GET my_index_1501/_doc/1
```

### 15.1.6 如何解决或者避免Elasticsearch文档版本冲突
```
PUT my_index_1501/_doc/1?version=2
{
  "user": {
    "id": "elkbee"
  }
}
```

```
PUT my_index_1501/_doc/1?version=2&version_type=external
{
  "user": {
    "id": "elkbee"
  }
}
```

- 2.利用 if_seq_no 和 if_primary_term 作为唯一标识来避免版本冲突
```
PUT my_index_1502/_doc/1567
{
  "product" : "r2d2",
  "details" : "A resourceful astromech droid"
}
# 查看ifseqno 和 ifprimaryterm 
GET my_index_1502/_doc/1567

# 模拟数据打标签的过程
PUT my_index_1502/_doc/1567?if_seq_no=0&if_primary_term=1
{
  "product": "r2d2",
  "details": "A resourceful astromech droid",
  "tags": [
    "droid"
  ]
}
 
 
# 再获取数据
GET my_index_1502/_doc/1567
```

- 3.批量更新和批量删除忽略冲突实现
```
POST test/_update_by_query?conflicts=proceed
{
  "query": {
    "match": {
      "name": "update"
    }
  },
  "script": {
    "source": "ctx._source['foo'] = '123ss'",
    "lang": "painless"
  }
}
```


```
#!/bin/sh
while true; do
    s=$(tr -dc A-Za-z0-9 < /dev/urandom | head -c 10)
    curl -u elastic:changeme -s -X POST '172.21.0.14:29200/test/_delete_by_query?conflicts=proceed' -H 'Content-Type: application/json' -d \
   '{
    "query": {
        "match": {
            "name": {
                "query": "update"
            }
        }
    }
   }'
    echo ''
    sleep 1
done
```

## 15.2 Elasticsearch文档更新/删除的原理

### 15.2.2 通过实战再看文档版本号的变化
```
#### 执行一次
PUT my_index_1503/_doc/1
{
    "counter" : 2,
    "tags" : ["blue"]
}
 
# "_version" : 1,
GET my_index_1503/_doc/1
 
#### "count" : 1, "deleted" : 0
GET my_index_1503/_stats
 
#### 再执行一次（更新操作）
####  "_version" : 2（版本号 + 1）,
PUT my_index_1503/_doc/1
{
    "counter" : 3,
    "tags" : ["blue","green"]
}
```

```
DELETE my_index_1503/_doc/1
```

### 15.2.3文档删除、索引删除、文档更新的本质

```
POST my_index_1503/_forcemerge?only_expunge_deletes

####删除后，显示"count":0, "deleted":0
GET my_index_1503/_stats
```

```
2. 索引删除的本质
DELETE my_index_1503
```
### 15.2.4 解决两个实战问题

```
POST kibana_sample_data_ecommerce/_delete_by_query
{
  "query":{
    "range":{
      "order_id":{
        "gt": 584670
      }
    }
  }
}
```

```
GET kibana_sample_data_ecommerce/_stats
```

## 15.3 Elasticsearch写入原理

```
PUT my_index_1504/_doc/1
{
  "title":"just testing"
}
 
# 默认一秒的刷新频率，秒级可见（用户无感知）
GET test_0001/_search

DELETE my_index_1504
# 设置了60秒的刷新频率
PUT my_index_1504
{
  "settings": {
    "index":{
      "refresh_interval":"60s"
    }
  }
}
 
PUT my_index_1504/_doc/1
{
  "title":"just testing"
}
# 60s后才可以被搜索到
GET  my_index_1504/_search
```

```

POST /my-index-000001/_flush
```
