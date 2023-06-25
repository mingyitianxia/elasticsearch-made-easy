## 17.1 Elasticsearch分片数要如何设置

### 17.1.3 分片及副本设置的建议
```
PUT /<index_name>/_settings
{
  "index.routing.allocation.total_shards_per_node": <number_of_shards>
}


```

### 17.2 25个核心Elasticsearch默认值

```
-XX:+UseConcMarkSweepGC
-XX:CMSInitiatingOccupancyFraction=75
-XX:+UseCMSInitiatingOccupancyOnly

-XX:+UseG1GC
-XX:MaxGCPauseMillis=50

```

## 17.3 Elasticsearch线程池和队列

### 17.3.1 线程池简介
```
GET /_cat/thread_pool/?v&h=id,name,active,rejected,completed,size,type&pretty&s=type 
```

## 17.4 深入解读Elasticsearch热点线程

### 17.4.1 hot_threads简介

```
GET /_nodes/hot_threads
GET /_nodes/<node_id>/hot_threads
```

## 17.6 Elasticsearch Java客户端的演进和选型

java 完整工程见：ESJavaClient.zip 
解压即可使用，原工程使用 Eclipse 编译器编译，如果使用其他编译器，略微调整即可。


## 17.7 Elasticsearch缓存深入详解

```
PUT my_index
{
  "settings": {
    "index.queries.cache.enabled": false
  }
}

POST /kimchy,elasticsearch/_cache/clear?request=true

PUT my_index
{
  "settings": {
    "index.requests.cache.enable": false
  }
}

PUT /my_index/_settings
{
  "index.requests.cache.enable": true
}


GET /my_index/_search?request_cache=true
{
  "size": 0,
  "aggs": {
    "popular_colors": {
      "terms": {
        "field": "colors"
      }
    }
  }
}

indices.requests.cache.size: 2%



GET /_stats/request_cache?human
GET /_nodes/stats/indices/request_cache?human


GET /_nodes/stats

GET /_cat/fielddata

（1）查询缓存
GET _cat/nodes?v&h=id,queryCacheMemory,queryCacheEvictions,requestCacheMemory,requestCacheHitCount,requestCacheMissCount,flushTotal,flushTotalTime
（2）清理节点查询缓存
POST /twitter/_cache/clear?query=true
（3）清理request请求缓存
POST /twitter/_cache/clear?request=true    
（4）清理field data缓存
POST /twitter/_cache/clear?fielddata=true 
（5）清理指定索引缓存
POST /kimchy,elasticsearch/_cache/clear
（6）清理全部缓存
POST /_cache/clear
```

## 17.8 Elasticsearch 数据建模指南

```
### 创建预处理管道
PUT _ingest/pipeline/indexed_at
{
  "description": "Adds indexed_at timestamp to documents",
  "processors": [
    {
      "set": {
        "field": "_source.indexed_at",
        "value": "{{_ingest.timestamp}}"
      }
    }
  ]
}
 
###创建索引，同时指定预处理管道
PUT my_index_0001
{
  "settings": {
    "number_of_replicas": 1,
    "number_of_shards": 3,
    "refresh_interval": "30s",
    "index": {
      "default_pipeline": "indexed_at"
    }
  }, 
  "mappings": {
    "properties": {
      "cont": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      }
    }
  }
}

PUT mix_index
{
  "mappings": {
      "properties": {
        "content": {
          "type": "text",
          "analyzer": "ik_max_word",
          "fields": {
            "standard": {
              "type": "text",
              "analyzer": "standard"
            },
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        }
      }
    }
}
 
POST mix_index/_search
{
  "query": {
    "bool": {
      "should": [
        {
          "match_phrase": {
            "content": "佟大"
          }
        },
        {
          "match_phrase": {
            "content.standard": "佟大"
          }
        }
      ]
    }
  }
}

PUT user/_doc/1
{
  "name":     "John Smith",
  "email":    "john@smith.com",
  "dob":      "1970/10/24"
}
 
PUT blogpost/_doc/2
{
  "title":    "Relationships",
  "body":     "It's complicated...",
  "user":     {
    "id":       1,
    "name":     "John Smith" 
  }
}
 
 
GET /blogpost/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "relationships"
          }
        },
        {
          "match": {
            "user.name": "John"
          }
        }
      ]
    }
  }
}
```