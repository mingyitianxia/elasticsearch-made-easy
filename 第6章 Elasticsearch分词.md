# 第6章 Elasticsearch分词

## 6.6 特定业务场景自定义分词案例


```
####创建索引
PUT my_index_0601
{
  "settings": {
    "analysis": {
      "char_filter": {},
      "tokenizer": {},
      "filter": {},
      "analyzer": {}
    }
  }
}
```

```
#### 删除索引
DELETE my_index_0601

#### 创建完整索引
PUT my_index_0601
{
  "settings": {
    "analysis": {
      "char_filter": {
        "my_char_filter": {
          "type": "mapping",
          "mappings": [
            ", => "
          ]
        }
      },
      "filter": {
        "my_synonym_filter": {
          "type": "synonym",
          "expand": true,
          "synonyms": [
            "leileili => lileilei",
            "meimeihan => hanmeimei"
          ]
        }
      },
      "analyzer": {
        "my_analyzer": {
          "tokenizer": "my_tokenizer",
          "char_filter": [
            "my_char_filter"
          ],
          "filter": [
            "lowercase",
            "my_synonym_filter"
          ]
        }
      },
      "tokenizer": {
        "my_tokenizer": {
          "type": "pattern",
          "pattern": """\;"""
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "my_analyzer"
      }
    }
  }
}
```

### 6.6.4 验证方案是否正确

```
POST my_index_0601/_analyze
{
  "analyzer": "my_analyzer",
  "text": "Li,LeiLei;Han,MeiMei"
}

POST my_index_0601/_analyze
{
  "field": "name",
  "text": "Li,LeiLei;Han,MeiMei"
}

####批量写入数据
POST my_index_0601/_bulk
{"index":{"_id":1}}
{"name":"Li,LeiLei;Han,MeiMei"}
{"index":{"_id":2}}
{"name":"LeiLei,Li;MeiMei,Han"}

####执行检索
POST my_index_0601/_search
{
  "query": {
    "match_phrase": {
      "name": "lileilei"
    }
  }
}
```

## 6.7 Ngram自定义分词案例

### 6.7.2 问题定义
```
####定义索引
PUT my_index_0602
{
  "mappings": {
    "properties": {
      "aname": {
        "type": "text"
      },
      "acode": {
        "type": "keyword"
      }
    }
  }
}
####批量写入数据
POST my_index_0602/_bulk
{"index":{"_id":1}}
{"acode":"160213.OF","aname":"X泰纳斯达克100"}
{"index":{"_id":2}}
{"acode":"160218.OF","aname":"X泰国证房地产"}

####执行模糊检索和高亮
POST my_index_0602/_search
{
  "highlight": {
    "fields": {
      "acode": {}
    }
  },
  "query": {
    "bool": {
      "should": [
        {
          "wildcard": {
            "acode": "*1602*"
          }
        }
      ]
    }
  }
}
```
### 6.7.5 Ngram实践
```
####创建ngram分词索引
PUT my_index_0603
{
  "settings": {
    "index.max_ngram_diff": 10,
    "analysis": {
      "analyzer": {
        "my_analyzer": {
          "tokenizer": "my_tokenizer"
        }
      },
      "tokenizer": {
        "my_tokenizer": {
          "type": "ngram",
          "min_gram": 4,
          "max_gram": 10,
          "token_chars": [
            "letter",
            "digit"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "aname": {
        "type": "text"
      },
      "acode": {
        "type": "text",
        "analyzer": "my_analyzer",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      }
    }
  }
}
####批量写入数据
POST my_index_0603/_bulk
{"index":{"_id":1}}
{"acode":"160213.OF","aname":"X泰纳斯达克100"}
{"index":{"_id":2}}
{"acode":"160218.OF","aname":"X泰国证房地产"}
```

```
POST my_index_0603/_analyze
{
  "analyzer": "my_analyzer",
  "text":"160213.OF"
}
```

```
POST my_index_0603/_search
{
  "highlight": {
    "fields": {
      "acode": {}
    }
  },
  "query": {
    "bool": {
      "should": [
        {
          "match_phrase": {
            "acode": {
              "query": "1602"
            }
          }
        }
      ]
    }
  }
}
```


