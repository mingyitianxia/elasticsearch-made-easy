# 第5章 Elasticsearch映射

## 5.1 映射定义

### 5.1.3 数据类型

#### 数组定义

```
PUT my_index_0501/_doc/1
{
  "media_array": [
    "新闻",
    "论坛",
    "博客",
    "电子报"
  ],
  "users_array": [
    {
      "name": "Mary",
      "age": 12
    },
    {
      "name": "John",
      "age": 10
    }
  ],
  "size_array": [
    0,
    50,
    100
  ]
}
```

```
#### 多字段类型Multi_fields
PUT my_index_0502
{
  "mappings": {
    "properties": {
      "cont": {
        "type": "text",
        "analyzer": "english",
        "fields": {
          "keyword": {
            "type": "keyword"
          },
          "stand": {
            "type": "text",
            "analyzer": "standard"
          }
        }
      }
    }
  }
}
```

```
#### Multi_fields 应用
PUT my_index_0503
{
  "mappings": {
    "properties": {
      "title": {
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
```

### 5.1.4 映射类型
```
#### 创建索引
PUT my_index_0504/_bulk
{"index":{"_id":1}}
{"cont":"Each document has metadata associated with it","visit_count":35,"publish_time":"2023-05-20T18:00:00"}
```

```
#### 字段匹配不正确
DELETE my_index_0505
PUT my_index_0505/_doc/1
{
  "create_date": "2020-12-26 12:00:00"
}
GET my_index_0505/_mapping
```

```
#### 提前设置匹配规则
DELETE my_index_0505
PUT my_index_0505
{
  "mappings": {
    "dynamic_date_formats": ["yyyy-MM-dd HH:mm:ss"]
  }
}
PUT my_index_0505/_doc/1
{
  "create_date": "2020-12-26 12:00:00"
}
GET my_index_0505/_mapping
```

```
#### 创建索引，指定dynamic:false
PUT my_index_0506
{
  "mappings": {
    "dynamic": false,
    "properties": {
      "user": {
        "properties": {
          "name": {
            "type": "text"
          },
          "social_networks": {
            "dynamic": true,
            "properties": {}
          }
        }
      }
    }
  }
}
```

```
#### 数据可以写入成功
PUT my_index_0506/_doc/1
{
  "cont": "Each document has metadata associated"
}

#### 检索不能找回数据，核心原因：cont是未映射字段
POST my_index_0506/_search
{
  "profile": true, 
  "query": {
    "match": {
      "cont": "document"
    }
  }
}

#### 可以返回结果
GET my_index_0506/_doc/1

#### Mapping中并没有cont
GET my_index_0506/_mapping
```

```
#### dynamic设置为strict
DELETE my_index_0507
PUT my_index_0507
{
  "mappings": {
    "dynamic": "strict", 
    "properties": {
      "user": { 
        "properties": {
          "name": {
            "type": "text"
          },
          "social_networks": { 
            "dynamic": true,
            "properties": {}
          }
        }
      }
    }
  }
}

#### 数据写入失败
PUT my_index_0507/_doc/1
{
  "cont": "Each document has metadata associated"
}
```

### 5.1.5 实战：Mapping创建后还可以更新吗
```
PUT my_index_0508
{
  "mappings": {
    "properties": {
      "name": {
        "properties": {
          "first": {
            "type": "text"
          }
        }
      },
      "user_id": {
        "type": "keyword"
      }
    }
  }
}
```

```
#### 如下Mapping是可以更新成功的。
PUT my_index_0508/_mapping
{
  "properties": {
    "name": {
      "properties": {
        "first": {
          "type": "text",
          "fields": {
            "field": {
              "type": "keyword"
            }
          }
        },
        "last": {
          "type": "text"
        }
      }
    },
    "user_id": {
      "type": "keyword",
      "ignore_above": 100
    }
  }
}
```

## 5.2 Nested类型及应用

### 5.2.1 Nested类型定义

```
#### 数据构造
PUT my_index_0509/_bulk
{"index":{"_id":1}}
{"title":"Invest Money","body":"Please start investing money as soon...","tags":["money","invest"],"published_on":"18 Oct 2017","comments":[{"name":"William","age":34,"rating":8,"comment":"Nice article..","commented_on":"30 Nov 2017"},{"name":"John","age":38,"rating":9,"comment":"I started investing after reading this.","commented_on":"25 Nov 2017"},{"name":"Smith","age":33,"rating":7,"comment":"Very good post","commented_on":"20 Nov 2017"}]}
```

```
#### 执行检索
POST my_index_0509/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "comments.name": "John"
          }
        },
        {
          "match": {
            "comments.age": 34
          }
        }
      ]
    }
  }
}
```

```
PUT my_index_0510
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "body": {
        "type": "text"
      },
      "tags": {
        "type": "keyword"
      },
      "published_on": {
        "type": "keyword"
      },
      "comments": {
        "type": "nested",
        "properties": {
          "name": {
            "type": "text"
          },
          "comment": {
            "type": "text"
          },
          "age": {
            "type": "short"
          },
          "rating": {
            "type": "short"
          },
          "commented_on": {
            "type": "text"
          }
        }
      }
    }
  }
}
```

```
#### 执行检索，不会召回结果。
POST my_index_0510/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "nested": {
            "path": "comments",
            "query": {
              "bool": {
                "must": [
                  {
                    "match": {
                      "comments.name": "john"
                    }
                  },
                  {
                    "match": {
                      "comments.age": 34
                    }
                  }
                ]
              }
            }
          }
        }
      ]
    }
  }
}
```

### 5.2.2  Nested类型的操作

```
#### Nested 增
POST my_index_0510/_doc/2
{
  "title": "Hero",
  "body": "Hero test body...",
  "tags": [
    "Heros",
    "happy"
  ],
  "published_on": "6 Oct 2018",
  "comments": [
    {
      "name": "steve",
      "age": 24,
      "rating": 18,
      "comment": "Nice article..",
      "commented_on": "3 Nov 2018"
    }
  ]
}
```

```
#### Nested 删
POST my_index_0510/_update/1
{
  "script": {
    "lang": "painless",
    "source": "ctx._source.comments.removeIf(it -> it.name == 'John');"
  }
}
```

```
#### 改
POST my_index_0510/_update/2
{
  "script": {
    "source": "for(e in ctx._source.comments){if (e.name == 'steve') {e.age = 25; e.comment= 'very very good article...';}}"
  }
}
```

```
#### 查
POST my_index_0510/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "nested": {
            "path": "comments",
            "query": {
              "bool": {
                "must": [
                  {
                    "match": {
                      "comments.name": "William"
                    }
                  },
                  {
                    "match": {
                      "comments.age": 34
                    }
                  }
                ]
              }
            }
          }
        }
      ]
    }
  }
}
```

```
#### 聚合
POST my_index_0510/_search
{
  "size": 0,
  "aggs": {
    "comm_aggs": {
      "nested": {
        "path": "comments"
      },
      "aggs": {
        "min_age": {
          "min": {
            "field": "comments.age"
          }
        }
      }
    }
  }
}
```

## 5.3 Join类型及应用

### 5.3.3 Join类型实战

```
#### Join定义
PUT my_index_0511
{
  "mappings": {
    "properties": {
      "my_join_field": {
        "type": "join",
        "relations": {
          "question": [
            "answer"
          ]
        }
      }
    }
  }
}
```

```
#### 写入父文档
POST my_index_0511/_doc/1
{
  "text": "This is a question",
  "my_join_field": "question" 
}

POST my_index_0511/_doc/2
{
  "text": "This is another question",
  "my_join_field": "question"
}
```

```
#### 写入子文档
PUT my_index_0511/_doc/3?routing=1&refresh 
{
  "text": "This is an answer",
  "my_join_field": {
    "name": "answer",
    "parent": "1"
  }
}

PUT my_index_0511/_doc/4?routing=1&refresh
{
  "text": "This is another answer",
  "my_join_field": {
    "name": "answer",
    "parent": "1"
  }
}
```

```
####Join 检索
POST my_index_0511/_search
{
  "query": {
    "match_all": {}
  }
}
````

```
#### 通过父文档查询子文档
POST my_index_0511/_search
{
  "query": {
    "has_parent": {
      "parent_type": "question",
      "query": {
        "match": {
          "text": "This is"
        }
      }
    }
  }
}
```

```
#### 通过子文档查询父文档
POST my_index_0511/_search
{
  "query": {
    "has_child": {
      "type": "answer",
      "query": {
        "match": {
          "text": "This is question"
        }
      }
    }
  }
}
```

```
#### Join 聚合操作
POST my_index_05611/_search
{
  "query": {
    "parent_id": { 
      "type": "answer",
      "id": "1"
    }
  },
  "aggs": {
    "parents": {
      "terms": {
        "field": "my_join_field#question", 
        "size": 10
      }
    }
  }
}
```

### 5.3.4 Join一对多实战

```
#### 一对多Join类型索引定义
PUT my_index_0512
{
  "mappings": {
    "properties": {
      "my_join_field": {
        "type": "join",
        "relations": {
          "question": [
            "answer",
            "comment"
          ]
        }
      }
    }
  }
}
```

```
#### 多对多Join类型索引定义
PUT my_index_0513
{
  "mappings": {
    "properties": {
      "my_join_field": {
        "type": "join",
        "relations": {
          "question": [
            "answer",
            "comment"
          ],
          "answer": "vote"
        }
      }
    }
  }
}
```

```
#### 孙子文档导入数据
PUT my_index_0513/_doc/3?routing=1&refresh
{
  "text": "This is a vote",
  "my_join_field": {
    "name": "vote",
    "parent": "2" 
  }
}
```

### 5.3.5 小结

```
#### 创建1个索引包含2个Join类型。
PUT my_index_0514
{
  "mappings": {
    "properties": {
      "my_join_field": {
        "type": "join",
        "relations": {
          "question": [
            "answer"
          ]
        }
      },
      "my_join_field_02": {
        "type": "join",
        "relations": {
          "question_02": [
            "answer_02"
          ]
        }
      }
    }
  }
}
```

## 5.4 Flattened类型及应用

### 5.4.1 Elasticsarch字段膨胀问题

```
#### 误操作，将检索语句写成插入语句。
PUT my_index_0515/_doc/1
{
  "query": {
    "bool": {
      "must": [
        {
          "nested": {
            "path": "comments",
            "query": {
              "bool": {
                "must": [
                  {
                    "match": {
                      "comments.name": "William"
                    }
                  },
                  {
                    "match": {
                      "comments.age": 34
                    }
                  }
                ]
              }
            }
          }
        }
      ]
    }
  }
}
```

### 5.4.3 Flattened类型解决的根本问题
```
PUT my_index_0516
{
  "settings": {
    "index.mapping.total_fields.limit": 2000
  }
}
```

### 5.4.4 Flattened类型实战解读

```
PUT my_index_0517
{
  "mappings": {
    "properties": {
      "host": {
        "type": "flattened"
      }
    }
  }
}
```

```
#### 写入数据
PUT my_index_0517/_doc/1
{
  "message": "[5592:1:0309/123054.737712:ERROR:child_process_sandbox_support_impl_linux.cc.",
  "fileset": {
    "name": "syslog"
  },
  "process": {
    "name": "org.gnome.Shell.desktop",
    "pid": 3383
  },
  "@timestamp": "2025-03-09T18:00:54.000+05:30",
  "host": {
    "hostname": "bionic",
    "name": "bionic"
  }
}
```

```
#### 更新Flattened字段，添加数据
POST my_index_0517/_update/1
{
  "doc": {
    "host": {
      "osVersion": "Bionic Beaver",
      "osArchitecture": "x86_64"
    }
  }
}
```

```
#### 精准匹配term检索
POST my_index_0517/_search
{
  "query": {
    "term": {
      "host": "Bionic Beaver"
    }
  }
}

POST my_index_0617/_search
{
  "query": {
    "term": {
      "host.osVersion": "Bionic Beaver"
    }
  }
}
```

```
#### match全文类型检索
POST my_index_0517/_search
{
  "query": {
    "match": {
      "host.osVersion": "bionic beaver"
    }
  }
}
 
POST my_index_0517/_search
{
  "query": {
    "match": {
      "host.osVersion": "Beaver"
    }
  }
}
```

## 5.6 内部数据结构解读

### 5.6.3 doc_values正排索引

```
PUT my_index_0618
{
  "mappings": {
    "properties": {
      "title": {
        "type": "keyword",
        "doc_values": false
      }
    }
  }
}
```

### 5.6.4 fielddata

```
PUT my_index_0619
{
  "mappings": {
    "properties": {
      "body":{
        "type":"text",
        "analyzer": "standard",
        "fielddata": true
      }
    }
  }
}
POST my_index_0619/_bulk
{"index":{"_id":1}}
{"body":"The quick brown fox jumped over the lazy dog"}
{"index":{"_id":2}}
{"body":"Quick brown foxes leap over lazy dogs in summer"}

GET my_index_0619/_search
{
  "size": 0,
  "query": {
    "match": {
      "body": "brown"
    }
  },
  "aggs": {
    "popular_terms": {
      "terms": {
        "field": "body"
      }
    }
  }
}
```

### 5.6.5 _source字段解读
```
PUT my_index_0620
{
  "mappings": {
    "_source": {
      "enabled": false
    }
  }
}
```

### 5.6.6 store字段解读

```
#### store使用举例
PUT my_index_0621
{
  "mappings": {
    "_source": {
      "enabled": false
    },
    "properties": {
      "title": {
        "type": "text",
        "store": true
      },
      "date": {
        "type": "date",
        "store": true
      },
      "content": {
        "type": "text"
      }
    }
  }
}
PUT my_index_0621/_doc/1
{
  "title":   "Some short title",
  "date":    "2021-01-01",
  "content": "A very long content field..."
}
#### 不能召回数据
GET my_index_0621/_search

#### 可以召回数据
GET my_index_0621/_search
{
  "stored_fields": [ "title", "date" ] 
}
```

## 5.7 详解null value

```
#### 创建索引
PUT  my_index_0622
{
  "mappings": {
    "properties": {
      "status_code": {
        "type": "keyword"
      },
      "title": {
        "type": "text"
      }
    }
  }
}
#### 批量写入数据
PUT  my_index_0622/_bulk
{"index":{"_id":1}}
{"status_code":null,"title":"just test"}
{"index":{"_id":2}}
{"status_code":"","title":"just test"}
{"index":{"_id":3}}
{"status_code":[],"title":"just test"}

#### 执行检索
POST  my_index_0622/_search
{
  "query": {
    "term": {
      "status_code": null
    }
  }
}
```

### 5.7.1 null_value的含义

```
#### 创建索引
PUT my_index_0523
{
  "mappings": {
    "properties": {
      "status_code": {
        "type":       "keyword",
        "null_value": "NULL"
      }
    }
  }
}

#### 批量写入数据
PUT my_index_0523/_bulk
{"index":{"_id":1}}
{"status_code":null}
{"index":{"_id":2}}
{"status_code":[]}
{"index":{"_id":3}}
{"status_code":"NULL"}

#### 执行检索
POST my_index_0523/_search
{
  "query": {
    "term": {
      "status_code": "NULL"
    }
  }
}
```

### 5.7.2 null_value使用的注意事项

```
PUT my_index_0524
{
  "mappings": {
    "properties": {
      "status_code": {
        "type": "keyword"
      },
      "title": {
        "type": "long",
        "null_value": "NULL"
      }
    }
  }
}
```

### 5.7.3 支持null_value的核心字段

```
PUT my_index_0525
{
  "mappings": {
    "properties": {
      "status_code": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "null_value": "NULL"
      }
    }
  }
}
```

```
PUT my_index_0526
{
  "mappings": {
    "properties": {
      "status_code": {
        "type": "keyword"
      },
      "title": {
        "type": "text",
        "fields": {
          "keyword": {
            "type": "keyword",
            "null_value": "NULL"
          }
        }
      }
    }
  }
}
```