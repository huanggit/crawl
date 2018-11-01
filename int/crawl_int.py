# coding:utf-8

import requests
from pyquery import PyQuery as pq
from codecs import open
import time
import simplejson as json

coockie = {"Hm_lvt_62d92d99f7c1e7a31a11759de376479f": "1522303518",
           "ymtinfo": "eyJ1aWQiOiIwIiwicmVzb3VyY2UiOiIiLCJhcHBfbmFtZSI6IiIsImV4dF92ZXJzaW9uIjoiMSJ9",
           "ymt_pk_id": "6a62bc20473c8f02",
           "sensorsdata2015jssdkcross": "%7B%22distinct_id%22%3A%22162f1784bd95aa-0ad205a7f10e36-336c7b04-1296000-162f1784bda5f2%22%2C%22%24device_id%22%3A%22162f1784bd95aa-0ad205a7f10e36-336c7b04-1296000-162f1784bda5f2%22%7D",
           "sess": "5oggtcbifmpiairf3fqu0j32e2",
           "JSESSIONID": "D57FBA0BD88A4726EB906000954C1449",
           "_pk_ses.3.a971": "*",
           "_pk_id.3.a971": "6a62bc20473c8f02.1522303518.19.1524723109.1524714424.",
           "Hm_lpvt_62d92d99f7c1e7a31a11759de376479f": "1524723109",
           }
req_count = 0


def exists_ids():
    with open('ids.txt', 'r', 'utf-8') as f:
        for l in f:
            x = l.split(',')
            return [int(a) for a in x]
eids = exists_ids()


def _req(drug_id, session):
    global req_count
    req_count += 1
    if req_count % 12 == 0:
        time.sleep(61)
    url = 'http://drugs.medlive.cn/drugref/html/{}.shtml'.format(drug_id)
    html = session.get(url, cookies=coockie)
    if html.status_code == 404:
        return None
    return pq(pq(html.content)('.info-left').html().replace('&#13;', ''))


def parse_drug(drug_info):
    def noneEmpty(s):
        return s is not None and len(s.strip()) > 0
    d = dict()
    divs = drug_info.children().items()
    for div in divs:
        title = div.find('.title').text()
        value = div.find('.more-infomation').text()
        if noneEmpty(title) and noneEmpty(value):
            title = title[:-1]
            if title != u'药品名称':
                d[title] = value
                continue
            for v in value.split('\n'):
                vv = v.split(' ', 1)
                tt = vv[0][1:5]
                nn = vv[1]
                d[tt] = nn
    return d


def start_id():
    with open('id.txt', 'r', 'utf-8') as f:
        for l in f:
            return int(l)


def get_drug(session, drug_id):
    if drug_id not in eids:
        return None
    drug_selector = _req(drug_id, session)
    if drug_selector is None:
        return None
    drug_info = parse_drug(drug_selector)
    drug_info['id'] = drug_id
    return json.dumps(drug_info, ensure_ascii=False)


def crawl_drug():
    session = requests.Session()
    for drugId in range(start_id(), 22500):
        try:
            drug = get_drug(session, drugId)
            with open('id.txt', 'w', 'utf-8') as wd:
                wd.write(str(drugId + 1))
            if drug is None:
                continue
            with open('drugs.json', 'a', 'utf-8') as w:
                w.write('{}\n'.format(drug))
            print(drugId)
        except Exception as e:
            print(e)
            time.sleep(301)
            session = requests.Session()


if __name__ == '__main__':
    crawl_drug()
