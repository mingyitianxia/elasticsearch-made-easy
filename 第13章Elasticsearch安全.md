## 13.1 集群安全基础

### 13.1.4 设置或重置账号和密码

```
 ./elasticsearch-8.1.0/bin/elasticsearch-reset-password -h
 
 ./elasticsearch-8.1.0/bin/elasticsearch-reset-password -i -u elastic
```

### 13.3.2 脚本类型细分
```
POST _scripts/sum_score_script
{
  "script": {
    "lang": "painless",
    "source": "ctx._source.total_score=ctx._source.math_score + ctx._source.english_score"
  }
}

POST my_test_scores/_update_by_query
{
  "script": {
    "id": "sum_score_script"
  },
  "query": {
    "match_all": {}
  }
}

GET my_test_scores/_search

POST my_test_scores/_update_by_query
{
  "script": {
    "lang": "painless",
    "source": "ctx._source.total_score=ctx._source.math_score + ctx._source.english_score"
  },
  "query": {
    "match_all": {}
  }
}

GET my_test_scores/_search

```

### 13.3.3 脚本分级限制

```
script.allowed_types: both
script.allowed_types: inline
script.allowed_types: none
script.allowed_contexts: none
script.allowed_contexts: score, update
```