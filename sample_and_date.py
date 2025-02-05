# -*- coding: utf-8 -*-
import datetime
import random
import re
import sys
import time
from urllib2 import Request, urlopen

import xlwt
from bs4 import BeautifulSoup
import pandas as pd  # 读取 Excel 文件
import httplib

httplib.HTTPConnection._http_vsn = 10
httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'
reload(sys)
sys.setdefaultencoding('utf-8')

urls = {
    'nfc': u'https://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s8059_9_1__1.html#showc',
    'test': u'https://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_m1673-s7075-s7318-s8059_1_1_0_1.html#showc',
    '2023': u'https://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s10086_1_1_0_1.html#showc'
}

# 已采集的手机型号
mobiles = []


def zol_spider(year):
    wb_name = '%s.xls' % year
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet("zol", cell_overwrite_ok=True)

    title_index = {  # 索引参数的列
        '机型': 0,
        '价格': 1,
        '上市日期': 2,

    }

    if len(title_index) != len(set(title_index)):
        raise ValueError('titles has duplicates.')

    for __column in title_index:
        sheet.write(0, title_index[__column], __column)
    wb.save(wb_name)

    rows = 1  # excel 行数索引
    detail_domain = "https://detail.zol.com.cn"
    head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    url = urls[year]
    req = Request(url, headers=head)
    response = urlopen(req)
    html = response.read().decode('gbk')
    # print html
    soup = BeautifulSoup(html, 'html.parser')
    total_page_area = soup.find('div', class_="page_total")  # 获取页面区域的信息
    __pages = re.findall(u"/(\d*) 页", total_page_area.text)  # 获取总页码

    if len(__pages) == 1:
        total_page = int(__pages[0])
        print "Total pages: %s" % total_page
    else:
        print 'get total pages failed.total %s' % len(__pages)
        sys.exit(-1)

    unknown_list = []

    for each_page in range(total_page):  # 遍历，开爬
        print "page: ", each_page + 1, "/", total_page
        per_url = url.replace('1.html', str(each_page + 1) + ".html")
        req = Request(per_url, headers=head)
        response = urlopen(req)
        html = response.read().decode('gbk')
        soup = BeautifulSoup(html, 'html.parser')
        result_frame = soup.find("ul", class_="result_list")  # 包含搜索信息的那个框架

        phones = result_frame.find_all("li")  # 匹配出单个手机的信息
        for phone_content in phones:
            try:
                phone_name = phone_content.find("dl", class_="pro_detail").find("a").text.split('（')[0]
                if mobiles.__contains__(phone_name) :
                    print phone_name + "已采集"
                    continue
                else:
                    print phone_name + "要采集"
                    mobiles.append(phone_name)
                    print mobiles

                phone_price = phone_content.find("div", class_="date_price").find("b", class_="price-type").text
                sheet.write(rows, title_index['机型'], phone_name)
                sheet.write(rows, title_index['价格'], phone_price)

            except:
                continue

            # details = phone_content.find_all("li")
            # for i in details:
            #     if u'屏幕尺寸' in str(i):
            #         sheet.write(rows, title_index['屏幕'], i["title"])
            #     elif u'CPU型号' in str(i):
            #         sheet.write(rows, title_index['CPU'], i["title"])
            #     elif u'CPU频率' in str(i):
            #         sheet.write(rows, title_index['主频'], i["title"])
            #     elif u'RAM容量' in str(i):
            #         sheet.write(rows, title_index['RAM'], i["title"])
            #     elif u'ROM容量' in str(i):
            #         sheet.write(rows, title_index['ROM'], i["title"])

            detail_url = phone_content.find("a", target="_blank")["href"]

            phone_detail_url = detail_domain + detail_url
            # print phone_detail_url
            req = Request(phone_detail_url, headers=head)
            response = urlopen(req)
            html = response.read().decode('gbk')
            soup = BeautifulSoup(html, 'html.parser')

            # 以下是获取详情表格的代码↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
            tds = soup.find('td', class_="hd", text=u'基本参数')  # 表格标题
            try:
                camera_area = tds.parent.parent  # 总表格
            except:
                print "can not get camera info: ", phone_detail_url
                rows += 1
                continue
            for tr in camera_area.find_all('tr'):
                try:
                    if tr.th.text == u'国内发布时间':
                        if tr.td.span.contents[0] != "":
                            sheet.write(rows, title_index['上市日期'], tr.td.span.contents[0])
                    if tr.th.text == u'国外发布时间':
                        if tr.td.span.contents[0] != "":
                            sheet.write(rows, title_index['上市日期'], tr.td.span.contents[0])
                    if tr.th.text == u'上市日期':
                        if tr.td.span.contents[0] != "" and not str(tr.td.span.contents[0]).__contains__("href"):
                            sheet.write(rows, title_index['上市日期'], tr.td.span.contents[0])
                        else:
                            sheet.write(rows, title_index['上市日期'], tr.td.span.contents[0].text.replace('>', ''))
                    else:
                        if tr.th.text not in unknown_list:
                            # print 'new parm: ', tr.th.text, phone_detail_url
                            unknown_list.append(tr.th.text)
                except:
                    pass  # 大表格外面的标题为none，会报错
            # 获取详情的代码结束↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

            wb.save(wb_name)
            rows += 1
            # sleep_time = random.randint(1, 3)  # 定义一个随机睡眠时间，防止被识别为爬虫，可能有点作用。
            # time.sleep(sleep_time) #太慢了


if __name__ == "__main__":
    excel = ""
    data1 = pd.read_excel( open('old.xlsx','r'),  dtype=str, index_col=False, encoding='utf8', engine='xlrd')
    for item in data1.values:
        mobiles.append(str(item[0]))
    print mobiles

    s = datetime.datetime.now().strftime('%y%m%d')
    if len(sys.argv) <= 1:
        zol_spider("nfc")
        excel = "nfc"
    elif sys.argv[1] in urls.keys():
        zol_spider(sys.argv[1])
        excel = sys.argv[1]
    elif sys.argv[1].__contains__("zol.com") and sys.argv[1].__contains__("1.html"):
        urls["zol"] = sys.argv[1]
        zol_spider("zol")
        excel = "zol"
    else:
        print('wrong argument, only support zol first page url')


    # 重写Excel 去重+排序
    data = pd.read_excel(excel + '.xls', 'zol', dtype=str)
    data.sort_values(by=['机型', '上市日期'], inplace=True)
    wp = data.drop_duplicates(subset=['机型', '上市日期'])
    wp.to_excel(excel + s + ".xlsx", index=False)
