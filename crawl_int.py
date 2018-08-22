#coding:utf-8

from scrapy.selector import Selector
from codecs import open
import requests
import time
import html2text
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

info_left = '//div[contains(@class, "info-left")]'

req_count = 0
session = requests.Session()

converter = html2text.HTML2Text()
converter.ignore_links = True


def _req(drug_id):
    global req_count
    req_count += 1
    time.sleep(65 if (req_count % 12 == 0) else 1)
    html = session.get('http://drugs.medlive.cn/drugref/html/{}.shtml'.format(drug_id), cookies=coockie)
    if html.status_code == 404:
        return None
    return Selector(text=html.content)


def parse_drug(drug_info):
    def _drug_names(drug_inf):
        titles = drug_inf.xpath(info_left + '/div[2]/div[2]/p/label/text()').extract()
        names = drug_inf.xpath(info_left + '/div[2]/div[2]/p/text()').extract()
        for title, name in zip(titles, names):
            yield title.strip()[1:-1], name.strip()

    def _drug_attr(drug_inf):
        titles = drug_inf.xpath(info_left + '/div[position()>2]/div[1]/a/text()').extract()
        texts = drug_inf.xpath(info_left + '/div[position()>2]/div[2]/p').extract()
        for title, text in zip(titles, texts):
            yield title.strip()[:-1], converter.handle(text).strip()
    d = dict()
    for k, v in _drug_names(drug_info):
        d[k] = v
    for k, v in _drug_attr(drug_info):
        d[k] = v
    if d.get(u'所属类别') is not None:
        d[u'所属类别'] = d[u'所属类别'].split('  >> ')
    return d


def start_id():
    with open('id.txt', 'r', 'utf-8') as f:
        for l in f:
            return int(l)


def crawl_drug():
    def gen_drugs():
        for drug_id in range(start_id(), 0, -1):
            drug_selector = _req(drug_id)
            if drug_selector is None:
                continue
            drug_info = parse_drug(drug_selector)
            drug_info['id'] = drug_id
            yield drug_id, json.dumps(drug_info, ensure_ascii=False)
    cid = start_id()
    try:
        for drugId, drug in gen_drugs():
            with open('drugs.json', 'a', 'utf-8') as w:
                w.write('{}\n'.format(drug))
            with open('id.txt', 'w', 'utf-8') as wd:
                wd.write(str(drugId-1))
    finally:
        print(cid)


if __name__ == '__main__':
    crawl_drug()





