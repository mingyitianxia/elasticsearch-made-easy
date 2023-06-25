## 12.1 冷热集群架构

### 12.1.4冷热集群架构实战

```
####热节点路由设置
PUT logs_2025-01-01
{
  "settings": {
    "index.routing.allocation.include._tier_preference": "data_hot",
    "number_of_replicas": 0
  }
}
####温节点路由设置，索引名称仅作为举例用
PUT logs_2025-11-01
{
  "settings": {
     "index.routing.allocation.include._tier_preference": "data_cold",
    "number_of_replicas": 0
  }
}
```

```
####通过模板指定节点角色
PUT _index_template/logs_2025-06-template
{
  "index_patterns": "logs_2025-06-*",
  "template": {
    "settings": {
      "index.number_of_replicas": "0",
      "index.routing.allocation.include._tier_preference": "data_warm"
    }
  }
}
```

## 12.2 ILM：索引生命周期管理

### 12.2.4 索引生命周期管理的前提

```
####1.创建基于日期的索引
PUT my-index-20250709-000001
{
  "aliases": {
    "my-alias": {
      "is_write_index": true
    }
  }
}
 
####2.批量导入数据
PUT my-alias/_bulk
{"index":{"_id":1}}
{"title":"testing 01"}
{"index":{"_id":2}}
{"title":"testing 02"}
{"index":{"_id":3}}
{"title":"testing 03"}
{"index":{"_id":4}}
{"title":"testing 04"}
{"index":{"_id":5}}
{"title":"testing 05"}
```

```
GET /_cat/indices?v&s=pri.store.size:desc
```

```
GET /_cat/shards?v=true&s=store:desc
```

```

# 3、rollover 滚动索引

POST my-alias/_rollover
{
  "conditions": {
    "max_age": "7d",
    "max_docs": 5,
    "max_primary_shard_size": "50gb"
  }
}
GET my-alias/_count

# 4、在满足滚动条件的前提下滚动索引
PUT my-alias/_bulk
{"index":{"_id":6}}
{"title":"testing 06"}

# 5、检索数据，验证滚动是否生效
GET my-alias/_search
```

- shrink 操作
```
####步骤1：设置待压缩的索引，分片设置为5个。
DELETE kibana_sample_data_logs_ext
PUT kibana_sample_data_logs_ext
{
  "settings": {
    "number_of_shards":5
  }
}
#### 以Kibana系统自带的数据构建演示索引数据
POST _reindex
{
  "source":{
    "index":"kibana_sample_data_logs"
  },
  "dest":{
    "index":"kibana_sample_data_logs_ext"
  }
}
# 步骤2：满足shrink压缩之前的3个必要条件
PUT kibana_sample_data_logs_ext/_settings
{
  "settings": {
    "index.number_of_replicas": 0,
    "index.routing.allocation.include._tier_preference": "data_hot", 
    "index.blocks.write": true                                    
  }
}
# 步骤3：实施压缩
POST kibana_sample_data_logs_ext/_shrink/kibana_sample_data_logs_shrink
{
  "settings": {
    "index.number_of_replicas": 0,
    "index.number_of_shards": 1, 
    "index.codec": "best_compression" 
  },
  "aliases": {
    "kibana_sample_data_logs_alias": {}
  }
}
```

### 12.2.6索引生命周期管理实战：DSL

```
# step1：演示刷新需要
PUT _cluster/settings
{
  "persistent": {
    "indices.lifecycle.poll_interval": "1s"
  }
}
 
# step2：出于测试需要，将每个阶段的生存时间调小了
PUT _ilm/policy/my_custom_policy_filter
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": {
            "max_age": "3d",
            "max_docs": 5,
            "max_size": "50gb"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "15s",
        "actions": {
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "30s",
        "actions": {
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "45s",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
 
# step3：创建模板，关联配置的ilm_policy
PUT _index_template/timeseries_template
{
  "index_patterns": ["timeseries-*"],                 
  "template": {
    "settings": {
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "index.lifecycle.name": "my_custom_policy_filter",      
      "index.lifecycle.rollover_alias": "timeseries",
      "index.routing.allocation.include._tier_preference": "data_hot"
    }
  }
}
 
# step4：创建起始索引，便于滚动
PUT timeseries-000001
{
  "aliases": {
    "timeseries": {
      "is_write_index": true
    }
  }
}
 
# step5：插入数据
PUT timeseries/_bulk
{"index":{"_id":1}}
{"title":"testing 01"}
{"index":{"_id":2}}
{"title":"testing 02"}
{"index":{"_id":3}}
{"title":"testing 03"}
{"index":{"_id":4}}
{"title":"testing 04"}
 
# step6：临界值
PUT timeseries/_bulk
{"index":{"_id":5}}
{"title":"testing 05"}
 
# 下一个索引数据写入
PUT timeseries/_bulk
{"index":{"_id":6}}
{"title":"testing 06"}
```

```
PUT time_base-000001
{
  "aliases": {
    "time_base_alias": {
      "is_write_index": true
    }
  }
}

 
# 插入数据
PUT time_base_alias/_bulk
{"index":{"_id":1}}
{"title":"testing 01"}
{"index":{"_id":2}}
{"title":"testing 02"}
{"index":{"_id":3}}
{"title":"testing 03"}
{"index":{"_id":4}}
{"title":"testing 04"}
 
# 临界值
PUT time_base_alias/_bulk
{"index":{"_id":5}}
{"title":"testing 05"}
 
# 下一个索引数据写入
PUT time_base_alias/_bulk
{"index":{"_id":6}}
{"title":"testing 06"}
```

## 12.3 跨机房、跨机架部署架构

### 12.3.3跨机房、跨机架部署架构实战

```
node.attr.rack_id: rack_01
node.attr.rack_id: rack_02
```

```
PUT _cluster/settings
{
  "persistent": {
    "cluster.routing.allocation.awareness.attributes": "rack_id",
    "cluster.routing.allocation.awareness.force.rack_id.values": "rack_01,rack_02"
  }
}
```

```
PUT test_001
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1
  }
}

GET _cat/shards/test_001?v&s=shard:asc
```

```
node.attr.rack_id: rack_01
PUT test_002
{
  "settings": {
    "number_of_shards": 5,
    "number_of_replicas": 1
  }
}
GET _cat/shards/test_002?v&s=shard:asc
```

## 12.4 集群、索引备份与恢复实战

```
path.repo: ["/www/elasticsearch/elasticsearch-8.3.0/backup"]

PUT /_snapshot/my_backup
{
  "type": "fs",
  "settings": {
    "location": "/www/elasticsearch/elasticsearch-8.3.0/backup"
  }
}

PUT hamlet_01
POST hamlet_01/_doc/1
{
  "title":"just testing"
}

PUT hamlet_02
POST hamlet_02/_doc/1
{
  "title":"just testing"
}

PUT /_snapshot/my_backup/snapshot_cluster?wait_for_completion=true

PUT /_snapshot/my_backup/snapshot_hamlet_index?wait_for_completion=true
{
  "indices": "hamlet_*",
  "ignore_unavailable": true,
  "include_global_state": false,
  "metadata": {
    "taken_by": "mingyi",
    "taken_because": "backup before upgrading"
  }
}

####缺省值为true，设置为false后，将支持“*”模糊操作
PUT /_cluster/settings
{
  "transient": {
    "action.destructive_requires_name" : false
  }
}

DELETE hamlet_*

POST /_snapshot/my_backup/snapshot_hamlet_index/_restore

```

```
- 3. 快照常见操作

#### 查看所有快照存储库
GET /_snapshot/_all

#### 查看快照状态
GET /_snapshot/my_backup/snapshot_hamlet_index/_status

#### 删除快照
DELETE /_snapshot/my_backup/snapshot_hamlet_index
```

### 12.4.5 elasticdump迁移

```
elasticdump \
  --input=http://192.168.1.1:9200/my_index \
  --output=http://192.168.3.2:9200/my_index \
  --type=analyzer
elasticdump \
  --input=http://192.168.1.1:9200/my_index \
  --output=http://192.168.3.2:9200/my_index \
  --type=settings
elasticdump \
  --input=http://192.168.1.1:9200/my_index \
  --output=http://192.168.3.2:9200/my_index \
  --type=mapping
  
  elasticdump \
  --input=http://192.168.1.1:9200/my_index \
  --output=http://192.168.3.2:9200/my_index \
  --type=data
```

## 12.5 SLM：快照生命周期管理

```
path.repo: ["/www/elasticsearch_0801/backup_0801"]

PUT _snapshot/mytx_backup
{
  "type": "fs",
  "settings": {
    "location": "/www/elasticsearch_0801/backup_0801"
  }
}

PUT _slm/policy/test-snapshots
{
  "schedule": "0 0/15 * * * ?",       
  "name": "<test-snap-{now/d}>", 
  "repository": "mytx_backup",    
  "config": {
    "indices": "*",                 
    "include_global_state": true    
  },
  "retention": {                    
    "expire_after": "30d",
    "min_count": 5,
    "max_count": 50
  }
}

GET _features

POST _slm/policy/test-snapshots/_execute


PUT _cluster/settings
{
  "persistent" : {
    "slm.retention_schedule" : "0 30 1 * * ?"
  }
}

POST _slm/_execute_retention

GET _snapshot/mytx_backup/*?verbose=false

DELETE .kibana-event-log-8.1.3-000001
POST _snapshot/mytx_backup/test-snap-2022.05.04-13d-_6dore-kc1x0-fdaiq/_restore
{
  "indices": ".kibana-event-log-8.1.3-000001"
}
```

```
- 1）监视任何当前正在运行的快照。
GET _snapshot/mytx_backup/_current

- 2）返回任何当前正在运行的快照的每个细节。
GET _snapshot/_status

- 3）查看全量SLM policy执行的历史。
GET _slm/stats

- 4）查看特定SLM policy执行的历史。
GET _slm/policy/test-snapshots

- 5）删除快照，命令如下。
DELETE _snapshot/mytx_backup/test-snap-2022.05.05-uhbwjyj8qwwhdxqvcgejbq
```

## 12.6 跨集群检索

```
PUT _cluster/settings
{
  "persistent": {
    "cluster": {
      "remote": {
        "cluster_one": {
          "seeds": [
            "172.21.0.14:9300"
          ]
        },
        "cluster_two": {
          "seeds": [
            "172.21.0.14:9302"
          ]
        }
      }
    }
  }
}
```

```
1）在集群1 cluster_one插入数据。
PUT twitter/_doc/1
{
  "user":"kimchy"
}
PUT twitter/_doc/2
{
  "user":"kimchy 01"
}

2）在集群2 cluster_two插入数据。
PUT twitter/_doc/1
{
  "user":"kimchy 02"
}

GET twitter/_search
{
  "query": {
    "match": {
      "user": "kimchy"
    }
  }
}

GET cluster_one:twitter,cluster_two:twitter/_search
{
  "query": {
    "match": {
      "user": "kimchy"
    }
  }
}
```