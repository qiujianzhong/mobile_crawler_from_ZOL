# mobile_crawler_from_ZOL
简单的爬虫，爬取中关村在线手机的信息

原来的库是：github.com/MrLeopard/mobile_crawler_from_ZOL.git 

python2.7

pip2 install xlwt bs4 numpy pandas xlrd openpyxl

#Pyinstaller -Fpip install pyinstaller==3.2.1

#改动点
修复部分bug

默认爬取所有支持nfc机型的手机

新增可以爬取指定传入的中关村url（入口必须是第一页）


# 使用方法
默认拉取含nfc的手机型号，并汇总数据到Excel，并去重后排序
>python2 sample_and_date.py

拉取自定义链接
> python2 sample_and_date.py "https://detail.zol.com.cn/cell_phone_advSearch/subcate57_1_m1673-s8059_1_1_0_1.html#showc"

