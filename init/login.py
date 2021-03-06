#!/bin/env python
# -*- coding=utf-8 -*-
import random
import json
import re
import socket
from time import sleep

from config.ticketConf import _get_yaml
from PIL import Image
from damatuCode.damatuWeb import DamatuApi
from myException.UserPasswordException import UserPasswordException
from myUrllib import myurllib2


class GoLogin:
    def __init__(self, httpClint, urlConf):
        self.httpClint = httpClint
        self.randCode = ""
        self.urlConf = urlConf

    def cookietp(self):
        print("正在获取cookie")
        url = self.urlConf["loginInit"]["req_url"]
        self.httpClint.send(url)
        # Url = "https://kyfw.12306.cn/otn/login/init"
        # myurllib2.get(Url)
        # for index, c in enumerate(myurllib2.cookiejar):
        #     stoidinput(c)

    def readImg(self):
        """
        增加手动打码，只是登录接口，完全不用担心提交订单效率
        思路
        1.调用PIL显示图片
        2.图片位置说明，验证码图片中每个图片代表一个下标，依次类推，1，2，3，4，5，6，7，8
        3.控制台输入对应下标，按照英文逗号分开，即可手动完成打码，
        :return:
        """
        print ("下载验证码...")
        codeimgUrl = self.urlConf["getCodeImg"]["req_url"]
        img_path = './tkcode'
        result = self.httpClint.send(codeimgUrl)
        try:
            open(img_path, 'wb').write(result)
            if _get_yaml()["is_aotu_code"]:
                self.randCode = DamatuApi(_get_yaml()["damatu"]["uesr"], _get_yaml()["damatu"]["pwd"], img_path).main()
            else:
                img = Image.open('./tkcode')
                img.show()
                self.codexy()
        except OSError as e:
            print (e)
            pass

    def codexy(self):
        """
        获取验证码
        :return: str
        """

        Ofset = raw_input("请输入验证码: ")
        select = Ofset.split(',')
        post = []
        offsetsX = 0  # 选择的答案的left值,通过浏览器点击8个小图的中点得到的,这样基本没问题
        offsetsY = 0  # 选择的答案的top值
        for ofset in select:
            if ofset == '1':
                offsetsY = 46
                offsetsX = 42
            elif ofset == '2':
                offsetsY = 46
                offsetsX = 105
            elif ofset == '3':
                offsetsY = 45
                offsetsX = 184
            elif ofset == '4':
                offsetsY = 48
                offsetsX = 256
            elif ofset == '5':
                offsetsY = 36
                offsetsX = 117
            elif ofset == '6':
                offsetsY = 112
                offsetsX = 115
            elif ofset == '7':
                offsetsY = 114
                offsetsX = 181
            elif ofset == '8':
                offsetsY = 111
                offsetsX = 252
            else:
                pass
            post.append(offsetsX)
            post.append(offsetsY)
        self.randCode = str(post).replace(']', '').replace('[', '').replace("'", '').replace(' ', '')

    def auth(self):
        """认证"""
        authUrl = self.urlConf["auth"]["req_url"]
        authData = {"appid": "otn"}
        tk = self.httpClint.send(authUrl, authData)
        return tk

    def codeCheck(self):
        """
        验证码校验
        :return:
        """
        codeCheck = self.urlConf["codeCheck"]["req_url"]
        codeCheckData = {
            "answer": self.randCode,
            "rand": "sjrand",
            "login_site": "E"
        }
        fresult = self.httpClint.send(codeCheck, codeCheckData)
        if "result_code" in fresult and fresult["result_code"] == "4":
            print ("验证码通过,开始登录..")
            return True
        else:
            if "result_message" in fresult:
                print(fresult["result_message"])
            sleep(1)
            self.httpClint.del_cookies()

    def baseLogin(self, user, passwd):
        """
        登录过程
        :param user:
        :param passwd:
        :return: 权限校验码
        """
        logurl = self.urlConf["login"]["req_url"]
        logData = {
            "username": user,
            "password": passwd,
            "appid": "otn"
        }
        tresult = self.httpClint.send(logurl, logData)
        if 'result_code' in tresult and tresult["result_code"] == 0:
            print ("登录成功")
            tk = self.auth()
            if "newapptk" in tk and tk["newapptk"]:
                return tk["newapptk"]
            else:
                return False
        elif 'result_message' in tresult and tresult['result_message']:
            messages = tresult['result_message']
            if messages.find("密码输入错误") is not -1:
                raise UserPasswordException("{0}".format(messages))
            else:
                print ("登录失败: {0}".format(messages))
                print ("尝试重新登陆")
                return False
        else:
            return False

    def getUserName(self, uamtk):
        """
        登录成功后,显示用户名
        :return:
        """
        if not uamtk:
            return "权限校验码不能为空"
        else:
            uamauthclientUrl = self.urlConf["uamauthclient"]["req_url"]
            data = {"tk": uamtk}
            uamauthclientResult = self.httpClint.send(uamauthclientUrl, data)
            if uamauthclientResult:
                if "result_code" in uamauthclientResult and uamauthclientResult["result_code"] == 0:
                    print("欢迎 {} 登录".format(uamauthclientResult["username"]))
                    return True
                else:
                    return False
            else:
                self.httpClint.send(uamauthclientUrl, data)
                url = self.urlConf["getUserInfo"]["req_url"]
                self.httpClint.send(url)

    def go_login(self):
        """
        登陆
        :param user: 账户名
        :param passwd: 密码
        :return:
        """
        user, passwd = _get_yaml()["set"]["12306count"][0]["uesr"], _get_yaml()["set"]["12306count"][1]["pwd"]
        if not user or not passwd:
            raise UserPasswordException("温馨提示: 用户名或者密码为空，请仔细检查")
        login_num = 0
        while True:
            self.cookietp()
            self.httpClint.set_cookies(_jc_save_wfdc_flag="dc", _jc_save_fromStation="%u4E0A%u6D77%u8679%u6865%2CAOH", _jc_save_toStation="%u5170%u5DDE%u897F%2CLAJ", _jc_save_fromDate="2018-02-14", _jc_save_toDate="2018-01-16", RAIL_DEVICEID="EN_3_EGSe2GWGHXJeCkFQ52kHvNCrNlkz9n1GOqqQ1wR0i98WsD8Gj-a3YHZ-XYKeESWgCiJyyucgSwkFOzVHhHqfpidLPcm2vK9n83uzOPuShO3Pl4lCydAtQu4BdFqz-RVmiduNFixrcrN_Ny43135JiEtqLaI")
            self.readImg()
            login_num += 1
            self.auth()
            if self.codeCheck():
                uamtk = self.baseLogin(user, passwd)
                if uamtk:
                    self.getUserName(uamtk)
                    break

    def logout(self):
        url = 'https://kyfw.12306.cn/otn/login/loginOut'
        result = myurllib2.get(url)
        if result:
            print ("已退出")
        else:
            print ("退出失败")


# if __name__ == "__main__":
#     # main()
#     # logout()