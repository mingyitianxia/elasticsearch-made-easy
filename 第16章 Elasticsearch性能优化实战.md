# 第16章 Elasticsearch性能优化实战

## 16.3 Elasticsearch写入优化

### 16.3.2 写入优化建议

```
PUT test-0001
{
  "settings": {
    "number_of_replicas": 0
  }
}

PUT test-008
{
  "settings": {
    "refresh_interval": -1
  }
}

PUT test-008
{
  "settings": {
    "refresh_interval": "30s"
  }
}

indices.memory.index_buffer_size: 10%


```

```
PUT my-index-000001
{
  "settings": {
    "index": {
      "sort.field": "date", 
      "sort.order": "desc"  
    }
  },
  "mappings": {
    "properties": {
      "date": {
        "type": "date"
      }
    }
  }
}
```

### 16.4.3 检索方式方法层面优化建议

```
####_source 控制返回字段
POST my_index_1701/_search
{
  "_source": [
    "url",
    "title"
  ],
  "query": {
    "match": {
      "content": "hello world"
    }
  }
}

PUT test_0001
{
  "mappings": {
    "properties": {
      "age":{
        "type":"integer",
        "fields": {
          "keyword":{
            "type":"keyword"
          }
        }
      }
    }
  }
}

PUT /my-index-000001
{
  "settings": {
    "index.store.preload": ["nvd", "dvd"]
  }
}

GET /my_index/_search
{
  "query": {
    "match": {
      "my_field": "my_value"
    }
  },
  "preference": "_prefer_nodes:node-1,node-3"
}


```

### 16.4.4 性能调优推荐实战DSL
```
GET _cat/shards?v&h=index,shard,prirep,state,unassigned.reason&s=state:asc

PUT my-index-2024.05.30-000002/_settings
{"number_of_replicas": 0}

PUT /_cluster/settings
{
  "transient": {
    "cluster.routing.allocation.enable": "all"
  }
}

POST /_cluster/reroute
{
  "commands": [
    {
      "move": {
        "index": "test",
        "shard": 0,
        "from_node": "node1",
        "to_node": "node2"
      }
    },
    {
      "allocate_replica": {
        "index": "test",
        "shard": 1,
        "node": "node3"
      }
    }
  ]
}

GET /_cat/allocation?v

GET /_cat/nodes?v&h=host,name,version

PUT /my-index-000001/_settings
{
  "index.search.slowlog.threshold.query.warn": "10s",
  "index.search.slowlog.threshold.query.info": "5s",
  "index.search.slowlog.threshold.query.debug": "2s",
  "index.search.slowlog.threshold.query.trace": "500ms",
  "index.search.slowlog.threshold.fetch.warn": "1s",
  "index.search.slowlog.threshold.fetch.info": "800ms",
  "index.search.slowlog.threshold.fetch.debug": "500ms",
  "index.search.slowlog.threshold.fetch.trace": "200ms",
  "index.search.slowlog.level": "info"
}

PUT my-index-000002
{
  "mappings": {
    "_routing": {
      "required": true 
    }
  }
}

POST /my-index-000001/_forcemerge

POST _bulk
{ "index" : { "_index" : "test", "_id" : "1" } }
{ "field1" : "value1" }
{ "delete" : { "_index" : "test", "_id" : "2" } }
{ "create" : { "_index" : "test", "_id" : "3" } }
{ "field1" : "value3" }
{ "update" : {"_id" : "1", "_index" : "test"} }
{ "doc" : {"field2" : "value2"} }

PUT /my-index-000001/_settings
{
  "index" : {
    "refresh_interval" : "30s"
  }
}

PUT my-index-000001/_settings
{
  "number_of_replicas": 0
}

PUT my-index-2023.06.03/_settings
{
  "index": {
    "translog": {
      "durability": "async"
    }
  }
}

ES_HEAP_SIZE=DESIRED_SIZE (e.g. "3g")


```