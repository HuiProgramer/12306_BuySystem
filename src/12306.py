# !/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'HuiProgramer'

import urllib,urllib2
import ssl
import cookielib
from user import user,password,is_valid_date
from json import loads
from rk import codes
from station import station
import time
import datetime
import sys
import re


class User(object):
    def __init__(self):
        # 设置编码为utf-8
        reload(sys)
        sys.setdefaultencoding('utf-8')

        # 设置车站简称的字典
        stationShort = {}
        # 设置车站全称的字典
        stationDict = {}
        for i in station.split("@")[1:]:
            stationList = i.split("|")
            stationDict[stationList[1]] = stationList[2]
            stationShort[stationList[2]] = stationList[1]

        # 保存cookie
        c = cookielib.LWPCookieJar()
        cookie = urllib2.HTTPCookieProcessor(c)
        opener = urllib2.build_opener(cookie)

        # 模拟游览器登录
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36    (KHTML, like Gecko) Chrome/56.0.2924.90 Safari/537.36 2345Explorer/9.2.1.17116'
        }
        # 设置车次信息的字典
        self.train_number = {}
        # 设置车的部分参数的字典
        self.train_no = {}
        self.train_location = {}
        self.leftTickets = {}

        self.headers = headers
        self.opener = opener
        self.stationShort = stationShort
        self.stationDict = stationDict
        self.train_date = ""
        self.from_station = ""
        self.to_station = ""

        # 取消安全证书认证
        ssl._create_default_https_context = ssl._create_unverified_context

    def login(self):
        """模拟登录"""
        req = urllib2.Request('https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.5816821643724046')
        req.headers = self.headers
        print "正在获取验证码！"
        imgCode = self.opener.open(req).read()
        with open('code.png','wb') as fn:
            fn.write(imgCode)
        print "正在识别验证码..."
        code = codes()
        data = {
            'answer': code,
          'login_site': 'E',
           'rand':'sjrand'
        }
        data = urllib.urlencode(data)
        req = urllib2.Request('https://kyfw.12306.cn/passport/captcha/captcha-check')
        req.headers = self.headers
        html = self.opener.open(req,data = data).read()
        html = loads(html)
        if html['result_code'] != '4':
            print "验证码识别失败"
        else:
            print "验证码识别成功"

        print "正在登录..."
        data = {
            'username':user,
            'password':password,
            'appid':'otn'
        }
        data = urllib.urlencode(data)
        req = urllib2.Request('https://kyfw.12306.cn/passport/web/login')
        req.headers = self.headers
        html = self.opener.open(req,data = data).read()
        html = loads(html)
        if html['result_code'] == 0:
            print "登录成功"
        else:
            print "登录失败,正在尝试重新登录..."
            time.sleep(3)
            self.login()

        req = urllib2.Request('https://kyfw.12306.cn/otn/login/userLogin')
        req.headers = self.headers
        data = {
            '_json_att': ''
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req, data=data).read()

        req = urllib2.Request('https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin')
        req.headers = self.headers
        html = self.opener.open(req).read()

        req = urllib2.Request('https://kyfw.12306.cn/passport/web/auth/uamtk')
        req.headers = self.headers
        data = {
            'appid': 'otn'
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data = data).read()
        result = loads(html)
        tk = result['newapptk']
        req = urllib2.Request('https://kyfw.12306.cn/otn/uamauthclient')
        req.headers = self.headers
        data = {
            'tk': tk
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data = data)

        req = urllib2.Request('https://kyfw.12306.cn/otn/login/userLogin')
        req.headers = self.headers
        html = self.opener.open(req)

        req = urllib2.Request('https://kyfw.12306.cn/otn/index/initMy12306')
        req.headers = self.headers
        html = self.opener.open(req).read()


    def information(self):
        deadline = datetime.date.today() + datetime.timedelta(days = 29)
        #出发时间
        train_date = raw_input('请输入出发时间：').strip()
        if is_valid_date(train_date) and train_date >= time.strftime("%Y-%m-%d",time.localtime(time.time())) and train_date <= str(deadline) :
            self.train_date = train_date
            print 'OK'
        else:
            print 'Input Error GoodBye!'
            exit()
        #出发城市
        from_station = raw_input('请输入出发城市：').strip()
        if from_station in self.stationDict:
            self.from_station = from_station
            print 'OK'
        else:
            print 'Input Error GoodBye!'
            exit()
        #到达城市
        to_station = raw_input("请输入到达城市：").strip()
        if to_station in self.stationDict:
            self.to_station = to_station
            print 'OK'
        else:
            print 'Input Error GoodBye!'
            exit()
    def query(self):
        req = urllib2.Request('https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=%s&leftTicketDTO.from_station=%s&leftTicketDTO.to_station=%s&purpose_codes=ADULT'%(self.train_date,self.stationDict[self.from_station],self.stationDict[self.to_station]))
        req.headers = self.headers
        html = self.opener.open(req).read()
        result = loads(html)
        return result['data']['result']

    def buytickets(self,secretStr,stationTrainCode,train_no,train_location,leftTickets):
        #第一个请求
        req = urllib2.Request('https://kyfw.12306.cn/otn/login/checkUser')
        req.headers = self.headers
        data = {
            '_json_att':''
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data = data).read()
        print html

        #第二个请求
        req = urllib2.Request('https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest')
        req.headers = self.headers
        data = {
                'secretStr':urllib.unquote(secretStr),
                'train_date':self.train_date,
                'back_train_date':time.strftime("%Y-%m-%d",time.localtime(time.time())),
                'tour_flag':'dc',
                'purpose_codes':'ADULT',
                'query_from_station_name':self.from_station,
                'query_to_station_name':self.to_station,
                'undefined':'',
              }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data=data).read()
        print html

        #第三个请求
        req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/initDc')
        req.headers = self.headers
        data = {
            '_json_att':''
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data=data).read()
        globalRepeatSubmitToken = re.findall(r"globalRepeatSubmitToken = '(.*?)'",html)[0]
        key_check_isChange = re.findall(r"'key_check_isChange':'(.*?)'",html)[0]
        print key_check_isChange

        #第四个请求
        req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs')
        req.headers = self.headers
        data = {
            '_json_att':'',
             'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data = data).read()
        html = loads(html)
        html = html['data']['normal_passengers']
        print html

        #第五个请求
        print u"""%s:%s  %s:%s  %s:%s  %s:%s  %s:%s  %s:%s """%(html[0]['index_id'],html[0]['passenger_name'],html[1]['index_id'],html[1]['passenger_name'],html[2]['index_id'],html[2]['passenger_name'],html[3]['index_id'],html[3]['passenger_name'],html[4]['index_id'],html[4]['passenger_name'],html[5]['index_id'],html[5]['passenger_name'],)
        passenger_name = raw_input('请选择一个乘客(序号)：')
        html = html[int(passenger_name)]
        print """1：硬座 2：软座 3：硬卧 4：软卧 6:高级软卧 F:动卧 O：二等座 M：一等座 9：商务座"""
        seatType = raw_input('请输入你需要的座位(序号)：')
        passengerTicketStr = seatType + ','+ html['passenger_flag'] + ',' + html['passenger_id_type_code'] + ',' + html['passenger_name'] + ',' + html['passenger_id_type_code'] + ',' + html['passenger_id_no'] + ',' + html['mobile_no'] + ',N'

        oldPassengerStr = html['passenger_name'] + ','+ html['passenger_id_type_code'] + ',' + html['passenger_id_no'] + ',' + '1_'
        req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo')
        req.headers = self.headers
        data = {
                   'cancel_flag':'2',
                   'bed_level_order_num': '000000000000000000000000000000',
                   'passengerTicketStr': passengerTicketStr,
                    'oldPassengerStr':oldPassengerStr,
                    'tour_flag':'dc',
                    'whatsSelect':'1',
                    '_json_att':'',
                    'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken,
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data=data).read()
        print html

        #第六个请求
        train_date = self.train_date
        train_date = time.strptime(train_date,"%Y-%m-%d")
        train_date = time.strftime("%a %b %d %Y %H:%M:%S",train_date)
        print train_date
        train_date = str(train_date) + " GMT + 0800(中国标准时间)"
        req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount')
        req.headers = self.headers
        data = {
            'train_date': train_date,
            'train_no':train_no,
            'stationTrainCode':stationTrainCode,
            'seatType':str(seatType),
            'fromStationTelecode':self.stationDict[self.from_station],
            'toStationTelecode':self.stationDict[self.to_station],
            'leftTicket':leftTickets,
            'purpose_codes':'00',
            'train_location':train_location,
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken,
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data = data).read()
        print html
        #第七个请求
        req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue')
        req.headers = self.headers
        data = {
            '_json_att':'',
            'choose_seats':'',
            'dwAll':'N',
            'key_check_isChange':key_check_isChange,
            'leftTicketStr':leftTickets,
            'oldPassengerStr':oldPassengerStr,
            'passengerTicketStr':passengerTicketStr,
            'purpose_codes':'00',
            'randCode':'',
            'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken,
            'roomType':'00',
            'seatDetailType':'000',
            'train_location':train_location,
            'whatsSelect':'1',
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data=data).read()
        print html

        #第八个请求
        req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime?random=%s&tourFlag=dc&_json_att=&REPEAT_SUBMIT_TOKEN=%s'%(time.time(),globalRepeatSubmitToken))
        req.headers = self.headers
        data = {
            '_json_att':'',
            'random':str(time.time()),
            'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken,
            'tourFlag':'dc',
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data = data).read()
        print html
        html = loads(html)
        orderId = html['data']['orderId']
        print orderId

        #第九个请求
        req = urllib2.Request('https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue')
        req.headers = self.headers
        data = {
            '_json_att':'',
            'orderSequence_no':str(orderId),
            'REPEAT_SUBMIT_TOKEN':globalRepeatSubmitToken
        }
        data = urllib.urlencode(data)
        html = self.opener.open(req,data=data).read()
        print html

    """
    [1] = "是否停运"
    [2] = train_no
    [3] = "车次"
    [6] = "起点城市"
    [7] = "终点城市"
    [8] = "出发时间"
    [9] = "到达时间"
    [10] = "历时"
    [12] = leftTickets
    [13] = "日期"
    [15] = train_location
    [21] = "高级软卧"
    [23] = "软卧"
    [24] = "软座"
    [26] = "无座"
    [28] = "硬卧"
    [29] = "硬座"
    [30] = "二等座"
    [31] = "一等座"
    [32] = "商务座"
    [33] = "动卧"
    """
if __name__ == '__main__':
    User = User()
    User.login()
    User.information()
    for i in User.query():
        tempList = i.split('|')
        try:
            #第一种类型
            if tempList[26] == u"无" and tempList[29] == u"无" or tempList[26] == u"" or tempList[29] == u"":
                pass
            elif tempList[26] == u"有" or int(tempList[26]) > 0 or int(tempList[29]) > 0:
                User.train_number[tempList[3]] = tempList[0]
                User.train_no[tempList[3]] = tempList[2]
                User.train_location[tempList[3]] = tempList[15]
                User.leftTickets[tempList[3]] = tempList[12]
                print u"""
                该车次有票：
                日期：%s
                %s --> %s
                车次：%s
                出发时间：%s
                到达时间：%s
                历时：%s
                高级软卧：%s
                软卧：%s
                动卧：%s
                硬卧：%s
                软座：%s
                硬座：%s
                无座：%s
                """%(tempList[13],User.stationShort[tempList[6]],User.stationShort[tempList[7]],tempList[3],tempList[8],tempList[9],tempList[10],tempList[21],tempList[23],tempList[33],tempList[28],tempList[24],tempList[29],tempList[26])
                continue
            #第二种类型
            if tempList[30] == u"无" and tempList[31] == u"无" or tempList[30] == u"" or tempList[31] == u'':
                pass
            elif tempList[30] == u"有"  or int(tempList[31]) > 0 or int(tempList[30]) > 0:
                User.train_number[tempList[3]] = tempList[0]
                User.train_no[tempList[3]] = tempList[2]
                User.train_location[tempList[3]] = tempList[15]
                User.leftTickets[tempList[3]] = tempList[12]
                print u"""
                该车次有票：
                日期：%s
                %s --> %s
                车次：%s
                出发时间：%s
                到达时间：%s
                历时：%s
                商务座：%s
                一等座：%s
                二等座：%s
                高级软卧：%s
                软卧：%s
                动卧：%s
                硬卧：%s
                无座：%s
                """%(tempList[13],User.stationShort[tempList[6]],User.stationShort[tempList[7]],tempList[3],tempList[8],tempList[9],tempList[10],tempList[32],tempList[31],tempList[30],tempList[21],tempList[23],tempList[33],tempList[28],tempList[26])
                continue
            #第三种类型
            if (tempList[33] == u"无" and tempList[23] == u"无") or tempList[33] == u"" or tempList[23] == u"":
                pass
            elif tempList[33] == u"有" or int(tempList[33]) > 0 or tempList[23] == u"有" or int(tempList[23]) > 0:
                User.train_number[tempList[3]] = tempList[0]
                User.train_no[tempList[3]] = tempList[2]
                User.train_location[tempList[3]] = tempList[15]
                User.leftTickets[tempList[3]] = tempList[12]
                print u"""
                该车次有票：
                日期：%s
                %s --> %s
                车次：%s
                出发时间：%s
                到达时间：%s
                历时：%s
                二等座：%s
                高级软卧：%s
                软卧：%s
                动卧：%s
                """%(tempList[13],User.stationShort[tempList[6]],User.stationShort[tempList[7]], tempList[3],tempList[8],tempList[9],tempList[10],tempList[30],tempList[21],tempList[23],tempList[33])
                continue
            #第四种类型
            if (tempList[23] == u"无" and tempList[30] == u"无") or tempList[23] == u"" or tempList[30] == u"":
                pass
            elif tempList[23] == u"有" or int(tempList[23]) > 0 or tempList[30] == u"有" or int(tempList[30]) > 0:
                User.train_number[tempList[3]] = tempList[0]
                User.train_no[tempList[3]] = tempList[2]
                User.train_location[tempList[3]] = tempList[15]
                User.leftTickets[tempList[3]] = tempList[12]
                print u"""
               该车次有票：
               日期：%s
               %s --> %s
               车次：%s
               出发时间：%s
               到达时间：%s
               历时：%s
               二等座：%s
               软卧：%s
                """ %(tempList[13],User.stationShort[tempList[6]],User.stationShort[tempList[7]],tempList[3],tempList[8],tempList[9],tempList[10],tempList[30],tempList[23])
                continue

        except:
            continue
    stationTrainCode = raw_input('请输入你要乘坐的车次：')
    if stationTrainCode in User.train_number:
        print 'OK'
        train_no = User.train_no[stationTrainCode]
        train_location = User.train_location[stationTrainCode]
        stationFlag = User.train_number[stationTrainCode]
        leftTickets = User.leftTickets[stationTrainCode]
    else:
        print "Input Error Goodbye!"
        exit()
    User.buytickets(stationFlag,stationTrainCode,train_no,train_location,leftTickets)
