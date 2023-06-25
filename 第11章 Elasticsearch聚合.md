
```
####创建索引
PUT my_index_1101
{
  "mappings": {
    "properties": {
      "color": {
        "type": "keyword"
      },
      "name": {
        "type": "keyword"
      }
    }
  }
}


####批量导入数据
POST my_index_1101/_bulk
{"index":{"_id":1}}
{"color":"red","name":"red_01"}
{"index":{"_id":2}}
{"color":"red","name":"red_02"}
{"index":{"_id":3}}
{"color":"red","name":"red_03"}
{"index":{"_id":4}}
{"color":"green","name":"green_01"}
{"index":{"_id":5}}
{"color":"blue","name":"blue_02"}
{"index":{"_id":6}}
{"color":"green","name":"green_02"}
{"index":{"_id":7}}
{"color":"blue","name":"blue_03"}


####执行聚合操作
POST my_index_1101/_search
{
  "size": 0,
  "aggs": {
    "color_terms_agg": {
      "terms": {
        "field": "color"
      }
    }
  }
}
```

```
#### 创建索引
PUT my_index_1102
{
  "mappings": {
    "properties": {
      "size": {
        "type": "integer"
      },
      "name": {
        "type": "keyword"
      }
    }
  }
}


#### 批量导入数据，和图11-7一一对应
POST my_index_1102/_bulk
{"index":{"_id":0}}
{"size":0,"name":"red_0"}
{"index":{"_id":1}}
{"size":1,"name":"red_1"}
{"index":{"_id":2}}
{"size":2,"name":"green_2"}
{"index":{"_id":3}}
{"size":3,"name":"yellow_3"}
{"index":{"_id":4}}
{"size":4,"name":"green_4"}
{"index":{"_id":5}}
{"size":5,"name":"blue_5"}
{"index":{"_id":6}}
{"size":6,"name":"yellow_6"}
{"index":{"_id":7}}
{"size":7,"name":"blue_7"}
{"index":{"_id":8}}
{"size":8,"name":"green_8"}
{"index":{"_id":9}}
{"size":9,"name":"green_9"}

####执行指标聚合统计最大值、最小值
POST my_index_1102/_search
{
  "size": 0,
  "aggs": {
    "max_agg": {
      "max": {
        "field": "size"
      }
    },
    "min_agg": {
      "min": {
        "field": "size"
      }
    },
    "avg_agg": {
      "avg": {
        "field": "size"
      }
    }
  }
}
```

```
####stats指标聚合统计
POST my_index_1102/_search
 {
   "size": 0,
   "aggs": {
     "size_stats": {
       "stats": {
         "field": "size"
       }
     }
   }
 }
```

```
####创建索引
PUT my_index_1103
{
  "mappings": {
    "properties": {
      "has_hole": {
        "type": "keyword"
      },
      "color": {
        "type": "keyword"
      },
      "size": {
        "type": "integer"
      },
      "name": {
        "type": "keyword"
      }
    }
  }
}

####批量写入数据
POST my_index_1103/_bulk
{"index":{"_id":0}}
{"size":0,"name":"red_0","has_hole":0,"color":"red"}
{"index":{"_id":1}}
{"size":1,"name":"red_1","has_hole":0,"color":"red"}
{"index":{"_id":2}}
{"size":2,"name":"green_2","has_hole":0,"color":"green"}
{"index":{"_id":3}}
{"size":3,"name":"yellow_3","has_hole":0,"color":"yellow"}
{"index":{"_id":4}}
{"size":4,"name":"green_4","has_hole":0,"color":"green"}
{"index":{"_id":5}}
{"size":5,"name":"blue_5","has_hole":0,"color":"blue"}
{"index":{"_id":6}}
{"size":6,"name":"yellow_6","has_hole":0,"color":"yellow"}
{"index":{"_id":7}}
{"size":7,"name":"blue_7","has_hole":0,"color":"blue"}
{"index":{"_id":8}}
{"size":8,"name":"green_8","has_hole":0,"color":"green"}
{"index":{"_id":9}}
{"size":9,"name":"green_9","has_hole":0,"color":"green"}
{"index":{"_id":10}}
{"size":7,"name":"red_hole_7","has_hole":1,"color":"red"}
{"index":{"_id":11}}
{"size":8,"name":"red_hole_8","has_hole":1,"color":"red"}
{"index":{"_id":12}}
{"size":0,"name":"yellow_hole_0","has_hole":1,"color":"yellow"}
{"index":{"_id":13}}
{"size":4,"name":"yellow_hole_4","has_hole":1,"color":"yellow"}
{"index":{"_id":14}}
{"size":6,"name":"yellow_hole_6","has_hole":1,"color":"yellow"}
{"index":{"_id":15}}
{"size":5,"name":"yellow_hole_5","has_hole":1,"color":"yellow"}
{"index":{"_id":16}}
{"size":3,"name":"green_hole_3","has_hole":1,"color":"green"}
{"index":{"_id":17}}
{"size":1,"name":"blue_hole_1","has_hole":1,"color":"blue"}
{"index":{"_id":18}}
{"size":2,"name":"blue_hole_1","has_hole":1,"color":"blue"}
```

```
####聚合内嵌套聚合实现
POST my_index_1103/_search
{
  "size": 0,
  "aggs": {
    "hole_terms_agg": {
      "terms": {
        "field": "has_hole"
      },
      "aggs": {
        "color_terms": {
          "terms": {
            "field": "color"
          }
        }
      }
    }
  }
}


####pipeline管道子聚合
POST my_index_1103/_search
{
  "size": 0,
  "aggs": {
    "hole_terms_agg": {
      "terms": {
        "field": "has_hole"
      },
      "aggs": {
        "max_value_aggs": {
          "max": {
            "field": "size"
          }
        }
      }
    },
    "max_hole_color_aggs": {
      "max_bucket": {
        "buckets_path": "hole_terms_agg>max_value_aggs"
      }
    }
  }
}
```

## 11.2 Composite聚合：聚合后分页新实现

```
####数据建模
PUT my_index_1104
{
  "mappings": {
    "properties": {
      "brand": {
        "type": "keyword"
      },
      "pt": {
        "type": "date"
      },
      "name": {
        "type": "keyword"
      },
      "color": {
        "type": "keyword"
      },
      "price": {
        "type": "integer"
      }
    }
  }
}

PUT my_index_1104/_bulk
{"index":{"_id":1}}
{"brand":"brand_a","pt":"2021-01-01","name":"product_01","color":"red","price":600}
{"index":{"_id":2}}
{"brand":"brand_b","pt":"2021-02-01","name":"product_02","color":"red","price":200}
{"index":{"_id":3}}
{"brand":"brand_c","pt":"2021-03-01","name":"product_03","color":"green","price":300}
{"index":{"_id":4}}
{"brand":"brand_c","pt":"2021-02-01","name":"product_04","color":"green","price":450}
{"index":{"_id":5}}
{"brand":"brand_b","pt":"2021-04-01","name":"product_05","color":"blue","price":180}
{"index":{"_id":6}}
{"brand":"brand_b","pt":"2021-02-01","name":"product_06","color":"yellow","price":165}
{"index":{"_id":7}}
{"brand":"brand_b","pt":"2021-02-01","name":"product_07","color":"yellow","price":190}
{"index":{"_id":8}}
{"brand":"brand_c","pt":"2021-04-01","name":"product_08","color":"blue","price":500}
{"index":{"_id":9}}
{"brand":"brand_a","pt":"2021-01-01","name":"product_09","color":"blue","price":1000}
```

```
####多桶聚合示例
POST my_index_1104/_search
{
  "size": 0,
  "aggs": {
    "brands_and_colors_aggs": {
      "multi_terms": {
        "terms": [
          {
            "field": "brand"
          },
          {
            "field": "color"
          }
        ]
      }
    }
  }
}
```

### 11.2.4 Composite聚合的核心功能
```
####多桶聚合示例如下
POST my_index_1104/_search
{
  "size": 0,
  "aggs": {
    "my_buckets": {
      "composite": {
        "size": 5,
        "sources": [
          {
            "brand_terms": {
              "terms": {
                "field": "brand",
                "order": "asc"
              }
            }
          },
          {
            "prices_histogram": {
              "histogram": {
                "field": "price",
                "interval": 50,
                "order": "asc"
              }
            }
          }
        ],
        "after": {
          "brand_terms": "brand_c",
          "prices_histogram": 500
        }
      }
    }
  }
}
```

```
####总实现
GET my_index_1104/_search
{
  "size": 0,
  "aggs": {
    "my_buckets": {
      "composite": {
        "size": 5,
        "sources": [
          {
            "date": {
              "date_histogram": {
                "field": "pt",
                "calendar_interval": "1m",
                "order": "desc",
                "time_zone": "Asia/Shanghai"
              }
            }
          },
          {
            "product": {
              "terms": {
                "field": "brand"
              }
            }
          }
        ]
      },
      "aggregations": {
        "the_avg": {
          "avg": {
            "field": "price"
          }
        }
      }
    }
  }
}
```

```
####聚合后分页实现
POST my_index_1104/_search
{
  "size": 0,
  "aggs": {
    "my_buckets": {
      "composite": {
        "size": 5,
        "sources": [
          {
            "date": {
              "date_histogram": {
                "field": "pt",
                "calendar_interval": "1m",
                "order": "desc",
                "time_zone": "Asia/Shanghai"
              }
            }
          },
          {
            "product": {
              "terms": {
                "field": "brand"
              }
            }
          }
        ],
        "after": {
          "date": 1617235200000,
          "product": "brand_c"
        }
      },
      "aggregations": {
        "the_avg": {
          "avg": {
            "field": "price"
          }
        }
      }
    }
  }
}
```

## 11.3 如何通过子聚合求环比的上升比例

### 11.3.2 Pipeline子聚合详解
```
PUT my_index_1105
{
  "mappings": {
    "properties": {
      "insert_date": {
        "type": "date"
      },
      "count": {
        "type": "integer"
      }
    }
  }
}


POST my_index_1105/_bulk
{"index":{"_id":1}}
{"insert_date":"2022-11-09T12:00:00Z","count":5}
{"index":{"_id":2}}
{"insert_date":"2022-11-08T12:00:00Z","count":150}
{"index":{"_id":3}}
{"insert_date":"2022-12-09T12:00:00Z","count":33}
{"index":{"_id":4}}
{"insert_date":"2022-12-08T12:00:00Z","count":44}
{"index":{"_id":5}}
{"insert_date":"2022-12-09T12:00:00Z","count":55}
{"index":{"_id":6}}
{"insert_date":"2022-12-08T12:00:00Z","count":66}

POST my_index_1105/_search
{
  "size": 0,
  "aggs": {
    "sales_per_month": {--------------------------------外层聚合：按照月份统计
      "date_histogram": {
        "field": "insert_date",
        "calendar_interval": "month"
      },
      "aggs": {
        "sales": {--------------------------------------内层聚合：月份内求和
          "sum": {
            "field": "count"
          }
        }
      }
    },
    "max_monthly_sales": {
      "max_bucket": {
        "buckets_path": "sales_per_month > sales"--------获取销量最大值所在的桶（月份）
      }
    }
  }
```

```
####环比求解实现
POST my_index_1105/_search
{
  "size": 0,----------------------------------------------------不显示检索结果
  "aggs": {
    "range_aggs": {
      "range": {------------------------------------------------全量数据聚合
        "field": "insert_date",
        "format": "yyyy-MM-dd",
        "ranges": [
          {
            "from": "2022-11-01",
            "to": "2022-12-31"
          }
        ]
      },
      "aggs": {
        "11month_count": {--------------------------------------11月数据聚合
          "filter": {
            "range": {
              "insert_date": {
                "gte": "2022-11-01",
                "lte": "2022-11-30"
              }
            }
          },
          "aggs": {
            "sum_aggs": {
              "sum": {
                "field": "count"
              }
            }
          }
        },
        "12month_count": {-----------------------------------12月数据聚合
          "filter": {
            "range": {
              "insert_date": {
                "gte": "2022-12-01",
                "lte": "2022-12-31"
              }
            }
          },
          "aggs": {
            "sum_aggs": {
              "sum": {
                "field": "count"
              }
            }
          }
        },
        "bucket_division": {----------------------------------求解环比上升比例
          "bucket_script": {
            "buckets_path": {
              "pre_month_count": "11month_count > sum_aggs",
              "cur_month_count": "12month_count > sum_aggs"
            },
            "script": "(params.cur_month_count - params.pre_month_count) / params.pre_month_count"
          }
        }
      }
    }
  }
}
```

## 11.4 Elasticsearch如何去重

```
####批量写入数据
PUT my_index_1106/_bulk
{"index":{"_id":10}}
{"brand":"brand_a","pt":"2021-01-01","name":"product_01","color":"red","price":600}
{"index":{"_id":11}}
{"brand":"brand_b","pt":"2021-02-01","name":"product_02","color":"red","price":200}
```

```
POST my_index_1106/_search
{
  "size": 0,
  "aggs": {
    "brand_count": {
      "cardinality": {
        "field": "brand"
      }
    }
  }
}
```

#### 方式一：top_hits聚合间接实现去重。

```
####top_hits子聚合
POST my_index_1106/_search
{
  "size": 0,
  "query": {
    "match_all": {}
  },
  "aggs": {
    "aggs_by_brand": {
      "terms": {
        "field": "brand",
        "size": 10
      },
      "aggs": {
        "pt_tops": {
          "top_hits": {
            "_source": {
              "includes": [
                "brand",
                "name",
                "color"
              ]
            },
            "sort": [
              {
                "pt": {
                  "order": "desc"
                }
              }
            ],
            "size": 1
          }
        }
      }
    }
  }
}
```

#### 方式二：通过折叠实现去重。
```
####折叠去重实现
POST my_index_1106/_search
{
  "query": {
    "match_all": {}
  },
  "collapse": {
    "field": "brand",
    "inner_hits": {
      "name": "by_color",
      "collapse": {
        "field": "color"
      },
      "size": 5
    }
  }
}
```