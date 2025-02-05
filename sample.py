# -*- coding: UTF-8 -*-

import re
import sys
import random
import time
from urllib2 import Request, urlopen

import xlwt
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf-8')


urls = {
        'nfc': u'https://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_s8059_1_1__1.html#showc'
    }


def zol_spider(year):

    wb_name = '%s.xls' %year
    wb = xlwt.Workbook(encoding="utf-8")
    sheet = wb.add_sheet("datas")

    titles = ["机型", '价格', '屏幕分辨率', "屏幕尺寸", "CPU", "主频", "电池", "主摄像头", "屏幕刷新", "RAM", "ROM"]

    par_index = {   #索引参数的列
        'name':0,
        'price':1,
        '4g':2,
        'screen':3,
        'cpu':4,
        'hz':5,
        'bettery':6,
        'camera':7,
        'os':8,
        'ram':9,
        'rom':10
    }

    for __column in range(11):
        sheet.write(0,__column,titles[__column])
    wb.save(wb_name)
    rows = 1  # excel 行数索引

    detail_domain = "http://detail.detail_domainzol.com.cn"
    head = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

    url = urls[year]
    print url
    req = Request(url, headers=head)
    response = urlopen(req)
    html = response.read().decode('gbk')
    # print html
    soup = BeautifulSoup(html, 'html.parser')

    total_page_area = soup.find('div', class_="page_total")  # 获取页面区域的信息

    __pages = re.findall(u"/(\d*) 页", total_page_area.text)  # 获取总页码

    if len(__pages) == 1:
        total_page = int(__pages[0])
        print("Total pages: %s" % total_page)
    else:
        print('get total pages failed.total %s' % len(__pages))
        sys.exit(-1)

    # 生成所有待爬的网页
    #url_templet = url.replace('1.html', '')
    unknown_list = []

    for i in range(total_page):  # 遍历，开爬
        print("page: ",i+1)
        per_url = url.replace('1.html', str(i + 1)+".html")
        #print per_url
        req = Request(per_url, headers=head)
        response = urlopen(req)
        html = response.read().decode('gbk')
        soup = BeautifulSoup(html, 'html.parser')
        result_frame = soup.find("ul", class_="result_list")  # 包含搜索信息的那个框架

        phones = result_frame.find_all("li")  # 匹配出单个手机的信息
        for phone_content in phones:
            try:
                phone_name = phone_content.find("dl", class_="pro_detail").find("a").text
                phone_price = phone_content.find("div", class_="date_price").find("b", class_="price-type").text
            except:
                continue
            sheet.write(rows,0,phone_name.split('（' )[0])
            sheet.write(rows, 1, phone_price)

            detals = phone_content.find_all("li")
            for i in detals:

                if u'分辨率' in str(i):
                    sheet.write(rows,par_index['4g'],i["title"])
                elif u'屏幕尺寸' in str(i):
                    sheet.write(rows, par_index['screen'], i["title"])
                elif u'CPU型号' in str(i):
                    sheet.write(rows, par_index['cpu'], i["title"])
                elif u'CPU频率' in str(i):
                    sheet.write(rows, par_index['hz'], i["title"])
                elif u'电池容量' in str(i):
                    sheet.write(rows, par_index['bettery'], i["title"])
                elif u'像素' in str(i):
                    sheet.write(rows, par_index['camera'], i["title"])
                elif u'屏幕刷新' in str(i):
                    sheet.write(rows, par_index['os'], i["title"])
                elif u'RAM容量' in str(i):
                    sheet.write(rows, par_index['ram'], i["title"])
                elif u'ROM容量' in str(i):
                    sheet.write(rows, par_index['rom'], i["title"])
            detail_url = phone_content.find("a", target="_blank")["href"]
            phone_detail_url = detail_domain + detail_url
            req = Request(phone_detail_url, headers=head)
            response = urlopen(req)
            html = response.read().decode('gbk')
            soup = BeautifulSoup(html, 'html.parser')

            # 以下是获取摄像头表格的代码↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓
            tds = soup.find('td', class_="hd", text=u'基本参数')  # 表格标题
            try:
                camera_area = tds.parent.parent  # 摄像头总表格
            except:
                print "can not get camera info: ", phone_detail_url
                rows += 1
                continue
            for tr in camera_area.find_all('tr'):
                try:
                    if tr.th.text == u'上市日期':
                        sheet.write(rows, title_index['上市日期'], tr.td.span.contents[0])
                    else:
                        if tr.th.text not in unknown_list:
                            print 'new parm: ', tr.th.text, phone_detail_url
                            unknown_list.append(tr.th.text)
                except:
                    pass  # 大表格外面的标题为none，会报错
            # 获取摄像头的代码结束↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑


            wb.save(wb_name)
            rows += 1
            # 注释的这段代码可以获取到手机概要的所有信息，但是无法区分机型和参数，舍弃
            # phone_name = phone_content.stripped_strings
            # for s in phone_name:
            #     print s
        sleep_time = random.randint(5,15)  #定义一个随机睡眠时间，防止被识别为爬虫，可能有点作用。
        time.sleep(sleep_time)


if __name__ == "__main__":
    # zol_spider(2019)
    if len(sys.argv) <= 1:
        zol_spider("nfc")
    elif sys.argv[1] in urls.keys():
        zol_spider(sys.argv[1])
    elif sys.argv[1].__contains__("zol.com"):
        urls["zol"]=sys.argv[1]
        zol_spider("zol")
    else:
        print(repr(sys.argv[1]))
        print('wrong argument, only support {}'.format(urls.keys()))
