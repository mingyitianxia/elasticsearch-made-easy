
## 18.2 知识库检索系统的技术选型

### 18.2.3 Ingest Attachment：文件处理器插件

```
sudo bin/elasticsearch-plugin install ingest-attachment
```

## 18.4 知识库检索系统的实现

### 18.4.1 FSCrawler使用步骤详解

```
name: "gupao_fs"
fs:
  url: "/www/mingyi_file_search_system/fscrawler-es7-2.9/filesystem"
  update_rate: "1m"
  excludes:
  - "*/~*"
  json_support: false
  filename_as_id: false
  add_filesize: true
  remove_deleted: true
  add_as_inner_object: false
  store_source: false
  index_content: true
  attributes_support: false
  raw_metadata: false
  xml_support: false
  index_folders: true
  lang_detect: false
  continue_on_error: false
  ocr:
    language: "eng"
    enabled: true
    pdf_strategy: "ocr_and_text"
  follow_symlinks: false
elasticsearch:
  nodes:
  - url: "http://172.20.0.14:29190"
  bulk_size: 100
  flush_interval: "5s"
  byte_size: "10mb"
  ssl_verification: true
  username: elastic
  password: changeme

```

```
./bin/fscrawler my_crawler_settings.yaml

## 1.初始化
bin/fscrawler --config_dir ./test_03 gupao_fs
创建配置文件

## 2.启动
bin/fscrawler --config_dir ./test_03 gupao_fs

## 3.重启
bin/fscrawler --config_dir ./test_03 gupao_fs restart

## 4.rest方式启动
bin/fscrawler --config_dir ./test gupao_fs --loop 0 --rest
如果端口冲突，记得先配置一下端口。

## 5.rest方式启动+上传文件
echo "This is my text" > test.txt
curl -F "file=@test.txt" "http://127.0.0.1:8080/fscrawler/_upload"
```

- Python 工程代码详见：Chapter18_MingyiFSSearch.zip