from flask import Flask, render_template, request
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import os
from flask import send_from_directory
import ssl
# coding=utf-8
import math
from ssl import create_default_context
from elasticsearch import Elasticsearch

import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 客户端初始化
def client_init():
    context = create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    ES_HOST = "https://127.0.0.1:9200"
    ES_USER = "elastic"
    ES_PASSWORD = "changeme"

    es = Elasticsearch( hosts=ES_HOST,
                        basic_auth=(ES_USER, ES_PASSWORD),
                        verify_certs=False,
                        ca_certs='conf/http_ca.crt' )
    print( es )
    return es

__all__ = ['pybyte']


def pybyte(size, dot=2):
    size = float( size )
    # 位 比特 bit
    if 0 <= size < 1:
        human_size = str( round( size / 0.125, dot ) ) + 'b'
    # 字节 字节 Byte
    elif 1 <= size < 1024:
        human_size = str( round( size, dot ) ) + 'B'
    # 千字节 千字节 Kilo Byte
    elif math.pow( 1024, 1 ) <= size < math.pow( 1024, 2 ):
        human_size = str( round( size / math.pow( 1024, 1 ), dot ) ) + 'KB'
    # 兆字节 兆 Mega Byte
    elif math.pow( 1024, 2 ) <= size < math.pow( 1024, 3 ):
        human_size = str( round( size / math.pow( 1024, 2 ), dot ) ) + 'MB'
    # 吉字节 吉 Giga Byte
    elif math.pow( 1024, 3 ) <= size < math.pow( 1024, 4 ):
        human_size = str( round( size / math.pow( 1024, 3 ), dot ) ) + 'GB'
    # 太字节 太 Tera Byte
    elif math.pow( 1024, 4 ) <= size < math.pow( 1024, 5 ):
        human_size = str( round( size / math.pow( 1024, 4 ), dot ) ) + 'TB'
    # 拍字节 拍 Peta Byte
    elif math.pow( 1024, 5 ) <= size < math.pow( 1024, 6 ):
        human_size = str( round( size / math.pow( 1024, 5 ), dot ) ) + 'PB'
    # 艾字节 艾 Exa Byte
    elif math.pow( 1024, 6 ) <= size < math.pow( 1024, 7 ):
        human_size = str( round( size / math.pow( 1024, 6 ), dot ) ) + 'EB'
    # 泽它字节 泽 Zetta Byte
    elif math.pow( 1024, 7 ) <= size < math.pow( 1024, 8 ):
        human_size = str( round( size / math.pow( 1024, 7 ), dot ) ) + 'ZB'
    # 尧它字节 尧 Yotta Byte
    elif math.pow( 1024, 8 ) <= size < math.pow( 1024, 9 ):
        human_size = str( round( size / math.pow( 1024, 8 ), dot ) ) + 'YB'
    # 千亿亿亿字节 Bront Byte
    elif math.pow( 1024, 9 ) <= size < math.pow( 1024, 10 ):
        human_size = str( round( size / math.pow( 1024, 9 ), dot ) ) + 'BB'
    # 百万亿亿亿字节 Dogga Byte
    elif math.pow( 1024, 10 ) <= size < math.pow( 1024, 11 ):
        human_size = str( round( size / math.pow( 1024, 10 ), dot ) ) + 'NB'
    # 十亿亿亿亿字节 Dogga Byte
    elif math.pow( 1024, 11 ) <= size < math.pow( 1024, 12 ):
        human_size = str( round( size / math.pow( 1024, 11 ), dot ) ) + 'DB'
    # 万亿亿亿亿字节 Corydon Byte
    elif math.pow( 1024, 12 ) <= size:
        human_size = str( round( size / math.pow( 1024, 12 ), dot ) ) + 'CB'
    # 负数
    else:
        raise ValueError( '{}() takes number than or equal to 0, but less than 0 given.'.format( pybyte.__name__ ) )
    return human_size

def search_detail_info(doc_id):
    global es
    search_dsl = { "query": {"term": {"_id": doc_id}}, "_source": {
                    "includes": [
                      "file.filename",
                      "file.created",
                      "content"
                    ]
                  }}

    res = es.search( index='fs_job',
                     body=search_dsl )
    print( "body = ", search_dsl )
    return res

def search_common_pages(search_term):
    global es
    page = request.args.get( 'page' )
    ipage = int(page)
    size = 10
    start = (ipage - 1) * size
    es = client_init()
   #print(es)
    search_dsl = {"from": start, "size": size, "query": {"match_phrase": {"file.filename": search_term}},
                  "highlight": {"pre_tags": ["<font color=\"red\">"], "post_tags": ["</font>"],
                                "fields": {"file.filename": {}}}}
    #print(search_term)
    res = es.search( index='fs_job',
                     body=search_dsl )
    #print("res = ", res)

    #res['ST'] = search_term
    res.update( {"ST": search_term} )
    print( "body = ", search_dsl )

    #res['cur_page'] = ipage
    res.update( {"cur_page": ipage} )
    total_doc_counts = res['hits']['total']['value']

    remainder = total_doc_counts % size
    total_pages = 0
    if remainder >= 1 and remainder <= 9:
        total_pages = 1 + int( total_doc_counts / size )
    else:
        total_pages = int( total_doc_counts / size )
    #res['total_pages'] = total_pages
    res.update( {"total_pages": ipage} )
    print( "共分为" + str( res['total_pages'] ) + "页！" )

    for hit in res['hits']['hits']:
        hit['good_summary'] = '…'.join( hit['highlight']['file.filename'][1:] )
    # print(res)
    #icount = 0
    #return render_template( 'zw_result.html', res=res, pybyte=pybyte )
    return res

app = Flask(__name__)
@app.route('/')
def home():
    return render_template('./zw_index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
@app.route('/search/img/zw.jpg')
def logo():
    return send_from_directory(os.path.join(app.root_path, 'static'),'zw.jpg')

@app.route('/search/results', methods = ['GET', 'POST'])
def request_search():
    search_term = request.form["input"]
    res = search_common_pages(search_term)
    return render_template( 'zw_result.html', res=res, pybyte=pybyte )

@app.route('/search/pages', methods = ['GET', 'POST'])
def search_by_page():
    search_term = request.args.get( 'keyword' )
    res = search_common_pages( search_term)
    return render_template( 'zw_result.html', res=res, pybyte=pybyte )

@app.route('/search/detail', methods = ['GET', 'POST'])
def search_detail():
    doc_id = request.args.get( 'doc_id' )
    res = search_detail_info(doc_id)
    #print(res)
    return render_template( 'zw_detail.html', res=res, pybyte=pybyte )


if __name__ == '__main__':
     app.run('127.0.0.1', debug=True)
     es = client_init()