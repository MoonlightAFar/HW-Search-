from elasticsearch import Elasticsearch
from interest import get_interest

index_name = 'music'
# 正确配置 URL 格式并更新 timeout 参数
es = Elasticsearch(
    hosts=["http://localhost:9200"],  # 需要包含协议部分 http:// 或 https://
    request_timeout=3600  # 使用 request_timeout 替代 timeout
)

host_counts = get_interest()
data = []


# 连接到 Elasticsearch 实例

def sort_by_host_count(document):
    link = document.get('link')  # 获取文档中的链接
    for host, count in host_counts.items():
        if host in link:
            return count
    return 0


# 短语查询
def select(search_term):
    page_size = 10
    # 构建查询
    query2 = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "title": search_term
                        }
                    },
                    {
                        "match_phrase": {
                            "text": search_term
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {
                "text": {
                    "number_of_fragments": 2,
                    "fragment_size": 30,
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                }
            }
        }
    }

    query3 = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match_phrase": {
                            "title": search_term
                        }
                    },
                    {
                        "match_phrase": {
                            "text": search_term
                        }
                    }
                ]
            }
        }
    }

    # 执行查询
    result = es.search(index=index_name, body=query2)
    print(type(result))
    count_results = es.count(index=index_name, body=query3)
    total_count = count_results['count']

    for hit in result['hits']['hits']:
        hit['_score'] = sort_by_host_count(hit['_source'])
    sorted_result = sorted(result['hits']['hits'], key=lambda x: x['_score'], reverse=True)

    return sorted_result, total_count


# 站内搜索
def select2(search_term, dns):
    query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "link": dns
                        }
                    }
                ],
                "should": [
                    {
                        "match_phrase": {
                            "title": search_term
                        }
                    },
                    {
                        "match_phrase": {
                            "text": search_term
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "highlight": {
            "fields": {
                "text": {
                    "number_of_fragments": 2,
                    "fragment_size": 30,
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                }
            }
        }
    }

    query1 = {
        "query": {
            "bool": {
                "must": [
                    {
                        "match_phrase": {
                            "link": dns
                        }
                    }
                ],
                "should": [
                    {
                        "match_phrase": {
                            "title": search_term
                        }
                    },
                    {
                        "match_phrase": {
                            "text": search_term
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
    }

    res = es.search(index=index_name, body=query)
    count_results = es.count(index=index_name, body=query1)
    total_count = count_results['count']
    return res, total_count


# 通配搜索
def select3(search_term):
    query = {
        "query": {
            "bool": {
                "should": [
                    {
                        "wildcard": {
                            "text": {
                                "value": search_term
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "title": {
                                "value": search_term
                            }
                        }
                    }
                ]
            }
        },
        "highlight": {
            "fields": {
                "text": {
                    "number_of_fragments": 2,
                    "fragment_size": 30,
                    "pre_tags": ["<strong>"],
                    "post_tags": ["</strong>"]
                }
            }
        }
    }

    query1 = {
        "query": {
            "bool": {
                "should": [
                    {
                        "wildcard": {
                            "text": {
                                "value": search_term
                            }
                        }
                    },
                    {
                        "wildcard": {
                            "title": {
                                "value": search_term
                            }
                        }
                    }
                ]
            }
        }
    }

    res = es.search(index=index_name, body=query)
    count_results = es.count(index=index_name, body=query1)
    total_count = count_results['count']
    return res, total_count
