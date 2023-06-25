## 4.1 索引的定义

### 4.1.2 索引定义实现

```
PUT index_00001
```
```
PUT hamlet-1
{
  "settings": {
    "number_of_shards": 2,
    "number_of_replicas": 1
  },
  "mappings": {
    "properties": {
      "cont":{
        "type":"text",
        "analyzer": "ik_max_word",
        "fields": {
          "field":{
            "type":"keyword"
          }
        }
      }
    }
  },
  "aliases": {
    "hamlet": {}
  }
}
```
```
PUT news_index/_settings
{
  "number_of_replicas": 3
}
```
```
PUT news_index/_settings
{
  "refresh_interval": "30s"
}
```
```
PUT news_index/_settings
{
  "max_result_window": 50000
}
```

### 4.2.1 新增/创建索引
```
PUT myindex
```

### 4.2.2 删除索引
```
DELETE myindex
```

### 4.2.3 修改索引
```
POST /_aliases
{
  "actions": [
    {
      "add": {
        "index": "myindex",
        "alias": "myindex_alias"
      }
    }
  ]
}
```

### 4.2.4 查询索引
```
GET myindex
GET myindex/_search
```

### 4.3.3 别名的实现
```
PUT myindex
{
  "aliases": {
    "myindex_alias": {}
  },
  "settings": {
    "refresh_interval": "30s",
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}

POST visitor_logs_202301,visitor_logs_202302/_search

POST visitor_logs_*/_search

PUT visitor_logs_202301
PUT visitor_logs_202302

POST /_aliases
{
  "actions": [
    {
      "add": {
        "index": "visitor_logs_202301",
        "alias": "visitor_logs"
      }
    },
    {
      "add": {
        "index": "visitor_logs_202302",
        "alias": "visitor_logs"
      }
    }
  ]
}

POST visitor_logs/_search
```

### 4.3.4 别名使用的常见问题
```
POST visitor_logs/_bulk
{"index":{}}
{"title":"001"}

POST /_aliases
{
  "actions": [
    {
      "add": {
        "index": "visitor_logs_202302",
        "alias": "visitor_logs",
        "is_write_index": true
      }
    }
  ]
}
#再指定别名批量写入数据就不会报错！
POST visitor_logs/_bulk
{"index":{}}
{"title":"001"}

GET _cat/aliases?v

```

## 4.4 索引模板

### 4.4.2 模板定义
```
PUT _index_template/template_1
{
  "index_patterns": [
    "te*",
    "bar*"
  ],
  "template": {
    "aliases": {
      "alias1": {}
    },
    "settings": {
      "number_of_shards": 1
    },
    "mappings": {
      "_source": {
        "enabled": false
      },
      "properties": {
        "host_name": {
          "type": "keyword"
        },
        "created_at": {
          "type": "date",
          "format": "EEE MMM dd HH:mm:ss Z yyyy"
        }
      }
    }
  }
}
```

组件模版
```
PUT _component_template/component_mapping_template
{
  "template": {
    "mappings": {
      "properties": {
        "@timestamp": {
          "type": "date"
        },
        "host_name": {
          "type": "keyword"
        },
        "created_at": {
          "type": "date",
          "format": "EEE MMM dd HH:mm:ss Z yyyy"
        }
      }
    }
  }
}

PUT _component_template/component_settings_template
{
  "template": {
    "settings": {
      "number_of_shards": 3
    },
     "aliases": {
      "mydata": { }
    }
  }
}

PUT _index_template/mydata_template
{
  "index_patterns": [
    "mydata*"
  ],
  "priority": 500,
  "composed_of": [
    "component_mapping_template",
    "component_settings_template"
  ],
  "version": 1,
  "_meta": {
    "description": "my custom template"
  }
}

```


### 4.4.3 模板基础操作

```
PUT _index_template/template_1
DELETE _index_template/template_1
GET _index_template/template_1
```

### 4.4.4 动态模板实战

```
PUT _index_template/sample_dynamic_template
{
  "index_patterns": [
    "sample*"
  ],
  "template": {
    "mappings": {
      "dynamic_templates": [
        {
          "handle_integers": {
            "match_mapping_type": "long",
            "mapping": {
              "type": "integer"
            }
          }
        },
        {
          "handle_date": {
            "match": "date_*",
            "mapping": {
              "type": "date"
            }
          }
        }
      ]
    }
  }
}

DELETE sampleindex
PUT sampleindex/_doc/1
{
  "ivalue":123,
  "date_curtime":"1574494620000"
}

GET sampleindex/_mapping

```


