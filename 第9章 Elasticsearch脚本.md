## 9.1 Elasticsearch脚本的背景和定义

### 9.1.1 Elasticsearch脚本的背景

```
#### 批量写入数据同时创建索引
PUT my_index_0901/_bulk
{"index":{"_id":1}}
{"theatre":"Downtown","popularity":10}
{"index":{"_id":2}}
{"theatre":"Downstyle","popularity":3}

#### 执行检索操作
POST my_index_0901/_search
{
  "query": {
    "bool": {
      "filter": {
        "script": {
          "script": {
            "lang": "painless",
            "source": "doc['theatre.keyword'].value.startsWith('Down')"
          }
        }
      }
    }
  }
}
```

## 9.4 Elasticsearch脚本实战

### 9.4.1 自定义字段

```
####写入数据同时创建索引
POST my_index_0902/_bulk
{"index":{"_id":1}}
{"my_field":10,"insert_date":"2024-01-01T12:10:30Z"}

####实现自定义字段的检索
POST my_index_0902/_search
{
  "script_fields": {
    "my_doubled_field": {
      "script": {
        "lang": "expression",
        "source": "doc['my_field'] * multiplier",
        "params": {
          "multiplier": 2
        }
      }
    }
  }
}

#### 截取返回日期格式中的年份
POST my_index_0902/_search
{
  "script_fields": {
    "insert_year": {
      "script": {
        "source": "doc['insert_date'].value.getYear()"
      }
    }
  }
}
```

### 9.4.2 自定义评分

```
#### 自定义评分检索
POST my_index_0901/_search
{
  "query": {
    "function_score": {
      "script_score": {
        "script": {
          "lang": "expression",
          "source": "_score * doc['popularity']"
        }
      }
    }
  }
}
```

### 9.4.3 自定义更新

```
####已有字段更新为其他字段
POST my_index_0901/_update/1
{
  "script": {
    "lang": "painless",
    "source": """
       ctx._source.theatre = params.theatre;
     """,
    "params": {
      "theatre": "jingju"
    }
  }
}

####基于正则表达式更新
POST my_index_0901/_update_by_query
{
  "script": {
    "lang": "painless",
    "source": """
       if (ctx._source.theatre =~/^j/) {
         ctx._source.theatre += "matched";
       } else {
         ctx.op = "noop";
      }
    """
  }
}
```

### 9.4.4 自定义reindex
```
####创建索引
PUT my_index_0903
{
  "mappings": {
    "properties": {
      "field_x": {
        "type": "keyword"
      },
      "field_y": {
        "type": "keyword"
      }
    }
  }
}
####导入样例数据
POST my_index_0903/_bulk
{"index":{"_id":1}}
{"field_x":"abcd","field_y":"foo bar"}

####创建预处理管道
PUT _ingest/pipeline/change_pipeline
{
  "processors": [
    {
      "script": {
        "source": """
        ctx.field_x_len = ctx.field_x.length();
        """, 
        "lang": "painless"
      }
    },
    {
      "split": {
        "field": "field_y",
        "separator": " "
      }
    }
  ]
}
####基于预处理管道执行更新操作
POST my_index_0903/_update_by_query?pipeline=change_pipeline

####验证更新结果是否满足预期
POST my_index_0903/_search
```

### 9.4.5 自定义聚合
```
####基于脚本的聚合
POST my_index_0901/_search
{
  "aggs": {
    "terms_aggs": {
      "terms": {
        "script": {
          "source": "doc['popularity'].value",
          "lang": "painless"
        }
      }
    }
  }
}
```

