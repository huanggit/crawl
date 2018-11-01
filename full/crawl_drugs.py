#coding:utf-8

from scrapy.selector import Selector
from math import ceil
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

root_url = 'http://drugs.medlive.cn/'
info_left = '//div[contains(@class, "info-left")]'

req_count = 0
session = requests.Session()

converter = html2text.HTML2Text()
converter.ignore_links = True


def _req(url, path=None):
    global req_count
    req_count += 1
    time.sleep(65 if (req_count % 12 == 0) else 1)
    html = session.get(root_url + url, cookies=coockie)
    selector = Selector(text=html.content)
    if path is None:
        return selector
    return selector.xpath(path)


def drug_list_pages():
    all_classes_urls = _req('drugref/drugCateIndex.do', '//div[contains(@class, "table2")]//a/@href').extract()
    all_classes_urls = set(all_classes_urls)
    with open('drug_page.txt', 'r', 'utf-8') as f:
        for line in f:
            all_classes_urls.remove(line.split()[0])
    with open('drug_page.txt', 'a', 'utf-8') as w:
        for inx, class_url in enumerate(all_classes_urls):
            page_res = _req(class_url, '//b[contains(@class, "blue")]/text()').extract_first()
            drug_num = int(page_res.strip())
            page_num = ceil(drug_num/10)
            w.write('{} {}\n'.format(class_url, page_num))

    def g():
        with open('drug_page.txt', 'r', 'utf-8') as f:
            for l in f:
                yield l
    with open('web_pages.txt', 'w', 'utf-8') as w:
        for line in g():
            url, page_num = line.split()
            for page in range(1, int(page_num) + 1):
                w.write('{}&page={}\n'.format(url, page))


def drug_detail_pages():
    list_page_urls = set()
    with open('web_pages.txt', 'r', 'utf-8') as f:
        for line in f:
            list_page_urls.add(line.strip())
    with open('web_pages_done.txt', 'r', 'utf-8') as f:
        for line in f:
            list_page_urls.remove(line.strip())
    with open('web_urls.txt', 'a', 'utf-8') as w:
        with open('web_pages_done.txt', 'a', 'utf-8') as wd:
            for list_page_url in list_page_urls:
                drugs_list = _req(list_page_url, '//div[contains(@class, "box-list")]//a/@href').extract()
                for drug_page in drugs_list:
                    w.write(drug_page+'\n')
                wd.write(list_page_url+'\n')


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
    d[u'所属类别'] = d[u'所属类别'].split('  >> ')
    return d


def crawl_drug():
    def gen_drugs():
        drug_page_urls = set()
        with open('drug_urls.txt', 'r', 'utf-8') as f:
            for line in f:
                drug_page_urls.add(line.strip())
        with open('drug_urls_done.txt', 'r', 'utf-8') as f:
            for line in f:
                drug_page_urls.remove(line.strip())
        for drug_page in drug_page_urls:
            drug_info = _req(drug_page)
            drug = parse_drug(drug_info)
            yield drug_page, json.dumps(drug, ensure_ascii=False)

    with open('drug_info.json', 'a', 'utf-8') as w:
        with open('drug_urls_done.txt', 'a', 'utf-8') as wd:
            for drug_page, drug in gen_drugs():
                w.write('{}\n'.format(drug))
                wd.write('{}\n'.format(drug_page))


if __name__ == '__main__':
    crawl_drug()





