## 10.1 检索选型指南

### 10.1.2 精准匹配检索和全文检索的本质区别
```
####创建索引
PUT my_index_1001
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
      },
      "popular_degree": {
        "type": "integer"
      },
      "source_class": {
        "type": "keyword"
      }
    }
  }
}
####批量写入数据
POST my_index_1001/_bulk
{"index":{"_id":1}}
{"title":"乌兰图雅经典歌曲30首连播 标清_手机乐视视频","popular_degree":30,"souce_class":"wechat"}
{"index":{"_id":2}}
{"title":"乌兰县地区生产总值22.9亿元","popular_degree":10,"souce_class":"blog"}
{"index":{"_id":3}}
{"title":"乌兰新闻网欢迎您!","popular_degree":100,"souce_class":"news"}
{"index":{"_id":4}}
{"title":"乌兰:你说急什么呢,我30岁了","popular_degree":50,"souce_class":"weibo"}
{"index":{"_id":5}}
{"title":"千城胜景丨胜境美誉 多彩乌兰","popular_degree":50,"souce_class":"weibo"}
{"index":{"_id":6}}
{"title":"乌兰新世界百货","popular_degree":80,"souce_class":"news"}

POST my_index_1001/_search
{
  "query": {
    "match": {
      "title": "乌兰新闻网欢迎您!"
    }
  }
}


POST my_index_1001/_analyze
{
  "text": [
    "乌兰新闻网欢迎您"
  ],
  "field": "title"
}


POST my_index_1001/_search
{
  "profile": true, 
  "query": {
    "term": {
      "title.keyword": "乌兰新闻网欢迎您!"
    }
  }
}
```

### 10.1.3 精准匹配检索

- 1.Term单字段精准匹配

```
# 对text类型字段非要执行term检索，实战不推荐！！
POST my_index_1001/_search
{
  "profile": true, 
  "query": {
    "term": {
      "title": {
        "value": "乌兰:你说急什么呢,我30岁了"
      }
    }
  }
}
```

```
#### terms 多字段精准检索
POST my_index_1001/_search
{
  "query": {
    "terms": {
      "souce_class": [
        "weibo",
        "wechat"
      ]
    }
  }
}
```

```
#### range 区间范围检索
POST my_index_1001/_search
{
  "query": {
    "range": {
      "popular_degree": {
        "gte": 10,
        "lte": 100
      }
    }
  },
  "sort": [
    {
      "popular_degree": {
        "order": "desc"
      }
    }
  ]
}
```

```
#### exists检索
POST my_index_1001/_search
{
  "query": {
    "exists": {
      "field": "title.keyword"
    }
  }
}
```

```
POST my_index_1001/_search
{
  "profile": true, 
  "query": {
    "wildcard": {
      "title.keyword": {
        "value": "*乌兰*"
      }
    }
  }
}
```


```
#### 6.Prefix前缀匹配检索
####创建索引
PUT my_index_1002
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

####导入数据
POST my_index_1002/_bulk
{"index":{"_id":1}}
{"title":"考试专题"}
{"index":{"_id":2}}
{"title":"测试考试成绩题"}
{"index":{"_id":3}}
{"title":"新动能考试"}

####执行前缀匹配检索
POST my_index_1002/_search
{
  "query": {
    "prefix": {
      "title.keyword": {
        "value": "考试"
      }
    }
  }
}
```

```
#### 7.Terms set检索

PUT my_index_1003
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text"
      },
      "tags": {
        "type": "keyword"
      },
      "tags_count": {
        "type": "integer"
      }
    }
  }
}

POST my_index_1003/_bulk
{"index":{"_id":1}}
{"title":"电影1","tags":["喜剧","动作","科幻"],"tags_count":3}
{"index":{"_id":2}}
{"title":"电影2","tags":["喜剧","爱情","家庭"],"tags_count":3}
{"index":{"_id":3}}
{"title":"电影3","tags":["动作","科幻","家庭"],"tags_count":3}

GET my_index_1003/_search
{
  "query": {
    "terms_set": {
      "tags": {
        "terms": ["喜剧", "动作", "科幻"],
        "minimum_should_match_field": "tags_count"
      }
    }
  }
}

GET my_index_1003/_search
{
  "query": {
    "terms_set": {
      "tags": {
        "terms": [
          "喜剧",
          "动作",
          "科幻"
        ],
        "minimum_should_match_script": {
          "source": "doc['tags_count'].value * 0.7"
        }
      }
    }
  }
}
```

```
#### Fuzzy支持编辑距离的模糊检索

####创建索引
PUT my_index_1004
{
  "mappings": {
    "properties": {
      "title": {
        "type": "text",
        "analyzer": "english"
      }
    }
  }
}

####批量写入数据
POST my_index_1004/_bulk
{"index":{"_id":1}}
{"title":"Editing Language Skins"}
{"index":{"_id":2}}
{"title":"Mirroring Pages in Page Layouts"}
{"index":{"_id":3}}
{"title":"Applying Conditions to Content"}

####执行检索，输入：apple，langauge，pager均能召回数据。
POST my_index_1004/_search
{
  "query": {
    "fuzzy": {
      "title": {
        "value": "langauge"
      }
    }
  }
}

```

```
####基于id进行检索
POST my_index_1005/_search
{
  "query": {
    "ids": {
      "values": [
        "1",
        "2",
        "3"
      ]
    }
  }
}
```

```
GET my_index_1005/_search
{
  "query": {
    "regexp": {
      "product_name.keyword": {
        "value": "Lap.."
      }
    }
  }
}
```

```
####加上profile:true 参数，看底层执行逻辑。
POST my_index_1001/_search
{
  "profile": true,
  "query": {
    "match": {
      "title": "乌兰新闻"
    }
  }
}
```

- 2.Match phrase短语检索
```
####短语匹配检索
POST my_index_1001/_search
{
  "query": {
    "match_phrase": {
      "title": {
        "query": "乌兰新闻"
      }
    }
  }
}
```

```
#### mulit_match 检索案例
POST my_index_1001/_search
{
  "query": {
    "multi_match" : {
      "query" : "乌兰",
      "fields" : [ "title^3", "message" ] 
    }
  }
}
```

```
#### match_phrase_prefix检索案例
POST my_index_1001/_search
{
  "profile": true, 
  "query": {
    "match_phrase_prefix": {
      "title": "乌兰新"
    }
  }
}
```

```
#### query_string检索案例
POST my_index_1001/_search
{
  "query": {
    "query_string": {
      "default_field": "title",
      "query": "乌兰 AND 新闻"
    }
  }
}
```

```
POST my_index_1001/_search
{
  "query": {
    "query_string": {
      "query": "乌兰 AND 新闻 AND",
      "fields": ["title"]
    }
  }
}
```

### 10.1.6 query和filter的区别

```
####query和filter的组合检索语句
POST my_index_1005/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": "Search"
          }
        },
        {
          "match": {
            "content": "Elasticsearch"
          }
        }
      ],
      "filter": [
        {
          "term": {
            "status": "published"
          }
        },
        {
          "range": {
            "publish_date": {
              "gte": "2024-01-01"
            }
          }
        }
      ]
    }
  }
}
```

## 10.2 高亮、排序、分页

### 10.2.1 高亮

```
####高亮语法演示
POST kibana_sample_data_ecommerce/_search
{
  "_source": "products.product_name",
  "query": {
    "match": {
      "products.product_name": "dress"
    }
  },
  "highlight": {
    "number_of_fragments": 0,
    "fragment_size": 150,
    "fields": {
      "products.product_name": {
        "pre_tags": [
          "<em>"
        ],
        "post_tags": [
          "</em>"
        ]
      }
    }
  }
}
```

### 10.2.2 排序

```
#### text字段排序会报错
POST my_index_1001/_search
{
  "sort": [
    {
      "title": {
        "order": "desc"
      }
    }
  ]
}

####两种排序方式
POST my_index_1001/_search
{
  "query": {
    "match": {
      "title": "乌兰"
    }
  },
  "sort": [
    {
      "popular_degree": {
        "order": "desc"
      }
    },
    {
      "_score": {
        "order": "asc"
      }
    }
  ]
}
```

### 10.2.3 分页检索

```
####分页查询
POST my_index_1001/_search
{
  "from": 0,
  "size": 10,
  "query": {
    "match_all": {}
  }
}

####基于Kibana样例索引数据实现检索
POST kibana_sample_data_ecommerce/_search
{
  "from": 0,
  "size": 5,
  "_source": "products.product_name",
  "query": {
    "match": {
      "products.product_name": "dress"
    }
  }
}
```

## 10.3 自定义评分的N种方法

### 10.3.5 如何自定义Elasticsearch评分

- 1.Index Boost在索引层面修改相关性

```
####创建索引并写入数据
PUT my_index_110a/_doc/1
{
  "subject": "subject 1"
}
PUT my_index_110b/_doc/1
{
  "subject": "subject 1"
}
PUT my_index_110c/_doc/1
{
  "subject": "subject 1"
}


####执行检索

POST my_index_110*/_search
{
  "indices_boost": [
    {
      "my_index_110a": 1.5
    },
    {
      "my_index_110b": 1.2
    },
    {
      "my_index_110c": 1
    }
  ],
  "query": {
    "term": {
      "subject.keyword": {
        "value": "subject 1"
      }
    }
  }
}
```

- 2.boosting修改文档相关性
```
#### 通过boost提升字段评分
POST my_index_1001/_search
{
  "query": {
    "bool": {
      "must": [
        {
          "match": {
            "title": {
              "query": "新闻",
              "boost": 3
            }
          }
        }
      ]
    }
  }
}
```

- 3.negative_boost降低相关性
```
####想召回包含“乌兰”的数据，但只要包含“新闻”则降低评分为原评分的十分之一
POST my_index_1001/_search
{
  "query": {
    "boosting": {
      "positive": {
        "match": {
          "title": "乌兰"
        }
      },
      "negative": {
        "match": {
          "title": "新闻"
        }
      },
      "negative_boost": 0.1
    }
  }
}
```

- 4.function_score自定义评分
```
####批量写入数据
PUT my_index_1006/_bulk
{"index":{"_id":1}}
{"name":"A","sales":10,"visitors":10}
{"index":{"_id":2}}
{"name":"B","sales":20,"visitors":20}
{"index":{"_id":3}}
{"name":"C","sales":30,"visitors":30}

####基于function_score实现自定义评分检索
POST my_index_1006/_search
{
  "query": {
    "function_score": {
      "query": {
        "match_all": {}
      },
      "script_score": {
        "script": {
          "source": "_score * (doc['sales'].value+doc['visitors'].value)"
        }
      }
    }
  }
}

####基于field_value_factor修改评分，是的评分相对平滑，没有大的评分波动。
POST my_index_1001/_search
{
  "query": {
    "function_score": {
      "query": {
        "match": {
          "title": "乌兰"
        }
      },
      "field_value_factor": {
        "field": "popular_degree",
        "modifier": "log1p",
        "factor": 0.1,
        "missing": 1
      },
      "boost_mode": "sum"
    }
  }
}
```

- 5.rescore_query查询后二次打分
```
####基于rescore_query执行检索
POST my_index_1001/_search
{
  "query": {
    "match": {
      "title": "乌兰"
    }
  },
  "rescore": {
    "window_size": 50,
    "query": {
      "rescore_query": {
        "function_score": {
          "script_score": {
            "script": {
              "source": "doc['popular_degree'].value"
            }
          }
        }
      }
    }
  }
}
```

## 10.4 拆解检索模板

### 10.4.1 检索模板必备基础

```
####定义检索模板
PUT _scripts/cur_search_template
{
  "script": {
    "lang": "mustache",
    "source": {
      "query": {
      "match": {
        "{{cur_field}}": "{{cur_value}}"
      }
    },
    "size": "{{cur_size}}"
    }
  }
}
####基于检索模板进行检索
POST my_index_1007/_search/template
{
  "id": "cur_search_template",
  "params": {
    "cur_field":"itemid",
    "cur_value":1,
    "cur_size":50
    
  }
}

####创建索引
PUT my_index_1007
{
  "mappings": {
    "properties": {
      "clock": {
        "type": "date",
        "format": "epoch_second"
      },
      "itemid": {
        "type": "long"
      },
      "ns": {
        "type": "long"
      },
      "ttl": {
        "type": "long"
      },
      "value": {
        "type": "long"
      }
    }
  }
}
 
####批量插入数据
PUT my_index_1007/_bulk
{"index":{"_id":"1"}}
{"itemid":1,"ns":643214179,"clock":1597752311,"value":"1123","ttl":604800}
{"index":{"_id":"2"}}
{"itemid":2,"ns":643214179,"clock":1597752311,"value":"123555","ttl":604800}
{"index":{"_id":"3"}}
{"itemid":3,"ns":643214179,"clock":1597752311,"value":"1","ttl":604800}
{"index":{"_id":"4"}}
{"itemid":4,"ns":643214179,"clock":1597752311,"value":"134","ttl":604800}
{"index":{"_id":"5"}}
{"itemid":2,"ns":643214179,"clock":1597752311,"value":"123556","ttl":604800}

POST my_index_1007/_search/template
{
  "id": "item_agg",
  "params": {
    "itemid":{
      "statuses":[1,2]
    },
    "startTime":1597752309,
    "endTime":1597752333
    
  }
}

POST my_index_1007/_search
{
  "_source": [
    "value"
  ],
  "size": 0,
  "query": {
    "bool": {
      "filter": [
        {
          "terms": {
            "itemid": [
              1,
              2
            ]
          }
        },
        {
          "range": {
            "clock": {
              "gte": 1597752309000,
              "lte": 1597752333000
            }
          }
        }
      ]
    }
  },
  "aggs": {
    "group_terms": {
      "terms": {
        "field": "itemid"
      },
      "aggs": {
        "avg_value": {
          "avg": {
            "field": "value"
          }
        },
        "max_value": {
          "max": {
            "field": "value"
          }
        }
      }
    }
  }
}

GET _search/template
{
  "source": "{ \"query\": { \"terms\": {{#toJson}}statuses{{/toJson}} }}",
  "params": {
    "statuses" : {
        "itemid": [ 1, 2 ]
    }
  }
}

####创建检索模板
POST _scripts/test_script_01
{
  "script": {
    "lang": "mustache",
    "source": """{ "query": { "terms": {{#toJson}}statuses{{/toJson}} }}"""
  }
####基于检索模板执行检索
POST my_index_1007/_search/template 
{
  "id": "test_script_01",
  "params": {
    "statuses": {
      "itemid": [
        1,
        2
      ]
    },
    "startTime": 1597752309000,
    "endTime": 1597752333000
  }
}
GET _search/template
{
  "source": """{"_source":["value"],"size":0,"query":{"bool":{"filter":[{"terms":{{#toJson}}statuses{{/toJson}}},{"range":{"clock":{"gte":{{startTime}},"lte":{{endTime}}}}}]}},"aggs":{"group_terms":{"terms":{"field":"itemid"},"aggs":{"avg_value":{"avg":{"field":"value"}},"max_value":{"max":{"field":"value"}}}}}}""",
  "params": {
    "statuses": {
      "itemid": [
        1,
        2
      ]
    },
    "startTime": 1597752309000,
    "endTime": 1597752333000
  }
}
```

## 10.5 全方位深度解读Elasticsearch分页查询

### 10.5.2 From + size分页查询
```
GET kibana_sample_data_flights/_search
{
  "from": 10,
  "size":5,
  "query": {
    "match": {
      "DestWeather": "Sunny"
    }
  },
  "sort": [
    {
      "FlightTimeHour": {
        "order": "desc"
      }
    }
  ]
}
```

```
####样例搜索1
GET kibana_sample_data_flights/_search
{
  "from": 0,
  "size":10001
}
####样例搜索2
GET kibana_sample_data_flights/_search
{
  "from": 10001,
  "size":10
}
```

```
####动态调整参数
PUT kibana_sample_data_flights/_settings
{
    "index.max_result_window":50000
}
```

```
####深度分页查询举例
GET kibana_sample_data_flights/_search
{
  "from": 10001,
  "size": 10
}
```

### 10.5.3 search_after查询
```
#### 创建 PIT
POST kibana_sample_data_logs/_pit?keep_alive=1m
 
#### 获取数据量 14074
POST kibana_sample_data_logs/_count
 
#### 新增一条数据
POST kibana_sample_data_logs/_doc/14075
{
  "test":"just testing"
}
 
#### 数据总量为 14075
POST kibana_sample_data_logs/_count

####查询PIT，数据依然是14074，说明走的是之前时间点的视图的统计。
POST /_search
{
  "track_total_hits": true, 
  "query": {
    "match_all": {}
  }, 
   "pit": {
    "id": "48myAwEXa2liYW5hX3NhbXBsZV9kYXRhX2xvZ3MWM2hGWXpxLXFSSGlfSmZIaXJWN0dxUQAWdG1TOWFMTF9UdTZHdVZDYmhoWUljZwAAAAAAAAEN3RZGOFJCMGVrZVNndTk3U1I0SG81V3R3AAEWM2hGWXpxLXFSSGlfSmZIaXJWN0dxUQAA"
  }
}


#### Step 1: 创建 PIT
POST kibana_sample_data_logs/_pit?keep_alive=5m

#### Step 2: 创建基础查询
GET /_search
{
  "size":10,
  "query": {
    "match" : {
      "host" : "elastic"
    }
  },
  "pit": {
     "id":  "48myAwEXa2liYW5hX3NhbXBsZV9kYXRhX2xvZ3MWM2hGWXpxLXFSSGlfSmZIaXJWN0dxUQAWdG1TOWFMTF9UdTZHdVZDYmhoWUljZwAAAAAAAAEg5RZGOFJCMGVrZVNndTk3U1I0SG81V3R3AAEWM2hGWXpxLXFSSGlfSmZIaXJWN0dxUQAA", 
     "keep_alive": "1m"
  },
  "sort": [ 
    {"response.keyword": "asc"}
  ]
}

#### step 3 : 开始翻页
GET /_search
{
  "size": 10,
  "query": {
    "match" : {
      "host" : "elastic"
    }
  },
  "pit": {
     "id":  "48myAwEXa2liYW5hX3NhbXBsZV9kYXRhX2xvZ3MWM2hGWXpxLXFSSGlfSmZIaXJWN0dxUQAWdG1TOWFMTF9UdTZHdVZDYmhoWUljZwAAAAAAAAEg5RZGOFJCMGVrZVNndTk3U1I0SG81V3R3AAEWM2hGWXpxLXFSSGlfSmZIaXJWN0dxUQAA", 
     "keep_alive": "1m"
  },
  "sort": [
    {"response.keyword": "asc"}
  ],
  "search_after": [                                
    "200",
    4
  ]
}
```

### 10.5.4 Scroll遍历查询

```
POST kibana_sample_data_logs/_search?scroll=3m
{
  "size": 100,
  "query": {
    "match": {
      "host": "elastic"
    }
  }
}
```

```
POST _search/scroll                                   
{
  "scroll" : "3m",
"scroll_id":"FGluY2x1ZGVfY29udGV4dF91dWlkDXF1ZXJ5QW5kRmV0Y2gBFkY4UkIwZWtlU2d1OTdTUjRIbzVXdHcAAAAAAAGmkBZ0bVM5YUxMX1R1Nkd1VkNiaGhZSWNn" 
}
```