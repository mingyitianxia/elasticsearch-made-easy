## 14.1 监控Elasticsearch集群的十个核心监控指标
### 14.1.1 五类核心监控维度
```
GET _cluster/health
```

```
POST my_index/_forcemerge
```

```
GET /_cat/nodes?v&h=id,disk.total,disk.used,disk.avail,disk.used_percent,ram.current,ram.percent,ram.max,cpu
id   disk.total disk.used disk.avail disk.used_percent ram.current ram.percent ram.max cpu
```

```
GET _cat/indices?v&health=red
GET _cat/indices?v&health=yellow
GET _cat/indices?v&health=green
```
```
GET /_cluster/allocation/explain
{
  "index": "my_index_003",
  "shard": 0,
  "primary": false
}
```

```
PUT my_index_003/_settings
{
  "index": {
    "number_of_replicas": 0
  }
}
```

```
POST /_cluster/reroute
{
  "commands": [
    {
      "move": {
        "index": "test", "shard": 0,
        "from_node": "node1", "to_node": "node2"
      }
    },
    {
      "allocate_replica": {
        "index": "test", "shard": 1,
        "node": "node3"
      }
    }
  ]
}
```

## 14.3 实战中运维及故障诊断的常用命令
```
PUT /_cluster/settings 
{
  "transient": {
     "cluster.routing.allocation.exclude._ip": "122.5.3.55"
   }
}
```

```
POST /_flush
```

```
PUT /_cluster/settings
{
   "transient": {
     "cluster.routing.allocation.cluster_concurrent_rebalance": 2
   }
 }
```

```
PUT /_cluster/settings
{
  "transient": {
     "cluster.routing.allocation.node_concurrent_recoveries": 6
   }
}
```
```
 PUT /_cluster/settings
 {
   "transient": {
    "indices.recovery.max_bytes_per_sec": "80mb"
  }
}

POST /_cache/clear


PUT /_cluster/settings
{
  "persistent": {
    "indices.breaker.total.limit": "40%"
  }
}

POST _reindex
{
  "source": {
    "index": "my-index-000001"
  },
  "dest": {
    "index": "my-new-index-000001"
  }
}

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
 
 POST /_snapshot/my_backup/snapshot_hamlet_index/_restore
 
 
```

## 14.4 Elasticsearch监控指标可视化

```
# Module: elasticsearch
# Docs: https://www.elastic.co/guide/en/beats/metricbeat/master/metricbeat-module-elasticsearch.html
- module: elasticsearch
  xpack.enabled: true
  period: 10s
  hosts: ["https://172.21.0.14:9200"]
  username: "elastic"
  password: "changeme"
  ssl.enabled: true
  ssl.certificate_authorities: ["/www/singo_node/elasticsearch-8.1.0/config/certs/http_ca.crt"]
```

```
./elasticsearch-reset-password --username elastic -i
```
```
# ---------------------------- Elasticsearch Output ----------------------------
output.elasticsearch:
  # Array of hosts to connect to.
  hosts: ["172.21.0.14:9200"]

  # Protocol - either `http` (default) or `https`.
  protocol: "https"

  # Authentication credentials - either API key or username/password.
  username: "elastic"
  password: "changeme"

  ssl.verification_mode: none


# =================================== Kibana ===================================

# Starting with Beats version 6.0.0, the dashboards are loaded via the Kibana API.
# This requires a Kibana endpoint configuration.
setup.kibana:

  # Kibana Host
  # Scheme and port can be left out and will be set to the default (http and 5601)
  # In case you specify and additional path, the scheme is required: http://localhost:5601/path
  # IPv6 addresses should always be defined as: https://[2001:db8::1]:5601
  host: "http://172.21.0.14:5601"
  username: "elastic"
  password: "changeme"
```

```
./metricbeat modules enable mysql
```

```
./metricbeat setup -e

./metricbeat -e


nohup ./metricbeat & > /dev/null 2>&1
```

## 14.5 Elasticsearch日志能否打印全部请求

```
PUT /_cluster/settings
{
  "persistent": {
    "logger.org.elasticsearch.discovery": "DEBUG"
  }
}

logger.org.elasticsearch.discovery: DEBUG


logger.discovery.name = org.elasticsearch.discovery
logger.discovery.level = debug
```

```
PUT /my-index-000001/_settings
{
  "index.search.slowlog.threshold.query.warn": "10s",
  "index.search.slowlog.threshold.query.info": "5s",
  "index.search.slowlog.threshold.query.debug": "2s",
  "index.search.slowlog.threshold.query.trace": "500ms",
  "index.search.slowlog.threshold.fetch.warn": "1s",
  "index.search.slowlog.threshold.fetch.info": "800ms",
  "index.search.slowlog.threshold.fetch.debug": "500ms",
  "index.search.slowlog.threshold.fetch.trace": "200ms"
}

PUT packets-2022-12-14/_settings
{
  "index.indexing.slowlog.threshold.index.debug": "0s",
  "index.search.slowlog.threshold.fetch.debug": "0s",
  "index.search.slowlog.threshold.query.debug": "0s"
}


```
