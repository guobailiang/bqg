# encoding=utf8
# 作者 李民康
# 时间 2021/6/21 11:03

'''
python爬取笔趣阁全站小说
1、准备三个方法
    爬取某章小说内容
        获取到某章小说链接即可
    爬取某本小说内容
        获取到小说链接，遍历小说章节列表，获取到每章的链接，调用爬取某章小说方法
    爬取全站小说内容
        遍历分页数据，获取每页的小说列表，获取每本小说的链接，调用爬取某本小说方法

2、ip防封
    设置请求头模拟浏览器发起请求 headers
    设置代理ip模拟别的设备发起请求 proxies
'''
import threading
import time

import requests
from lxml import etree
import os
import random
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 忽略警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

userAgents = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36',
    # 我本地的chrome浏览器
    # 下面是网上搜的浏览器
    'Mozilla/4.0 (Windows; MSIE 6.0; Windows NT 5.2)',  # IE6
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',  # IE7
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',  # IE8
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',  # IE9
    'Mozilla/5.0 (compatible; WOW64; MSIE 10.0; Windows NT 6.2)',  # IE10
    'Mozilla/5.0 (Windows NT 6.3; Trident/7.0; rv 11.0) like Gecko',  # IE11
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2486.0 Safari/537.36Edge/13.10586',
    # Edge
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows Phone OS 7.0; Trident/3.1; IEMobile/7.0; LG; GW910)',  # Windows phone 7
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; SAMSUNG; SGH-i917)',
    # Windows phone 7.5
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; NOKIA; Lumia 920)',
    # Windows phone 8
    'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36',
    # Chrome on windows
    'Mozilla/5.0 (iPhone; CPU iPhone OS 6_1_4 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) CriOS/27.0.1453.10 Mobile/10B350 Safari/8536.25',
    # Chrome on iphone
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    # Chrome on mac
    'Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1',  # Firefox4.0.1–MAC
    'Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11',  # Firefox4.0.1–Windows
    'Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11',  # Opera11.11–MAC
    'Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11',
    # Opera11.11–Windows
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)',  # 傲游（Maxthon）
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)',  # 腾讯TT
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)',  # 世界之窗（TheWorld）2.x
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)',  # 世界之窗（TheWorld）3.x
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)',
    # 搜狗浏览器1.x
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)',  # 360浏览器
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)',  # Avant
    'Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)',  # GreenBrowser
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50",
    "Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50",
    "Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0;",
    "Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT6.0)",
    "Mozilla/4.0(compatible;MSIE6.0;WindowsNT5.1)",
    "Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1",
    "Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1",
    "Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11",
    "Opera/9.80(WindowsNT6.1;U;en)Presto/2.8.131Version/11.11",
    "Mozilla/5.0(Macintosh;IntelMacOSX10_7_0)AppleWebKit/535.11(KHTML,likeGecko)Chrome/17.0.963.56Safari/535.11",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Maxthon2.0)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TencentTraveler4.0)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;TheWorld)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;Trident/4.0;SE2.XMetaSr1.0;SE2.XMetaSr1.0;.NETCLR2.0.50727;SE2.XMetaSr1.0)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;360SE)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1;AvantBrowser)",
    "Mozilla/4.0(compatible;MSIE7.0;WindowsNT5.1)",
]

"""
免费代理ip网站：http://www.xiladaili.com/http
目前收容了前6页的200多个ip
"""
proxieList = [
    '103.103.3.6:8080',
    '113.237.3.178:9999',
    '118.117.188.171:3256',
    '45.228.188.241:999',
    '104.254.238.122:20171',
    '211.24.95.49:47615',
    '103.205.15.97:8080',
    '185.179.30.130:8080',
    '190.108.88.97:999',
    '81.30.220.116:8080',
    '178.134.208.126:50824',
    '175.42.122.142:9999',
    '182.84.144.91:3256',
    '188.166.125.206:38892',
    '167.172.180.46:33555',
    '58.255.7.90:9999',
    '190.85.244.70:999',
    '118.99.100.164:8080',
    '182.84.145.181:3256',
    '45.236.168.183:999',
    '114.233.189.228:9999',
    '171.35.213.44:9999',
    '131.153.151.250:43064',
    '106.45.220.42:3256',
    '177.229.194.30:999',
    '195.46.124.94:4444',
    '113.237.1.179:9999',
    '182.84.144.12:3256',
    '36.56.102.35:9999',
    '131.153.151.250:8003',
    '45.225.88.220:999',
    '195.9.61.22:45225',
    '43.239.152.254:8080',
    '36.255.211.1:54623',
    '114.67.108.243:8081',
    '197.148.50.132:8080',
    '179.49.161.210:999',
    '103.139.194.69:8080',
    '49.232.118.212:3128',
    '190.61.63.83:999',
    '117.157.197.18:3128',
    '27.152.194.253:8888',
    '183.88.2.123:8080',
    '60.170.152.46:38888',
    '45.235.110.66:53281',
    '49.86.58.36:9999',
    '45.177.109.195:8080',
    '60.216.20.210:8001',
    '124.70.155.89:808',
    '202.6.227.174:3888',
    '121.232.148.66:3256',
    '131.100.212.102:8080',
    '177.105.232.114:8080',
    '27.43.184.240:9999',
    '124.66.54.112:9999',
    '103.146.196.85:8081',
    '103.24.125.33:83',
    '200.122.226.43:999',
    '49.85.188.171:8058',
    '110.18.154.46:9999',
    '172.104.15.247:3128',
    '118.117.188.66:3256',
    '45.229.32.190:999',
    '172.104.4.181:3128',
    '35.210.56.187:3128',
    '47.100.96.27:8080',
    '222.85.190.32:8090',
    '218.2.214.107:80',
    '150.138.253.73:808',
    '124.70.206.57:808',
    '1.2.252.65:8080',
    '167.99.123.63:8080',
    '121.36.17.97:808',
    '109.74.203.7:3128',
    '182.52.83.213:8080',
    '218.88.204.96:3256',
    '218.60.8.99:3129',
    '106.45.104.136:3256',
    '61.160.210.223:808',
    '220.163.129.150:808',
    '218.60.8.83:3129',
    '113.100.209.98:3128',
    '106.45.105.172:3256',
    '144.126.139.121:3128',
    '163.172.221.209:443',
    '150.138.253.72:808',
    '14.116.213.100:8081',
    '190.108.93.82:999',
    '116.115.211.2:9999',
    '113.100.209.62:3128',
    '193.136.19.68:8080',
    '157.230.103.91:44816',
    '103.139.181.103:3128',
    '203.91.121.212:3128',
    '113.100.209.113:3128',
    '113.238.142.208:3128',
    '47.100.207.139:8080',
    '124.232.227.10:3128',
    '119.84.70.198:6666',
    '118.117.188.116:3256',
    '59.124.224.180:4378',
    '178.63.17.151:3128',
    '118.190.244.234:3128',
    '188.166.125.206:44199',
    '35.195.6.233:3128',
    '170.82.115.58:999',
    '143.198.168.95:8080',
    '161.202.226.194:80',
    '191.234.166.244:80',
    '157.230.103.91:44133',
    '59.124.224.180:3128',
    '192.248.146.116:3128',
    '20.70.209.150:8080',
    '188.166.125.206:37775',
    '177.104.4.167:53281',
    '220.132.20.215:3128',
    '119.81.71.27:8123',
    '167.86.110.240:3128',
    '138.199.4.96:3128',
    '45.14.185.237:8080',
    '149.28.37.131:3128',
    '121.232.148.100:3256',
    '167.172.180.46:43690',
    '181.78.23.135:999',
    '167.99.62.12:8080',
    '183.91.0.120:3128',
    '167.172.180.40:41102',
    '117.239.29.115:3128',
    '51.158.68.133:9999',
    '167.172.180.46:34291',
    '167.172.180.40:34265',
    '169.57.1.85:8123',
    '167.172.180.46:35330',
    '119.81.71.27:80',
    '1.0.205.87:8080',
    '91.202.240.208:51678',
    '45.77.8.93:3128',
    '159.8.114.37:8123',
    '216.21.18.193:80',
    '117.187.167.224:3128',
    '91.132.139.194:3128',
    '169.57.1.84:8123',
    '159.8.114.37:80',
    '169.57.1.85:80',
    '169.57.1.84:80',
    '120.196.112.6:3128',
    '61.73.1.198:8080',
    '45.71.68.51:8080',
    '159.197.128.8:3128',
    '117.94.141.160:9999',
    '54.68.25.206:8000',
    '120.78.240.243:3228',
    '58.253.144.103:9999',
    '60.7.163.18:9999',
    '171.35.214.144:9999',
    '218.14.14.104:9999',
    '42.7.4.59:9999',
    '175.146.211.202:9999',
    '75.109.186.174:3128',
    '223.243.177.197:9999',
    '223.242.108.146:9999',
    '60.179.227.77:3000',
    '220.191.47.154:9000',
    '220.201.84.237:9999',
    '27.43.191.111:9999',
    '60.169.132.154:9999',
    '115.218.1.220:9000',
    '27.40.125.144:9999',
    '59.33.55.245:9999',
    '42.176.134.149:9999',
    '188.6.164.138:30255',
    '36.57.231.108:9999',
    '113.194.141.252:9999',
    '27.43.184.210:9999',
    '27.43.186.77:9999',
    '27.43.186.184:9999',
    '58.22.177.94:9999',
    '175.146.213.213:9999',
    '121.230.225.222:9999	',
    '218.14.15.249:9999',
    '182.87.136.227:9999	',
    '58.255.206.209:9999	',
    '58.253.144.115:9999',
    '36.248.133.61:9999',
    '42.7.29.70:9999',
    '42.177.141.50:9999',
    '223.243.245.101:9999	',
    '183.166.118.211:8888',
    '59.55.166.247:3256',
    '60.17.206.109:9999',
    '171.35.140.11:9999',
    '58.253.144.226:9999',
    '163.204.92.114:9999',
    '171.35.161.216:9999',
    '36.7.26.110:9999',
    '61.161.29.174:9999',
    '36.250.156.123:9999',
    '36.56.103.193:9999',
    '36.56.100.34:9999',
    '58.253.155.194:9999',
    '117.94.142.200:9999',
    '49.73.143.164:9999',
    '60.168.206.28:9999',
    '212.200.42.214:8080',
    '123.171.42.98:3256',
    '120.86.39.6:9999',
    '111.72.25.83:3256',
    '117.94.157.213:9999',
    '163.179.199.130:9999',
    '42.84.175.177:9999',
    '218.27.221.170:9999',
    '115.216.119.30:8888',
    '111.72.25.50:3256',
    '106.45.104.208:3256',
    '112.195.240.6:3256',
    '221.1.39.114:8118',
    '125.72.106.235:3256',
    '59.33.59.248:9999',
    '101.75.189.199:9999',
    '45.123.25.49:54913',
    '117.64.234.28:1133',
    '114.100.0.216:9999',
    '117.69.29.88:9999',
    '124.66.55.239:9999',
    '113.237.1.115:9999',
    '183.166.67.20:9999',
    '117.64.224.9:1133',
    '115.211.35.145:9000',
    '114.232.110.191:8888',
    '113.237.4.213:9999',
    '114.98.114.212:3256',
    '113.121.95.97:9999',
    '14.38.255.22:80',
    '114.100.0.34:9999',
    '183.166.6.27:8888',
    '122.234.89.169:9000',
    '114.99.0.118:8888',
    '42.176.135.250:9999',
    '113.58.179.42:9999',
    '110.18.154.231:9999',
    '111.177.192.211:3256',
    '112.91.79.80:9999',
    '60.174.190.218:9999',
    '124.94.255.43:9999',
    '115.219.2.2:3256',
    '121.230.210.167:3256',
    '116.115.211.74:9999',
    '110.229.154.145:9999',
    '118.212.104.248:9999',
    '121.232.148.110:3256',
    '58.255.207.34:9999',
    '104.254.238.122:21435',
    '60.174.188.201:9999',
    '60.174.191.132:9999',
    '125.40.210.239:9999',
    '125.87.95.81:3256',
    '36.248.132.68:9999',
    '121.19.0.184:9999',
    '115.218.2.233:9000',
    '13.239.32.239:80',
    '150.255.131.25:9999',
    '124.94.252.210:9999',
    '117.64.234.124:9999',
    '117.69.29.146:9999',
    '101.75.185.158:9999',
    '60.174.191.56:9999',
    '113.229.4.206:9999',
    '115.62.42.206:9999',
    '183.166.66.11:9999',
    '112.91.78.88:9999',
    '36.91.160.171:8080',
    '58.255.199.7:9999',
    '36.56.103.10:9999',
    '112.195.243.251:3256	',
    '218.64.142.172:9999',
    '78.8.174.35:1080',
    '175.7.199.30:3256',
    '103.233.153.58:1080',
    '42.177.140.174:9999',
    '120.86.39.141:9999',
    '27.40.106.191:9999',
    '113.194.28.51:9999',
    '42.237.102.128:9999',
    '110.18.154.68:9999	',
    '27.152.194.216:8888',
    '163.204.93.230:9999',
    '118.117.189.154:3256	',
    '113.194.30.94:9999',
    '175.43.35.44:9999',
    '175.42.68.208:9999',
    '120.83.110.203:9999',
    '113.176.195.145:4153',
    '114.231.8.167:8888	',
    '27.159.164.111:8888',
    '113.237.0.190:9999',
    '113.237.0.32:9999',
    '180.122.141.155:9999',
    '157.230.34.152:37403',
    '113.194.141.91:9999',
    '180.122.75.201:9999',
    '175.42.129.167:9999',
    '118.212.106.232:9999',
    '115.197.127.221:9000	',
    '47.254.247.210:3128',
    '113.194.143.84:9999',
    '113.195.225.173:9999',
    '113.194.140.140:9999',
    '101.18.83.124:9999',
    '115.219.3.223:3256',
    '120.86.38.24:9999',
    '115.218.0.139:9000',
    '223.240.208.169:9999',
    '60.174.189.231:9999',
    '60.167.112.214:1133',
    '193.149.225.74:80',
    '42.177.139.43:9999	',
    '27.43.189.38:9999',
    '182.87.138.47:9999',
    '58.253.158.175:9999',
    '113.237.5.171:9999',
    '85.216.127.178:3128',
    '60.174.190.85:9999',
    '114.100.2.211:9999',
    '222.141.244.203:9999',
    '175.147.106.109:9999',
    '42.7.30.60:9999',
    '58.255.7.167:9999',
    '42.7.30.249:9999',
    '163.204.93.1:9999',
    '58.255.6.0:9999',
    '223.243.229.199:9999',
    '182.46.110.221:9999',
    '182.87.136.27:9999',
    '42.238.71.218:9999',
    '8.129.2.143:3128',
    '171.35.147.9:9999',
    '36.56.101.72:9999',
    '59.63.74.197:9999',
    '49.49.27.242:8080',
    '171.35.141.161:9999',
    '58.252.201.100:9999',
    '36.56.101.117:9999',
    '27.192.172.131:9000',
    '58.255.207.125:9999',
    '223.244.179.165:3256',
    '223.243.177.108:9999',
    '175.146.209.161:9999',
    '58.255.207.88:9999',
    '49.70.32.168:8888',
    '120.83.104.97:9999',
    '60.17.204.148:9999',
    '60.168.207.175:8888',
]

# 代理ip
# 如果请求的ip是https类型的，但代理的ip是只支持http的，那么还是使用本机的ip，
# 如果请求的ip是http类型的，那么代理的ip一定要是http的，前面不能写成https。
proxies = {
    'https://': random.choice(proxieList)  # 随机选择一个代理
    # 'https://': '103.103.3.6:8080'  # 随机选择一个代理
}

# 请求头
headers = {
    'User-Agent': random.choice(userAgents)  # 每次请求随机选择一个useragent 防止ip被封
}


# 爬取全部页小说
def getOnePageBooks(bookNum, page):
    pageUrl = 'https://www.52bqg.cc/top/allvisit/' + str(page) + '.html'

    html = requests.get(url=pageUrl, headers=headers, verify=False, proxies=proxies)
    html.encoding = 'gbk'
    # 解析返回的html
    content = etree.HTML(html.text)
    bookList = content.xpath('//*[@id="main"]/div[1]/li')  # 获取本页小说列表
    # 打印日志

    # 遍历小说列表
    # for i in range(0, len(bookList)):
    bookName = ''.join(
        bookList[bookNum].xpath('//*[@id="main"]/div[1]/li[' + str(bookNum + 1) + ']/span[2]/a/text()'))  # 书名
    bookUrl = ''.join(
        bookList[bookNum].xpath('//*[@id="main"]/div[1]/li[' + str(bookNum + 1) + ']/span[2]/a/@href'))  # 小说链接
    # 打印日志
    print('bookNum:' + str(bookNum) + '第' + str(page) + '页，第' + str(bookNum + 1) + '本小说，共' + str(
        len(bookList)) + '本小说===|||===' + str(bookNum + 1) + '.书名：《' + bookName + '》 ==>' + bookUrl)

    # 调用爬取整本书的方法
    getOneBook(bookUrl)


# 爬取一本小说的 信息 :《书名》+作者+简介+更新时间+最新章节+总章节+所有章节列表（章节名称）+小说分类
def getOneBook(bookUrl):
    html = requests.get(url=bookUrl, headers=headers, verify=False, proxies=proxies)
    html.encoding = 'gbk'
    # 解析返回的html
    content = etree.HTML(html.text)

    bookName = '《' + ''.join(content.xpath('//*[@id="info"]/h1/text()')) + '》'.replace(' ','').replace('\xa0', ' ')  # 书名
    author = '作者：' + ''.join(content.xpath('//*[@id="info"]/p[1]/a/text()'))  # 作者
    updateTime = ''.join(content.xpath('//*[@id="info"]/p[3]/text()')).replace('\xa0', ' ').replace('\u200b',
                                                                                                    ' ')  # 更新时间
    desc = ''.join(content.xpath('//*[@id="intro"]/text()')).replace('\xa0', ' ')  # 简介
    newSection = '最新章节：' + ''.join(content.xpath('//*[@id="info"]/p[4]/a/text()'))  # 最新章节
    category = ''.join(content.xpath('/html/body/div[2]/div[1]/text()'))[2:7].replace(' ', '')  # 小说分类

    # 写入到文件
    bookPath = './books_page11-40/' + category + '/'  # 小说保存目录 分类名/小说名.txt  如果不存在，就创建
    if not os.path.exists(bookPath):
        os.makedirs(bookPath)
    f = open(bookPath + bookName + '.txt', 'w', encoding='gbk')  # 写入书名,作者等信息
    f.write(bookName + '\n')
    f.write(author + '\n')
    f.write(updateTime + '\n')
    f.write(desc + '\n')
    f.write(newSection + '\n')
    f.write(category + '\n\n\n\n')
    f.close()

    # 获取这本书下的所有章节列表
    sectionList = content.xpath('//*[@id="list"]/dl/dd')
    # 遍历正文章节列表，并且爬取每一章的内容 包括 章节名+章节内容、
    downLoadSection = 2000;  # 要下载的章节数量，大部分书的章节数量都在2000以下，
    if len(sectionList) < downLoadSection:
        downLoadSection = len(sectionList)
    for i in range(13, downLoadSection):
        f1 = open(bookPath + bookName + '.txt', 'a+', encoding='gbk')
        sectionName = ''.join(sectionList[i].xpath('//*[@id="list"]/dl/dd[' + str(i) + ']/a/text()'))  # 章节名称
        sectionUrl = ''.join(sectionList[i].xpath('//*[@id="list"]/dl/dd[' + str(i) + ']/a/@href'))  # 章节url
        # 打印日志
        print(str(i - 12) + '.' + sectionName + '==>' + bookUrl + sectionUrl)
        # 利用章节url爬取章节内容--调用爬取章节内容方法
        text = getOnSection(bookUrl + sectionUrl)
        random_sleep()  # 爬取一章之后随机睡眠一小会
        f1.write(sectionName + '\n\n')
        f1.write(text + '\n\n')
        f1.close()


# 爬取一章小说的方法
def getOnSection(sectionUrl):
    # print('getOnSection' + sectionUrl)
    html = requests.get(url=sectionUrl, headers=headers, verify=False, proxies=proxies)
    html.encoding = 'gbk'
    # 解析返回的html
    content = etree.HTML(html.text)
    text = ''.join(content.xpath('//*[@id="content"]/text()')).replace('\xa0', ' ').replace('     ', '\n').replace(
        '\u200b', ' ').replace('\ufffd',' ')
    return text


'''正态分布随机睡眠
    :param mu: 平均值
    :param sigma: 标准差，决定波动范围
'''
def random_sleep(mu=1, sigma=0.3):
    secs = random.normalvariate(mu, sigma)
    if secs <= 0:
        secs = mu  # 太小则重置为平均值
    time.sleep(secs)


class myThread(threading.Thread):
    def __init__(self, threadID, page, threadNum):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.page = page
        self.threadNum = threadNum

    def run(self):
        print('线程' + str(threadNum) + '开始,第' + str(self.page) + '页，第'+str(self.threadID+1)+'本小说')
        getOnePageBooks(self.threadID, self.page)
        print('线程' + str(threadNum) + '结束,第' + str(self.page) + '页，第'+str(self.threadID+1)+'本小说')



threadNum = 0;#第几个线程
for page in range(11, 41):  # 页码 
    threadNum = threadNum + 1
    for i in range(0, 50):  # 每页小说列表 每页50本，这里获取每页的全部的50本
        threadNum += 1
        t = myThread(i, page, threadNum)#i每页的第几本书  page 第几页  threadNum:第几个线程-有点小bug
        t.start()

