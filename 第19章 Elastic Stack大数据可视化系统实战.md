# 0、相关地址

## 0.1官方文档

https://www.elastic.co/guide/en/elasticsearch/reference/7.13/index.html

## 0.2 长津湖地址
https://maoyan.com/films/257706
https://m.maoyan.com/mmdb/comments/movie/257706.json

# 1、数据建模 Mapping
```
PUT cjh_movie_index
{
   "settings": {
    "index": {
      "default_pipeline": "auto_process"
    }
  },
  "mappings": {
    "properties": {
      "comment_id": {
        "type": "keyword"
      },
      "approve": {
        "type": "long"
      },
      "reply": {
        "type": "long"
      },
      "comment_time": {
        "type": "date",
        "format": " yyyy-M-d H:m || yyyy-M-dd H:m || yyyy-M-dd H:mm || yyyy-M-d HH:mm || yyyy-M-dd HH:mm ||yyyy-MM-dd HH:mm || yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      },
      "sureViewed": {
        "type": "keyword"
      },
      "nickName": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "gender": {
        "type": "keyword"
      },
      "cityName": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "userLevel": {
        "type": "keyword"
      },
      "user_id": {
        "type": "keyword"
      },
      "score": {
        "type": "keyword"
      },
      "score_level": {
        "type": "integer",
        "fields": {
          "keyword":{
            "type":"keyword"
          }
        }
      },
      "director": {
        "type": "keyword"
      },
      "starring":{
        "type":"keyword"
      },
      "content": {
        "type": "text",
        "analyzer": "ik_max_word",
        "fields": {
          "smart": {
              "type": "text",
        "analyzer": "ik_smart",
        "fielddata": true
          },
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "location": {
        "type": "geo_point"
      }
    }
  }
}
```

# 2、数据预处理（部分）

## 2.1 打tag

### 2.1.1 _simulate模拟打tag实现

```
POST _ingest/pipeline/_simulate
{
  "pipeline": {
    "processors": [
      {
        "script": {
          "description": "Extract 'tags' from 'env' field",
          "lang": "painless",
          "source": """if(ctx.content.contains('易烊千玺') | ctx.content.contains('易烊') | ctx.content.contains('千玺')){
              ctx.starring.add('易烊千玺')
           }"""
        }
      }
    ]
  },
  "docs": [
    {
      "_source": {
        "comment_id": 1,
        "content": "易烊千玺真棒，吴京也好厉害！钢七连最厉害！",
        "score": "4.5",
        "cityName": "北京",
        "starring": []
      }
    }
  ]
}

```

### 2.1.2 模拟打tag再验证（字段动态或静态）
```
DELETE my-index-102801
PUT my-index-102801
{
  "settings": {
    "index": {
      "default_pipeline": "addtags"
    }
  },
  "mappings": {
    "properties": {
      "content": {
        "type": "text"
      },
      "starring": {
        "type": "keyword"
      }
    }
  }
}

GET my-index-102801

POST my-index-102801/_doc
{
  "content": "易烊千玺真棒，吴京也好厉害！钢七连最厉害！",
  "score": "4.5",
  "cityName": "北京"
}

GET my-index-102801/_search
```

# 3、数据同步脚本

 ** 注意：数据已整理为 Chapter19_datas.zip，解压即可使用。 **

```
input {
  file {
    path => "/www/elasticsearch_0713/logstash-7.13.0/sync/*.csv"
    start_position => "beginning"
    sincedb_path => "/dev/null"
  }
}
filter {
  csv {
     separator => ","
      columns => ["comment_id","approve","reply","comment_time","sureViewed","nickName","gender","cityName","userLevel","user_id","score","content"]
        }
  mutate {
        remove_field =>["message"]
        }
}
output {
   elasticsearch {
     hosts => "https://172.21.0.14:9200"
     index => "cjh_movie_index"
	 user => "elastic"
     password => "psdlaoyang"
	 cacert => "/www/elasticsearch_0801_20220713/singo_node/elasticsearch-8.1.0/config/certs/http_ca.crt"
  }
stdout {}
}
```

# 4、可视化内容


### 4.1 打点可行性验证
```
(这一步极为重要)
PUT my-index-0000029
{
  "mappings": {
    "properties": {
      "location": {
        "type": "geo_point"
      }
    }
  }
}

POST my-index-0000029/_doc      
{
"date": "2021-10-29T20:00:00Z",
  "text": "Geopoint as an object",
  "location": "39.9299857781,116.395645038"
}

https://www.elastic.co/guide/en/elasticsearch/reference/current/geo-point.html
```
### 4.2 词云-前置tag 可行性验证
```
DELETE my-index-102802
PUT my-index-102802
{
  "mappings": {
    "properties": {
      "content":{
        "type":"text",
        "analyzer": "ik_smart",
        "fielddata": true
      }
    }
  }
}

PUT my-index-102802/_bulk
{"index":{"_id":1}}
{"content":"《长津湖》续集正式官宣,吴京、易烊千玺领衔主演"}
{"index":{"_id":2}}
{"content":"吴京、易烊千玺领衔,《长津湖之水门桥》入冬后全员再度集..."}
{"index":{"_id":3}}
{"content":"易烊千玺从不单独去机场,身边往往有两个人护送,三人各有各..."}
{"index":{"_id":4}}
{"content":"易烊千玺面对镜头时笑到癫狂,原来都是生蚝惹的祸! - 饭圈..."}

POST my-index-102802/_search
{
  "size": 0,
  "aggs": {
    "term_aggs": {
      "terms": {
        "field": "content"
      }
    }
  }
}
```


# 3、数据预处理全量

```
PUT _ingest/pipeline/auto_process
{
  "description": "add score level...",
  "processors": [
       {
      "script": {
        "lang": "painless",
        "source": """
       if(ctx.cityName=='上海'){ctx.location = "31.24916171,121.487899486"}
if(ctx.cityName=='临沧'){ctx.location = "23.8878061038,100.092612914"}
if(ctx.cityName=='丽江'){ctx.location = "26.8753510895,100.229628399"}
if(ctx.cityName=='保山'){ctx.location = "25.1204891962,99.1779956133"}
if(ctx.cityName=='大理白族自治州'){ctx.location = "25.5968996394,100.223674789"}
if(ctx.cityName=='德宏傣族景颇族自治州'){ctx.location = "24.441239663,98.5894342874"}
if(ctx.cityName=='怒江傈僳族自治州'){ctx.location = "25.8606769782,98.8599320425"}
if(ctx.cityName=='文山壮族苗族自治州'){ctx.location = "23.3740868504,104.246294318"}
if(ctx.cityName=='昆明'){ctx.location = "25.0491531005,102.714601139"}
if(ctx.cityName=='昭通'){ctx.location = "27.3406329636,103.725020656"}
if(ctx.cityName=='普洱'){ctx.location = "22.7887777801,100.98005773"}
if(ctx.cityName=='曲靖'){ctx.location = "25.5207581429,103.782538888"}
if(ctx.cityName=='楚雄彝族自治州'){ctx.location = "25.0663556742,101.529382239"}
if(ctx.cityName=='玉溪'){ctx.location = "24.3704471344,102.545067892"}
if(ctx.cityName=='红河哈尼族彝族自治州'){ctx.location = "23.3677175165,103.384064757"}
if(ctx.cityName=='西双版纳傣族自治州'){ctx.location = "22.0094330022,100.803038275"}
if(ctx.cityName=='迪庆藏族自治州'){ctx.location = "27.8310294612,99.7136815989"}
if(ctx.cityName=='乌兰察布'){ctx.location = "41.0223629468,113.112846391"}
if(ctx.cityName=='乌海'){ctx.location = "39.6831770068,106.831999097"}
if(ctx.cityName=='兴安盟'){ctx.location = "46.0837570652,122.048166514"}
if(ctx.cityName=='包头'){ctx.location = "40.6471194257,109.846238532"}
if(ctx.cityName=='呼伦贝尔'){ctx.location = "49.2016360546,119.760821794"}
if(ctx.cityName=='呼和浩特'){ctx.location = "40.8283188731,111.66035052"}
if(ctx.cityName=='巴彦淖尔'){ctx.location = "40.7691799024,107.42380672"}
if(ctx.cityName=='赤峰'){ctx.location = "42.2971123203,118.930761192"}
if(ctx.cityName=='通辽'){ctx.location = "43.633756073,122.260363263"}
if(ctx.cityName=='鄂尔多斯'){ctx.location = "39.8164895606,109.993706251"}
if(ctx.cityName=='锡林郭勒盟'){ctx.location = "43.9397048423,116.027339689"}
if(ctx.cityName=='阿拉善盟'){ctx.location = "38.8430752644,105.695682871"}
if(ctx.cityName=='北京'){ctx.location = "39.9299857781,116.395645038"}
if(ctx.cityName=='台中'){ctx.location = "26.0911937119,119.337634104"}
if(ctx.cityName=='台北'){ctx.location = "22.3748329286,114.130474436"}
if(ctx.cityName=='台南'){ctx.location = "38.9658447898,121.360525873"}
if(ctx.cityName=='嘉义'){ctx.location = "22.7288657203,114.246701335"}
if(ctx.cityName=='高雄'){ctx.location = "21.9464822541,111.590952812"}
if(ctx.cityName=='吉林'){ctx.location = "43.8719883344,126.564543989"}
if(ctx.cityName=='四平'){ctx.location = "43.1755247011,124.391382074"}
if(ctx.cityName=='延边朝鲜族自治州'){ctx.location = "42.8964136037,129.485901958"}
if(ctx.cityName=='松原'){ctx.location = "45.1360489701,124.832994532"}
if(ctx.cityName=='白城'){ctx.location = "45.6210862752,122.840776679"}
if(ctx.cityName=='白山'){ctx.location = "41.945859397,126.435797675"}
if(ctx.cityName=='辽源'){ctx.location = "42.9233026191,125.133686052"}
if(ctx.cityName=='通化'){ctx.location = "41.7363971299,125.942650139"}
if(ctx.cityName=='长春'){ctx.location = "43.8983376071,125.313642427"}
if(ctx.cityName=='乐山'){ctx.location = "29.6009576111,103.760824239"}
if(ctx.cityName=='内江'){ctx.location = "29.5994615348,105.073055992"}
if(ctx.cityName=='凉山彝族自治州'){ctx.location = "27.8923929037,102.259590803"}
if(ctx.cityName=='南充'){ctx.location = "30.8009651682,106.105553984"}
if(ctx.cityName=='宜宾'){ctx.location = "28.7696747963,104.633019062"}
if(ctx.cityName=='巴中'){ctx.location = "31.8691891592,106.757915842"}
if(ctx.cityName=='广元'){ctx.location = "32.4410401584,105.81968694"}
if(ctx.cityName=='广安'){ctx.location = "30.4639838879,106.635720331"}
if(ctx.cityName=='德阳'){ctx.location = "31.1311396527,104.402397818"}
if(ctx.cityName=='成都'){ctx.location = "30.6799428454,104.067923463"}
if(ctx.cityName=='攀枝花'){ctx.location = "26.5875712571,101.722423152"}
if(ctx.cityName=='泸州'){ctx.location = "28.8959298039,105.443970289"}
if(ctx.cityName=='甘孜藏族自治州'){ctx.location = "30.0551441144,101.969232063"}
if(ctx.cityName=='眉山'){ctx.location = "30.0611150799,103.841429563"}
if(ctx.cityName=='绵阳'){ctx.location = "31.5047012581,104.705518975"}
if(ctx.cityName=='自贡'){ctx.location = "29.3591568895,104.776071339"}
if(ctx.cityName=='资阳'){ctx.location = "30.132191434,104.635930302"}
if(ctx.cityName=='达州'){ctx.location = "31.2141988589,107.494973447"}
if(ctx.cityName=='遂宁'){ctx.location = "30.5574913504,105.564887792"}
if(ctx.cityName=='阿坝藏族羌族自治州'){ctx.location = "31.9057628583,102.228564689"}
if(ctx.cityName=='雅安'){ctx.location = "29.9997163371,103.009356466"}
if(ctx.cityName=='天津'){ctx.location = "39.1439299033,117.210813092"}
if(ctx.cityName=='中卫'){ctx.location = "37.5211241916,105.196754199"}
if(ctx.cityName=='吴忠'){ctx.location = "37.9935610029,106.208254199"}
if(ctx.cityName=='固原'){ctx.location = "36.0215234807,106.285267996"}
if(ctx.cityName=='石嘴山'){ctx.location = "39.0202232836,106.379337202"}
if(ctx.cityName=='银川'){ctx.location = "38.5026210119,106.206478608"}
if(ctx.cityName=='亳州'){ctx.location = "33.8712105653,115.787928245"}
if(ctx.cityName=='六安'){ctx.location = "31.7555583552,116.505252683"}
if(ctx.cityName=='合肥'){ctx.location = "31.8669422607,117.282699092"}
if(ctx.cityName=='安庆'){ctx.location = "30.5378978174,117.058738772"}
if(ctx.cityName=='宣城'){ctx.location = "30.9516423543,118.752096311"}
if(ctx.cityName=='宿州'){ctx.location = "33.6367723858,116.988692412"}
if(ctx.cityName=='池州'){ctx.location = "30.6600192482,117.494476772"}
if(ctx.cityName=='淮北'){ctx.location = "33.9600233054,116.791447429"}
if(ctx.cityName=='淮南'){ctx.location = "32.6428118237,117.018638863"}
if(ctx.cityName=='滁州'){ctx.location = "32.3173505954,118.324570351"}
if(ctx.cityName=='芜湖'){ctx.location = "31.3660197875,118.384108423"}
if(ctx.cityName=='蚌埠'){ctx.location = "32.9294989067,117.357079866"}
if(ctx.cityName=='铜陵'){ctx.location = "30.9409296947,117.819428729"}
if(ctx.cityName=='阜阳'){ctx.location = "32.9012113306,115.820932259"}
if(ctx.cityName=='马鞍山'){ctx.location = "31.6885281589,118.515881847"}
if(ctx.cityName=='黄山'){ctx.location = "29.7344348562,118.293569632"}
if(ctx.cityName=='东营'){ctx.location = "37.4871211553,118.583926333"}
if(ctx.cityName=='临沂'){ctx.location = "35.0724090744,118.340768237"}
if(ctx.cityName=='威海'){ctx.location = "37.5287870813,122.093958366"}
if(ctx.cityName=='德州'){ctx.location = "37.4608259263,116.328161364"}
if(ctx.cityName=='日照'){ctx.location = "35.4202251931,119.507179943"}
if(ctx.cityName=='枣庄'){ctx.location = "34.8078830784,117.279305383"}
if(ctx.cityName=='泰安'){ctx.location = "36.1880777589,117.089414917"}
if(ctx.cityName=='济南'){ctx.location = "36.6827847272,117.024967066"}
if(ctx.cityName=='济宁'){ctx.location = "35.4021216643,116.600797625"}
if(ctx.cityName=='淄博'){ctx.location = "36.8046848542,118.059134278"}
if(ctx.cityName=='滨州'){ctx.location = "37.4053139418,117.968292415"}
if(ctx.cityName=='潍坊'){ctx.location = "36.7161148731,119.142633823"}
if(ctx.cityName=='烟台'){ctx.location = "37.5365615629,121.30955503"}
if(ctx.cityName=='聊城'){ctx.location = "36.4558285147,115.986869139"}
if(ctx.cityName=='莱芜'){ctx.location = "36.2336541336,117.684666912"}
if(ctx.cityName=='菏泽'){ctx.location = "35.2624404961,115.463359775"}
if(ctx.cityName=='青岛'){ctx.location = "36.1052149013,120.384428184"}
if(ctx.cityName=='临汾'){ctx.location = "36.0997454436,111.538787596"}
if(ctx.cityName=='吕梁'){ctx.location = "37.527316097,111.143156602"}
if(ctx.cityName=='大同'){ctx.location = "40.1137444997,113.290508673"}
if(ctx.cityName=='太原'){ctx.location = "37.890277054,112.550863589"}
if(ctx.cityName=='忻州'){ctx.location = "38.461030573,112.727938829"}
if(ctx.cityName=='晋中'){ctx.location = "37.6933615268,112.7385144"}
if(ctx.cityName=='晋城'){ctx.location = "35.4998344672,112.867332758"}
if(ctx.cityName=='朔州'){ctx.location = "39.3376719662,112.479927727"}
if(ctx.cityName=='运城'){ctx.location = "35.0388594798,111.006853653"}
if(ctx.cityName=='长治'){ctx.location = "36.2016643857,113.120292086"}
if(ctx.cityName=='阳泉'){ctx.location = "37.8695294932,113.569237602"}
if(ctx.cityName=='东莞'){ctx.location = "23.0430238154,113.763433991"}
if(ctx.cityName=='中山'){ctx.location = "22.5451775145,113.422060021"}
if(ctx.cityName=='云浮'){ctx.location = "22.9379756855,112.050945959"}
if(ctx.cityName=='佛山'){ctx.location = "23.0350948405,113.134025635"}
if(ctx.cityName=='广州'){ctx.location = "23.1200491021,113.307649675"}
if(ctx.cityName=='惠州'){ctx.location = "23.1135398524,114.41065808"}
if(ctx.cityName=='揭阳'){ctx.location = "23.5479994669,116.379500855"}
if(ctx.cityName=='梅州'){ctx.location = "24.304570606,116.126403098"}
if(ctx.cityName=='汕头'){ctx.location = "23.3839084533,116.728650288"}
if(ctx.cityName=='汕尾'){ctx.location = "22.7787305002,115.372924289"}
if(ctx.cityName=='江门'){ctx.location = "22.5751167835,113.078125341"}
if(ctx.cityName=='河源'){ctx.location = "23.7572508505,114.713721476"}
if(ctx.cityName=='深圳'){ctx.location = "22.5460535462,114.025973657"}
if(ctx.cityName=='清远'){ctx.location = "23.6984685504,113.040773349"}
if(ctx.cityName=='湛江'){ctx.location = "21.2574631038,110.365067263"}
if(ctx.cityName=='潮州'){ctx.location = "23.6618116765,116.630075991"}
if(ctx.cityName=='珠海'){ctx.location = "22.2569146461,113.562447026"}
if(ctx.cityName=='肇庆'){ctx.location = "23.0786632829,112.47965337"}
if(ctx.cityName=='茂名'){ctx.location = "21.6682257188,110.931245331"}
if(ctx.cityName=='阳江'){ctx.location = "21.8715173045,111.977009756"}
if(ctx.cityName=='韶关'){ctx.location = "24.8029603119,113.594461107"}
if(ctx.cityName=='北海'){ctx.location = "21.472718235,109.122627919"}
if(ctx.cityName=='南宁'){ctx.location = "22.8064929356,108.297233556"}
if(ctx.cityName=='崇左'){ctx.location = "22.4154552965,107.357322038"}
if(ctx.cityName=='来宾'){ctx.location = "23.7411659265,109.231816505"}
if(ctx.cityName=='柳州'){ctx.location = "24.3290533525,109.42240181"}
if(ctx.cityName=='桂林'){ctx.location = "25.262901246,110.260920147"}
if(ctx.cityName=='梧州'){ctx.location = "23.4853946367,111.30547195"}
if(ctx.cityName=='河池'){ctx.location = "24.6995207829,108.069947709"}
if(ctx.cityName=='玉林'){ctx.location = "22.6439736084,110.151676316"}
if(ctx.cityName=='百色'){ctx.location = "23.9015123679,106.631821404"}
if(ctx.cityName=='贵港'){ctx.location = "23.1033731644,109.613707557"}
if(ctx.cityName=='贺州'){ctx.location = "24.4110535471,111.552594179"}
if(ctx.cityName=='钦州'){ctx.location = "21.9733504653,108.638798056"}
if(ctx.cityName=='防城港'){ctx.location = "21.6173984705,108.351791153"}
if(ctx.cityName=='乌鲁木齐'){ctx.location = "43.8403803472,87.5649877411"}
if(ctx.cityName=='伊犁哈萨克自治州'){ctx.location = "43.9222480963,81.2978535304"}
if(ctx.cityName=='克孜勒苏柯尔克孜自治州'){ctx.location = "39.7503455778,76.1375644775"}
if(ctx.cityName=='克拉玛依'){ctx.location = "45.5943310667,84.8811801861"}
if(ctx.cityName=='博尔塔拉蒙古自治州'){ctx.location = "44.9136513743,82.0524362672"}
if(ctx.cityName=='吐鲁番地区'){ctx.location = "42.9604700169,89.1815948657"}
if(ctx.cityName=='和田地区'){ctx.location = "37.1167744927,79.9302386372"}
if(ctx.cityName=='哈密地区'){ctx.location = "42.8585963324,93.5283550928"}
if(ctx.cityName=='喀什地区'){ctx.location = "39.4706271887,75.9929732675"}
if(ctx.cityName=='塔城地区'){ctx.location = "46.7586836297,82.9748805837"}
if(ctx.cityName=='昌吉回族自治州'){ctx.location = "44.0070578985,87.2960381257"}
if(ctx.cityName=='自治区直辖'){ctx.location = "42.1270009576,85.6148993383"}
if(ctx.cityName=='阿克苏地区'){ctx.location = "41.1717309015,80.2698461793"}
if(ctx.cityName=='阿勒泰地区'){ctx.location = "47.8397444862,88.1379154871"}
if(ctx.cityName=='南京'){ctx.location = "32.0572355018,118.778074408"}
if(ctx.cityName=='南通'){ctx.location = "32.0146645408,120.873800951"}
if(ctx.cityName=='宿迁'){ctx.location = "33.9520497337,118.296893379"}
if(ctx.cityName=='常州'){ctx.location = "31.7713967447,119.981861013"}
if(ctx.cityName=='徐州'){ctx.location = "34.2715534311,117.188106623"}
if(ctx.cityName=='扬州'){ctx.location = "32.4085052546,119.427777551"}
if(ctx.cityName=='无锡'){ctx.location = "31.5700374519,120.305455901"}
if(ctx.cityName=='泰州'){ctx.location = "32.4760532748,119.919606016"}
if(ctx.cityName=='淮安'){ctx.location = "33.6065127393,119.030186365"}
if(ctx.cityName=='盐城'){ctx.location = "33.3798618771,120.148871818"}
if(ctx.cityName=='苏州'){ctx.location = "31.317987368,120.619907115"}
if(ctx.cityName=='连云港'){ctx.location = "34.601548967,119.173872217"}
if(ctx.cityName=='镇江'){ctx.location = "32.2044094436,119.455835405"}
if(ctx.cityName=='上饶'){ctx.location = "28.4576225539,117.955463877"}
if(ctx.cityName=='九江'){ctx.location = "29.7196395261,115.999848022"}
if(ctx.cityName=='南昌'){ctx.location = "28.6895780001,115.893527546"}
if(ctx.cityName=='吉安'){ctx.location = "27.1138476502,114.992038711"}
if(ctx.cityName=='宜春'){ctx.location = "27.8111298958,114.400038672"}
if(ctx.cityName=='抚州'){ctx.location = "27.9545451703,116.360918867"}
if(ctx.cityName=='新余'){ctx.location = "27.8223215586,114.947117417"}
if(ctx.cityName=='景德镇'){ctx.location = "29.3035627684,117.186522625"}
if(ctx.cityName=='萍乡'){ctx.location = "27.639544223,113.859917033"}
if(ctx.cityName=='赣州'){ctx.location = "25.8452955363,114.935909079"}
if(ctx.cityName=='鹰潭'){ctx.location = "28.2413095972,117.035450186"}
if(ctx.cityName=='保定'){ctx.location = "38.886564548,115.494810169"}
if(ctx.cityName=='唐山'){ctx.location = "39.6505309225,118.183450598"}
if(ctx.cityName=='廊坊'){ctx.location = "39.5186106251,116.703602223"}
if(ctx.cityName=='张家口'){ctx.location = "40.8111884911,114.89378153"}
if(ctx.cityName=='承德'){ctx.location = "40.9925210525,117.933822456"}
if(ctx.cityName=='沧州'){ctx.location = "38.2976153503,116.863806476"}
if(ctx.cityName=='石家庄'){ctx.location = "38.0489583146,114.522081844"}
if(ctx.cityName=='秦皇岛'){ctx.location = "39.9454615659,119.604367616"}
if(ctx.cityName=='衡水'){ctx.location = "37.7469290459,115.686228653"}
if(ctx.cityName=='邢台'){ctx.location = "37.0695311969,114.520486813"}
if(ctx.cityName=='邯郸'){ctx.location = "36.6093079285,114.482693932"}
if(ctx.cityName=='三门峡'){ctx.location = "34.7833199411,111.181262093"}
if(ctx.cityName=='信阳'){ctx.location = "32.1285823075,114.085490993"}
if(ctx.cityName=='南阳'){ctx.location = "33.0114195691,112.542841901"}
if(ctx.cityName=='周口'){ctx.location = "33.6237408181,114.654101942"}
if(ctx.cityName=='商丘'){ctx.location = "34.4385886402,115.641885688"}
if(ctx.cityName=='安阳'){ctx.location = "36.1102667222,114.351806508"}
if(ctx.cityName=='平顶山'){ctx.location = "33.7453014565,113.300848978"}
if(ctx.cityName=='开封'){ctx.location = "34.8018541758,114.351642118"}
if(ctx.cityName=='新乡'){ctx.location = "35.3072575577,113.912690161"}
if(ctx.cityName=='洛阳'){ctx.location = "34.6573678177,112.447524769"}
if(ctx.cityName=='漯河'){ctx.location = "33.5762786885,114.0460614"}
if(ctx.cityName=='濮阳'){ctx.location = "35.7532978882,115.026627441"}
if(ctx.cityName=='焦作'){ctx.location = "35.234607555,113.211835885"}
if(ctx.cityName=='省直辖'){ctx.location = "31.2093162501,112.410562192"}
if(ctx.cityName=='许昌'){ctx.location = "34.0267395887,113.83531246"}
if(ctx.cityName=='郑州'){ctx.location = "34.7566100641,113.64964385"}
if(ctx.cityName=='驻马店'){ctx.location = "32.9831581541,114.049153547"}
if(ctx.cityName=='鹤壁'){ctx.location = "35.7554258742,114.297769838"}
if(ctx.cityName=='丽水'){ctx.location = "28.4562995521,119.929575843"}
if(ctx.cityName=='台州'){ctx.location = "28.6682832857,121.440612936"}
if(ctx.cityName=='嘉兴'){ctx.location = "30.7739922396,120.760427699"}
if(ctx.cityName=='宁波'){ctx.location = "29.8852589659,121.579005973"}
if(ctx.cityName=='杭州'){ctx.location = "30.2592444615,120.219375416"}
if(ctx.cityName=='温州'){ctx.location = "28.002837594,120.690634734"}
if(ctx.cityName=='湖州'){ctx.location = "30.8779251557,120.137243163"}
if(ctx.cityName=='绍兴'){ctx.location = "30.0023645805,120.592467386"}
if(ctx.cityName=='舟山'){ctx.location = "30.0360103026,122.169872098"}
if(ctx.cityName=='衢州'){ctx.location = "28.9569104475,118.875841652"}
if(ctx.cityName=='金华'){ctx.location = "29.1028991054,119.652575704"}
if(ctx.cityName=='三亚'){ctx.location = "18.2577759149,109.522771281"}
if(ctx.cityName=='三沙'){ctx.location = "16.840062894,112.350383075"}
if(ctx.cityName=='海口'){ctx.location = "20.022071277,110.330801848"}
if(ctx.cityName=='十堰'){ctx.location = "32.6369943395,110.801228917"}
if(ctx.cityName=='咸宁'){ctx.location = "29.8806567577,114.300060592"}
if(ctx.cityName=='孝感'){ctx.location = "30.9279547842,113.935734392"}
if(ctx.cityName=='宜昌'){ctx.location = "30.732757818,111.310981092"}
if(ctx.cityName=='恩施土家族苗族自治州'){ctx.location = "30.2858883166,109.491923304"}
if(ctx.cityName=='武汉'){ctx.location = "30.5810841269,114.316200103"}
if(ctx.cityName=='荆州'){ctx.location = "30.332590523,112.241865807"}
if(ctx.cityName=='荆门'){ctx.location = "31.0426112029,112.217330299"}
if(ctx.cityName=='襄阳'){ctx.location = "32.2291685915,112.250092848"}
if(ctx.cityName=='鄂州'){ctx.location = "30.3844393228,114.895594041"}
if(ctx.cityName=='随州'){ctx.location = "31.7178576082,113.379358364"}
if(ctx.cityName=='黄冈'){ctx.location = "30.4461089379,114.906618047"}
if(ctx.cityName=='黄石'){ctx.location = "30.2161271277,115.050683164"}
if(ctx.cityName=='娄底'){ctx.location = "27.7410733023,111.996396357"}
if(ctx.cityName=='岳阳'){ctx.location = "29.3780070755,113.146195519"}
if(ctx.cityName=='常德'){ctx.location = "29.0121488552,111.653718137"}
if(ctx.cityName=='张家界'){ctx.location = "29.1248893532,110.481620157"}
if(ctx.cityName=='怀化'){ctx.location = "27.5574829012,109.986958796"}
if(ctx.cityName=='株洲'){ctx.location = "27.8274329277,113.131695341"}
if(ctx.cityName=='永州'){ctx.location = "26.4359716468,111.614647686"}
if(ctx.cityName=='湘潭'){ctx.location = "27.835095053,112.935555633"}
if(ctx.cityName=='湘西土家族苗族自治州'){ctx.location = "28.3179507937,109.7457458"}
if(ctx.cityName=='益阳'){ctx.location = "28.5880877799,112.366546645"}
if(ctx.cityName=='衡阳'){ctx.location = "26.8981644154,112.583818811"}
if(ctx.cityName=='邵阳'){ctx.location = "27.2368112449,111.461525404"}
if(ctx.cityName=='郴州'){ctx.location = "25.7822639757,113.037704468"}
if(ctx.cityName=='长沙'){ctx.location = "28.2134782309,112.979352788"}
if(ctx.cityName=='无堂区划分区域'){ctx.location = "22.2041179884,113.557519102"}
if(ctx.cityName=='澳门半岛'){ctx.location = "22.1950041592,113.566432335"}
if(ctx.cityName=='澳门离岛'){ctx.location = "22.2041179884,113.557519102"}
if(ctx.cityName=='临夏回族自治州'){ctx.location = "35.5985143488,103.215249178"}
if(ctx.cityName=='兰州'){ctx.location = "36.064225525,103.823305441"}
if(ctx.cityName=='嘉峪关'){ctx.location = "39.8023973267,98.2816345853"}
if(ctx.cityName=='天水'){ctx.location = "34.5843194189,105.736931623"}
if(ctx.cityName=='定西'){ctx.location = "35.5860562418,104.626637601"}
if(ctx.cityName=='平凉'){ctx.location = "35.55011019,106.688911157"}
if(ctx.cityName=='庆阳'){ctx.location = "35.7268007545,107.644227087"}
if(ctx.cityName=='张掖'){ctx.location = "38.939320297,100.459891869"}
if(ctx.cityName=='武威'){ctx.location = "37.9331721429,102.640147343"}
if(ctx.cityName=='甘南藏族自治州'){ctx.location = "34.9922111784,102.917442486"}
if(ctx.cityName=='白银'){ctx.location = "36.5466817062,104.171240904"}
if(ctx.cityName=='酒泉'){ctx.location = "39.7414737682,98.5084145062"}
if(ctx.cityName=='金昌'){ctx.location = "38.5160717995,102.208126263"}
if(ctx.cityName=='陇南'){ctx.location = "33.3944799729,104.934573406"}
if(ctx.cityName=='三明'){ctx.location = "26.2708352794,117.642193934"}
if(ctx.cityName=='南平'){ctx.location = "26.6436264742,118.181882949"}
if(ctx.cityName=='厦门'){ctx.location = "24.4892306125,118.103886046"}
if(ctx.cityName=='宁德'){ctx.location = "26.6565274192,119.54208215"}
if(ctx.cityName=='泉州'){ctx.location = "24.901652384,118.600362343"}
if(ctx.cityName=='漳州'){ctx.location = "24.5170647798,117.676204679"}
if(ctx.cityName=='福州'){ctx.location = "26.0471254966,119.330221107"}
if(ctx.cityName=='莆田'){ctx.location = "25.4484501367,119.077730964"}
if(ctx.cityName=='龙岩'){ctx.location = "25.0786854335,117.017996739"}
if(ctx.cityName=='山南地区'){ctx.location = "29.2290269317,91.7506438744"}
if(ctx.cityName=='拉萨'){ctx.location = "29.6625570621,91.111890896"}
if(ctx.cityName=='日喀则地区'){ctx.location = "29.2690232039,88.8914855677"}
if(ctx.cityName=='昌都地区'){ctx.location = "31.1405756319,97.18558158"}
if(ctx.cityName=='林芝地区'){ctx.location = "29.6669406258,94.3499854582"}
if(ctx.cityName=='那曲地区'){ctx.location = "31.4806798301,92.0670183689"}
if(ctx.cityName=='阿里地区'){ctx.location = "30.4045565883,81.1076686895"}
if(ctx.cityName=='六盘水'){ctx.location = "26.5918660603,104.85208676"}
if(ctx.cityName=='安顺'){ctx.location = "26.2285945777,105.928269966"}
if(ctx.cityName=='毕节'){ctx.location = "27.4085621313,105.333323371"}
if(ctx.cityName=='贵阳'){ctx.location = "26.6299067414,106.709177096"}
if(ctx.cityName=='遵义'){ctx.location = "27.6999613771,106.931260316"}
if(ctx.cityName=='铜仁'){ctx.location = "27.6749026906,109.168558028"}
if(ctx.cityName=='黔东南苗族侗族自治州'){ctx.location = "26.5839917665,107.985352573"}
if(ctx.cityName=='黔南布依族苗族自治州'){ctx.location = "26.2645359974,107.52320511"}
if(ctx.cityName=='黔西南布依族苗族自治州'){ctx.location = "25.0951480559,104.900557798"}
if(ctx.cityName=='丹东'){ctx.location = "40.1290228266,124.338543115"}
if(ctx.cityName=='大连'){ctx.location = "38.9487099383,121.593477781"}
if(ctx.cityName=='抚顺'){ctx.location = "41.8773038296,123.929819767"}
if(ctx.cityName=='朝阳'){ctx.location = "41.5718276679,120.446162703"}
if(ctx.cityName=='本溪'){ctx.location = "41.3258376266,123.77806237"}
if(ctx.cityName=='沈阳'){ctx.location = "41.8086447835,123.432790922"}
if(ctx.cityName=='盘锦'){ctx.location = "41.141248023,122.07322781"}
if(ctx.cityName=='营口'){ctx.location = "40.6686510665,122.233391371"}
if(ctx.cityName=='葫芦岛'){ctx.location = "40.7430298813,120.860757645"}
if(ctx.cityName=='辽阳'){ctx.location = "41.2733392656,123.172451205"}
if(ctx.cityName=='铁岭'){ctx.location = "42.2997570121,123.854849615"}
if(ctx.cityName=='锦州'){ctx.location = "41.1308788759,121.147748738"}
if(ctx.cityName=='阜新'){ctx.location = "42.0192501071,121.660822129"}
if(ctx.cityName=='鞍山'){ctx.location = "41.1187436822,123.007763329"}
if(ctx.cityName=='重庆'){ctx.location = "29.5446061089,106.530635013"}
if(ctx.cityName=='咸阳'){ctx.location = "34.345372996,108.707509278"}
if(ctx.cityName=='商洛'){ctx.location = "33.8739073951,109.934208154"}
if(ctx.cityName=='安康'){ctx.location = "32.70437045,109.038044563"}
if(ctx.cityName=='宝鸡'){ctx.location = "34.3640808097,107.170645452"}
if(ctx.cityName=='延安'){ctx.location = "36.6033203523,109.500509757"}
if(ctx.cityName=='榆林'){ctx.location = "38.2794392401,109.745925744"}
if(ctx.cityName=='汉中'){ctx.location = "33.0815689782,107.045477629"}
if(ctx.cityName=='渭南'){ctx.location = "34.5023579758,109.483932697"}
if(ctx.cityName=='西安'){ctx.location = "34.2777998978,108.953098279"}
if(ctx.cityName=='铜川'){ctx.location = "34.9083676964,108.968067013"}
if(ctx.cityName=='果洛藏族自治州'){ctx.location = "34.4804845846,100.223722769"}
if(ctx.cityName=='海东地区'){ctx.location = "36.5176101677,102.085206987"}
if(ctx.cityName=='海北藏族自治州'){ctx.location = "36.9606541011,100.879802174"}
if(ctx.cityName=='海南藏族自治州'){ctx.location = "36.2843638038,100.624066094"}
if(ctx.cityName=='海西蒙古族藏族自治州'){ctx.location = "37.3737990706,97.3426254153"}
if(ctx.cityName=='玉树藏族自治州'){ctx.location = "33.0062399097,97.0133161374"}
if(ctx.cityName=='西宁'){ctx.location = "36.640738612,101.76792099"}
if(ctx.cityName=='黄南藏族自治州'){ctx.location = "35.5228515517,102.007600308"}
if(ctx.cityName=='九龙'){ctx.location = "22.3072458588,114.173291988"}
if(ctx.cityName=='新界'){ctx.location = "22.4274312754,114.146701965"}
if(ctx.cityName=='香港岛'){ctx.location = "22.2721034276,114.183870524"}
if(ctx.cityName=='七台河'){ctx.location = "45.7750053686,131.019048047"}
if(ctx.cityName=='伊春'){ctx.location = "47.7346850751,128.910765978"}
if(ctx.cityName=='佳木斯'){ctx.location = "46.8137796047,130.284734586"}
if(ctx.cityName=='双鸭山'){ctx.location = "46.6551020625,131.17140174"}
if(ctx.cityName=='哈尔滨'){ctx.location = "45.7732246332,126.657716855"}
if(ctx.cityName=='大兴安岭地区'){ctx.location = "51.991788968,124.19610419"}
if(ctx.cityName=='大庆'){ctx.location = "46.59670902,125.02183973"}
if(ctx.cityName=='牡丹江'){ctx.location = "44.5885211528,129.608035396"}
if(ctx.cityName=='绥化'){ctx.location = "46.646063927,126.989094572"}
if(ctx.cityName=='鸡西'){ctx.location = "45.3215398866,130.941767273"}
if(ctx.cityName=='鹤岗'){ctx.location = "47.3386659037,130.292472051"}
if(ctx.cityName=='黑河'){ctx.location = "50.2506900907,127.500830295"}
if(ctx.cityName=='齐齐哈尔'){ctx.location = "47.3476998134,123.987288942"}
  """
      }
    },
    {
      "fingerprint": {
        "fields": [
          "comment_id"
        ]
      }
    },
    {
      "append": {
        "field": "starring",
        "value": []
      }
    },
    {
      "append": {
        "field": "director",
        "value": []
      }
    },
    {
      "script": {
        "lang": "painless",
        "source": """
         if(ctx.score == "0.0"){
              ctx.score_level = 0
           }
           if(ctx.score == "0.5"){
              ctx.score_level = 0
           }
           if(ctx.score == "1.0"){
              ctx.score_level = 1
           }
           if(ctx.score == "1.5"){
              ctx.score_level = 1
           }
           if(ctx.score == "2.0"){
              ctx.score_level = 2
           }
           if(ctx.score == "2.5"){
              ctx.score_level = 2
           }
           if(ctx.score == "3.0"){
              ctx.score_level = 3
           }
           if(ctx.score == "3.5"){
              ctx.score_level = 3
           }
           if(ctx.score == "4.0"){
              ctx.score_level = 4
           }
            if(ctx.score == "4.5"){
              ctx.score_level = 4
           }
            if(ctx.score == "5.0"){
              ctx.score_level = 5
           }
          
          
           """
      }
    },

    {
      "script": {
        "lang": "painless",
        "source": """
           if(ctx.content.contains('陈凯歌') | ctx.content.contains('凯歌导演') | ctx.content.contains('陈导')){
              ctx.director.add('陈凯歌')
           }
           if(ctx.content.contains('徐克') | ctx.content.contains('徐导')){
              ctx.director.add('徐克')
           }
          if(ctx.content.contains('林超贤') | ctx.content.contains('林导')){
              ctx.director.add('林超贤')
           }
"""
      }
    },
    {
      "script": {
        "lang": "painless",
        "source": """
           if(ctx.content.contains('吴京')){
              ctx.starring.add('吴京')
           }
            if(ctx.content.contains('伍千里')){
              ctx.starring.add('伍千里')
           }
            if(ctx.content.contains('伍万里')){
              ctx.starring.add('伍万里')
           }
           if(ctx.content.contains('易烊千玺') | ctx.content.contains('易烊') | ctx.content.contains('千玺')){
              ctx.starring.add('易烊千玺')
           }
          if(ctx.content.contains('段奕宏') ){
              ctx.starring.add('段奕宏')
           }
            if( ctx.content.contains('谈子为')){
              ctx.starring.add('谈子为')
           }
           
            if(ctx.content.contains('朱亚文')){
              ctx.starring.add('朱亚文')
           }
             if(ctx.content.contains('梅生')){
              ctx.starring.add('梅生')
           }
           if(ctx.content.contains('李晨')){
              ctx.starring.add('李晨')
           }
            if(ctx.content.contains('余从戎')){
              ctx.starring.add('余从戎')
           }
            if(ctx.content.contains('胡军') ){
              ctx.starring.add('胡军')
           }
             if(ctx.content.contains('雷公') | ctx.content.contains('雷爸') | ctx.content.contains('雷爹')){
              ctx.starring.add('雷公')
           }
            if(ctx.content.contains('韩东君')){
              ctx.starring.add('韩东君')
           }
             if(ctx.content.contains('平河') ){
              ctx.starring.add('平河')
           }
            if(ctx.content.contains('张涵予')){
              ctx.starring.add('张涵予')
           }
              if(ctx.content.contains('宋时轮')){
              ctx.starring.add('宋时轮')
           }
            if(ctx.content.contains('欧豪')){
              ctx.starring.add('欧豪')
           }
            if(ctx.content.contains('黄轩')| ctx.content.contains('毛岸英')){
              ctx.starring.add('黄轩')
           }
"""
      }
    }
  ]
}
```