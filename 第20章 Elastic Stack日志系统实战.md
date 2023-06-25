
## 20.1 日志系统的需求分析

数据地址为：https://www.kaggle.com/datasets/shawon10/web-log-dataset?resource=download


## 20.2 日志系统的技术架构

```
#!/bin/bash
while read -r line; do
    modified_line=$(echo "$line" | sed 's/,GET/ +0800,GET/')
    modified_line=$(echo "$modified_line" | sed 's/,POST/ +0800,POST/')
    echo "$modified_line"
done < weblog.csv > weblog_update.csv
```

## 20.3 日志系统的设计

```
 date {
    match => ["timestamp", "ISO8601"]
  }
```

```
"%{TIMESTAMP_ISO8601:timestamp}"

TIMESTAMP_ISO8601  %{YEAR}-%{MONTHNUM}-%{MONTHDAY}[T ]%{HOUR}:?%{MINUTE}(?::?%{SECOND})?%{ISO8601_TIMEZONE}?

 %{YEAR}-%{MONTHNUM}-%{MONTHDAY}[T ]%{HOUR}:?%{MINUTE}(?::?%{SECOND})?%{ISO8601_TIMEZONE}?
```

## 20.4 日志系统的实现

### 20.4.1 Logstash数据处理

```
input {
file {
path => "/www/elasticsearch_0806/logstash-8.6.0/sync/weblog_update.csv"
start_position => "beginning"
}
}

filter {
grok {
match => { "message" => "%{IPORHOST:client_ip},\[%{HTTPDATE:timestamp},%{WORD:http_method} %{NOTSPACE:http_path} HTTP/%{NUMBER:http_version},%{INT:http_status_code}" }
}

date {
match => [ "timestamp", "dd/MMM/yyyy:HH:mm:ss Z" ]
target => "timestamp_new"
}
}

output {
elasticsearch {
hosts => ["https://172.20.0.14:9190"]
index => "my_log_index"
user => "elastic"
password => "changeme"
cacert => "/www/elasticsearch_0806/elasticsearch-8.6.0/config/certs/http_ca.crt"
}
stdout { codec => rubydebug }
}
```

### 20.4.2数据同步到Elasticsearch

```
./bin/logstash -f ./config/logs.conf
```