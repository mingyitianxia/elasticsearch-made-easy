## 8.2 新增文档

### 8.2.2 新增单条文档

#### 写入一条文档数据
```
PUT my_index_0801/_doc/1
{
  "user": "kimchy",
  "post_date": "2023-11-15T14:12:12",
  "message": "trying out Elasticsearch"
}
```

```
####关闭自动创建索引
PUT _cluster/settings
{
  "persistent": {
    "action.auto_create_index": "false"
  }
}
```

```
DELETE my_index_0802
PUT my_index_0802/_doc/1
{
  "user": "kimchy"
}
```

```
POST my_index_0801/_doc/
{
  "user": "kimchy",
  "post_date": "2023-01-15T14:12:12",
  "message": "trying out Elasticsearch"
}
```

### 8.2.3 批量新增文档

1.指定索引批量插入数据

```
POST my_index_0801/_bulk
{"index":{"_id":"1"}}
{"user":"aaa","post_date":"2023-11-15T14:12:12","message":"trying out Elasticsearch"}
{"index":{"_id":"2"}}
{"user":"bbb","post_date":"2023-11-15T14:12:12","message":"trying out Elasticsearch"}
{"index":{"_id":"3"}}
{"user":"ddd","post_date":"2023-11-15T14:12:12","message":"trying out Elasticsearch"}
```

2.批量执行多种操作

```
POST _bulk
{"index":{"_index":"my_index_0801","_id":"1"}}
{"field1":"value1"}
{"delete":{"_index":"my_index_0801","_id":"2"}}
{"create":{"_index":"my_index_0801","_id":"3"}}
{"field1":"value3"}
{"update":{"_id":"1","_index":"my_index_0801"}}
{"doc":{"field2":"value2"}}
```

## 8.3 删除文档

### 8.3.1 单个文档删除

```
DELETE my_index_0801/_doc/1
```

### 8.3.2 批量文档删除

```
####批量删除文档#
POST my_index_0801/_delete_by_query
{
  "query": {
    "match": {
      "message": "Elasticsearch"
    }
  }
}
```

```
GET _tasks
POST _tasks/r1A2WoRbTwKZ516z6NEs5A:36619/_cancel
```

## 8.4 修改/更新文档

### 8.4.1 更新文档的前置条件
```
PUT my_index_0803
{
  "mappings": {
    "_source": {
      "enabled": false
    }
  }
}

PUT my_index_0803/_doc/1
{
    "counter" : 1,
    "tags" : ["red"]
}

POST my_index_0803/_update/1
{
  "doc": {
    "counter": 2
  }
}
```

### 8.4.2 单个文档部分更新
```
####删除索引
DELETE my_index_0803
####创建索引
PUT my_index_0803
####写入数据
PUT my_index_0803/_doc/1
{
    "counter" : 1,
    "tags" : ["red"]
}
####更新操作
POST my_index_0803/_update/1
{
  "doc": {
    "name": "doctor wang"
  }
}
####执行检索
POST my_index_0803/_search
```

2. 在原有字段基础上部分修改字段值
```
####文档更新操作
POST my_index_0803/_update/1
{
  "script": {
    "source": "ctx._source.counter += params.count; ctx._source.tags.add(params.tag); ctx._source.phone = '18999998888'",
    "lang": "painless",
    "params": {
      "count": 4,
      "tag": "blue"
    }
  }
}

```

3. 存在则更新，不存在则插入给定值
```
####删除索引
DELETE my_index_0803
####借助upsert更新文档
POST my_index_0803/_update/1
{
  "script": {
    "source": "ctx._source.counter += params.count",
    "lang": "painless",
    "params": {
      "count": 4
    }
  },
  "upsert": {
    "counter": 1
  }
}
####执行检索操作
GET my_index_0803/_search
```

### 8.4.3 全部文档更新

```
####插入数据的同时，创建索引
PUT my_index_0803/_doc/1
{
  "user": "kimchy",
  "post_date": "2009-11-15T14:12:12",
  "message": "trying out Elasticsearch"
}
####执行检索
GET  my_index_0803/_search
```

### 8.4.4 批量文档更新

```
####借助painless实现批量更新
POST my_index_0803/_update_by_query
{
  "script": {
    "source": "ctx._source.counter++",
    "lang": "painless"
  },
  "query": {
    "term": {
      "counter": 5
    }
  }
}
```

```
#### 定义 ingest pipeline
PUT _ingest/pipeline/new-add-field
{
  "description": "new add title field",
  "processors": [
    {
      "set": {
        "field": "title",
        "value": "title testing..."
      }
    }
  ]
}

####更新的同时，指定pipeline
POST my_index_0803/_update_by_query?pipeline=new-add-field

####查看更新后的结果
GET my_index_0803/_search

```

### 8.4.5 取消更新

```
GET _tasks?detailed=true&actions=*byquery

GET /_tasks/r1A2WoRbTwKZ516z6NEs5A:36619

POST _tasks/r1A2WoRbTwKZ516z6NEs5A:36619/_cancel
```

## 8.5 reindex文档

### 8.5.1 reindex的背景及定义

```
#### reindex 实现数据迁移
POST _reindex
{
  "source": {
    "index": "my_index_0803"
  },
  "dest": {
    "index": "my_index_0804"
  }
}
```

```
####同集群索引之间全量数据迁移
POST _reindex
{
  "conflicts": "proceed",
  "source": {
    "index": "my_index_0803"
  },
  "dest": {
    "index": "my_index_0805"
  }
}
```

### 8.5.3 同集群索引之间基于特定条件迁移数据

```
#### 基于检索条件的部分结果数据迁移
POST _reindex
{
  "source": {
    "index": "my_index_0803",
    "query": {
      "term": {
        "user": "kimchy"
      }
    }
  },
  "dest": {
    "index": "my_index_0806"
  }
}

####基于脚本的删除操作
POST _reindex
{
  "source": {
    "index": "my_index_0803"
  },
  "dest": {
    "index": "my_index_0908",
    "version_type": "external"
  },
  "script": {
    "source": "if (ctx._source.user == 'kimchy') { ctx._source.remove('user')}",
    "lang": "painless"
  }
}

####批量写入数据
POST my_index_0909/_bulk
{"index":{"_id":1}}
{"title":" foo bar "}
####执行检索操作
GET my_index_0909/_search
####定义预处理管道
PUT _ingest/pipeline/my-trim-pipeline
{
  "description": "describe pipeline",
  "processors": [
    {
      "trim": {
        "field": "title"
      }
    }
  ]
}
####reindex同时指定预处理管道实现数据迁移
POST _reindex
{
  "source": {
    "index": "my_index_0909"
  },
  "dest": {
    "index": "my_index_0910",
    "pipeline": "my-trim-pipeline"
  }
}
####获取迁移后的检索结果
GET my_index_0910/_search
```

### 8.5.4 不同集群索引之间迁移数据

```
涉及跨集群数据迁移，必须要提前配置白名单。
reindex.remote.whitelist: "172.17.0.11:9200, 172.17.0.12:9200"
```

```
####执行索引迁移操作
POST _reindex
{
  "source": {
    "remote": {
      "host": "http://otherhost:9200"
    },
    "index": "source_index",
    "size": 10,
    "query": {
      "match": {
        "test": "data"
      }
    }
  },
  "dest": {
    "index": "my_index_0911"
  }
}
```

### 8.5.5 查看及取消reindex任务

```
####获取 reindex 相关任务
GET _tasks?detailed=true&actions=*reindex

####获取任ID及相关信息
GET /_tasks/r1A2WoRbTwKZ516z6NEs5A:36619

####取消任务
POST _tasks/r1A2WoRbTwKZ516z6NEs5A:36619/_cancel
```

