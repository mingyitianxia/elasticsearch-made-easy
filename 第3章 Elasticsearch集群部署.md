# 第3章 Elasticsearch集群部署

## 3.1 ElasticStack 集群部署先验知识

### 3.1.5 Elasticsearch集群核心配置解读

```
vim /etc/profile
ulimit -n 65535
source /etc/profile
```

```
* soft nofile 65536
* hard nofile 65536
```

```
ulimit -a
```

```
sysctl -w vm.max_map_count=262144
```

```
[root@4ad config]# tail -f /etc/sysctl.conf
vm.max_map_count=262144
```

## 3.3 Elasticsearch单节点与Kibana自定义证书部署

### 3.3.1 Elasticsearch 自定义证书部署

首先，生成或创建认证中心。
```
./bin/elasticsearch-certutil ca
```
其次，生成TLS加密通信的证书。
```
./bin/elasticsearch-certutil cert --ca elastic-stack-ca.p12
```
然后，修改elasticsearch.yml的安全配置。设置集群名称（按照业务需求来）、设置节点名称（按照业务需求来）、设置TLS安全加密，参考如下。
```
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate 
xpack.security.transport.ssl.client_authentication: required
xpack.security.transport.ssl.keystore.path: elastic-certificates.p12
xpack.security.transport.ssl.truststore.path: elastic-certificates.p12
```

最后，将密码存储在密钥库。如果你在创建节点证书时输入了密码，请运行以下命令将密码存储在Elasticsearch密钥库中。
```
./bin/elasticsearch-keystore add xpack.security.transport.ssl.keystore.secure_password
./bin/elasticsearch-keystore add xpack.security.transport.ssl.truststore.secure_password
```

生成HTTP的证书。
```
./bin/elasticsearch-certutil http
```

将密码存储在密钥库。
```
./bin/elasticsearch-keystore add xpack.security.http.ssl.keystore.secure_password
```

