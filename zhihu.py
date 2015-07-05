# -*- coding: utf-8 -*-

import os
import re
import time
import json
import platform
import requests
import html2text
import ConfigParser
from bs4 import BeautifulSoup
import sys
import exceptions
from Bloom_Filter import BloomFilter

#reload(sys)
#sys.setdefaultencoding('utf8')

initial_user_url = "http://www.zhihu.com/people/BigMing"
bf = BloomFilter(1000000000,10)
bf.add(initial_user_url)


session = None

cookies = {}


def create_session():
    global session
    global cookies
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    cookies = cf._sections['cookies']

    email = cf.get("info", "email")
    password = cf.get("info", "password")
    cookies = dict(cookies)

    s = requests.session()
    login_data = {"email": email, "password": password}
    header = {
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36",
        'Host': "www.zhihu.com",
        'Referer': "http://www.zhihu.com/",
        'X-Requested-With': "XMLHttpRequest"
    }

    r = s.post('http://www.zhihu.com/login', data=login_data, headers=header)
    if r.json()["r"] == 1:
        print "Login Failed, reason is:"
        for m in r.json()["msg"]:
            print r.json()["msg"][m]
        print "Use cookies"
        has_cookies = False
        for key in cookies:
            if key != '__name__' and cookies[key] != '':
                has_cookies = True
                break
        if has_cookies == False:
            raise ValueError("请填写config.ini文件中的cookies项.")
    session = s


class User:
    user_url = None
    # session = None
    soup = None
    user_id = None
    user_followers_num=None
    user_gender = None
    user_pic_url=None

    def __init__(self, user_url, user_id=None, user_followers_num=None, gender=None, pic_url=None):
        if user_url == None:
            self.user_id = "匿名用户"
        elif user_url[0:28] != "http://www.zhihu.com/people/":
            raise ValueError("\"" + user_url + "\"" + " : it isn't a user url.")
        else:
            self.user_url = user_url
            if user_id != None:
                self.user_id = user_id
            if user_followers_num != None:
                self.user_followers_num = user_followers_num
            if gender !=None:
                self.user_gender = gender
            if pic_url != None:
                self.user_pic_url=pic_url


    def parser(self):

        global session
        global cookies

        if session == None:
            create_session()
        s = session
        has_cookies = False
        for key in cookies:
            if key != '__name__' and cookies[key] != '':
                has_cookies = True
                r = s.get(self.user_url, cookies=cookies, timeout=10)
                break
        if has_cookies == False:
            r = s.get(self.user_url, timeout=10)
        soup = BeautifulSoup(r.content)
        self.soup = soup

    def get_user_id(self):
        if self.user_url == None:
            # print "I'm anonymous user."
            if platform.system() == 'Windows':
                return "匿名用户".decode('utf-8','ignore').encode('gbk','ignore')
            else:
                return "匿名用户"
        else:
            if hasattr(self, "user_id"):
                if platform.system() == 'Windows':
                    return self.user_id.decode('utf-8','ignore').encode('gbk','ignore')
                else:
                    return self.user_id
            else:
                if self.soup == None:
                    self.parser()
                soup = self.soup
                user_id = soup.find("div", class_="title-section ellipsis") \
                    .find("span", class_="name").string.encode("utf-8",'ignore')
                self.user_id = user_id
                if platform.system() == 'Windows':
                    return user_id.decode('utf-8','ignore').encode('gbk','ignore')
                else:
                    return user_id

    def get_user_gender(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return -1
        else:
            if self.soup == None:
                try:
                    self.parser()
                except:
                    return -1
            soup = self.soup
            if soup.find("span", class_="item gender"):
                gender= soup.find("span", class_="item gender").i["class"][1]
                #print gender
                if gender =='icon-profile-male':
                    self.user_gender = 1
                    return 1
                else:
                    self.user_gender = 0
                    return 0
            else:
                self.user_gender = 2
                return 2

    def get_followees_num(self):
        if self.user_url == None:
            print "I'm anonymous user."
            return 0
        else:
            if self.soup == None:
                try:
                    self.parser()
                    soup = self.soup
                    followees_num = int(soup.find("div", class_="zm-profile-side-following zg-clear") \
                                .find("a").strong.string)
                    return followees_num
                except:
                    return 0
            else:
                try:
                    soup = self.soup
                    followees_num = int(soup.find("div", class_="zm-profile-side-following zg-clear") \
                                .find("a").strong.string)
                    return followees_num
                except:
                    return 0

              
    def get_followees_with_condition(self, limit_number=1000):

        global session
        global cookies

        if self.user_url == None:
            print "I'm anonymous user."
            return
            yield
        else:
            followees_num = self.get_followees_num()
            
            if followees_num == 0:
                return
                yield
            else:
                try:
                    if session == None:
                        create_session()
                    s = session
                    followee_url = self.user_url + "/followees"
                    has_cookies = False
                
                    for key in cookies:
                        if key != '__name__' and cookies[key] != '':
                            has_cookies = True
                            r = s.get(followee_url, cookies=cookies, timeout=10)
                            break
                    if has_cookies == False:
                        r = s.get(followee_url, timeout=10)
                    soup = BeautifulSoup(r.content)
                except:
                    return
                    yield
                    
                for i in xrange((followees_num - 1) / 20 + 1):
                    if i == 0:
                        user_url_list = soup.find_all("div", class_="zm-profile-card zm-profile-section-item zg-clear no-hovercard")
                        for j in xrange(min(followees_num, 20)):
                            
                            length=len(user_url_list[j].find("div", class_="details zg-gray").find("a").string)
                            pic_url=user_url_list[j].find("img")["src"]
                            
                            followee_count_1=int(user_url_list[j].find("div", class_="details zg-gray").find("a").string[0:length-4])

                            gender=2
                            
                            if (followee_count_1>limit_number):

                                if bf.lookup(user_url_list[j].h2.a["href"])==0:
                                    try:
                                        gender_length=len(user_url_list[j].find("div", class_="zg-right").find("button").string)
                                        gender_text = user_url_list[j].find("div", class_="zg-right").find("button").string[0:length].encode('utf-8','ignore')
                                    
                                        var1='关注他'
                                        var2='关注她'
                                        var3='取消关注'
                                        var4='关注'
                                    
                                        if(gender_text.decode('utf-8')==var1.decode('utf-8')):
                                            gender=1

                                        if(gender_text.decode('utf-8')==var2.decode('utf-8')):
                                            gender=0

                                        if(gender_text.decode('utf-8')==var3.decode('utf-8')):
                                            gender=3

                                        if(gender_text.decode('utf-8')==var4.decode('utf-8')):
                                            gender=2
                                        
                                    except:
                                        gender=4
                                        
                                    print gender
                                    yield User(user_url_list[j].h2.a["href"], user_url_list[j].h2.a.string.encode("utf-8",'ignore'), followee_count_1, gender, pic_url)
                                    bf.add(user_url_list[j].h2.a["href"])
                    else:
                        try:
                            post_url = "http://www.zhihu.com/node/ProfileFolloweesListV2"
                            _xsrf = soup.find("input", attrs={'name': '_xsrf'})["value"]
                            offset = i * 20
                            hash_id = re.findall("hash_id&quot;: &quot;(.*)&quot;},", r.text)[0]
                            params = json.dumps({"offset": offset, "order_by": "created", "hash_id": hash_id})
                            data = {
                                '_xsrf': _xsrf,
                                'method': "next",
                                'params': params
                            }
                            header = {
                                'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36",
                                'Host': "www.zhihu.com",
                                'Referer': followee_url
                            }
                            has_cookies = False
                        
                            for key in cookies:
                                if key != '__name__' and cookies[key] != '':
                                    has_cookies = True
                                    r_post = s.post(post_url, data=data, headers=header, cookies=cookies, timeout=10)
                                    break
                            if has_cookies == False:
                                r_post = s.post(post_url, data=data, headers=header, timeout=10)
                            followee_list = r_post.json()["msg"]
                        except:
                            return
                            yield
                            
                        for j in xrange(min(followees_num - i * 20, 20)):

                            followee_soup = BeautifulSoup(followee_list[j])
                            length=len(followee_soup.find("div", class_="details zg-gray").find("a").string)
                            followee_count_2=int(followee_soup.find("div", class_="details zg-gray").find("a").string[0:length-4])

                            gender=2
                            
                            if (followee_count_2>limit_number):
                                
                                user_url_list = followee_soup.find("div", class_="zm-profile-card zm-profile-section-item zg-clear no-hovercard")                           
                                    
                                if bf.lookup(user_url_list.h2.a["href"])==0:
                                    try:
                                        gender_text=followee_soup.find("div", class_="zg-right").find("button").string.encode('utf-8','ignore')
                                    
                                        var1='关注他'
                                        var2='关注她'
                                        var3='取消关注'
                                        var4='关注'
                                    
                                        if(gender_text.decode('utf-8')==var1.decode('utf-8')):
                                            gender=1

                                        if(gender_text.decode('utf-8')==var2.decode('utf-8')):
                                            gender=0

                                        if(gender_text.decode('utf-8')==var3.decode('utf-8')):
                                            gender=3
                                            
                                        if(gender_text.decode('utf-8')==var4.decode('utf-8')):
                                            gender=2
                                    except:
                                        gender=4
                                        
                                
                                    print gender
                                
                                    pic_url=followee_soup.find("img")["src"]
                                    yield User(user_url_list.h2.a["href"], user_url_list.h2.a.string.encode("utf-8",'ignore'),followee_count_2, gender, pic_url)
                                    bf.add(user_url_list.h2.a["href"])
