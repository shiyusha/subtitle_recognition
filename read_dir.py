# coding=utf-8
# pip install baidu-api
"""
监听指定目录，目录中有新添加的图片，就对其进行文字识别，并将识别文字读出来。
"""
import os
import sys
import json
import base64

import win32com.client
spk = win32com.client.Dispatch('SAPI.Spvoice')
spk.rate = 10

# 保证兼容python2以及python3
IS_PY3 = sys.version_info.major == 3
if IS_PY3:
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.error import URLError
    from urllib.parse import urlencode
    from urllib.parse import quote_plus
else:
    import urllib2
    from urllib import quote_plus
    from urllib2 import urlopen
    from urllib2 import Request
    from urllib2 import URLError
    from urllib import urlencode

# 防止https证书校验不正确
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

""" 你的 APPID AK SK """
APP_ID = '16205381'
API_KEY = 'kN3IGXV7qy5jRs5YFewaDGqd'
SECRET_KEY = 'FdWOtX9xH43Y8cGCjEkgbNyjFrLPjlqw'

OCR_URL = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"

"""  TOKEN start """
TOKEN_URL = 'https://aip.baidubce.com/oauth/2.0/token'


def fetch_token():
    """ 获取token """
    params = {'grant_type': 'client_credentials',
              'client_id': API_KEY,
              'client_secret': SECRET_KEY}
    post_data = urlencode(params)
    if (IS_PY3):
        post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req, timeout=5)
        result_str = f.read()
    except URLError as err:
        print(err)
    if (IS_PY3):
        result_str = result_str.decode()

    result = json.loads(result_str)

    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if not 'brain_all_scope' in result['scope'].split(' '):
            print ('please ensure has check the  ability')
            exit()
        return result['access_token']
    else:
        print ('please overwrite the correct API_KEY and SECRET_KEY')
        exit()

def read_file(image_path):
    """    读取文件    """
    f = None
    try:
        f = open(image_path, 'rb')
        return f.read()
    except:
        print('read image file fail')
        return None
    finally:
        if f:
            f.close()

def request(url, data):
    """    调用远程服务    """
    req = Request(url, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()
        if (IS_PY3):
            result_str = result_str.decode()
        return result_str
    except  URLError as err:
        print(err)

picpath = "D:\\read"
donelist = []
while True :
    for i in os.listdir(picpath):
        if (not (i in donelist)) and (i[-3:].lower() == 'jpg' or i[-3:].lower() == 'png' or i[-3:].lower() == 'tif'):
            # if i is a pictuer and i was not treated yet.
            try:
                print(i)
                donelist.append(i)
                token = fetch_token()   # 获取access token
                image_url = OCR_URL + "?access_token=" + token  # 拼接通用文字识别url

                text = ""
                file_content = read_file(picpath+'\\'+i)  # 读取书籍页面图片
                result = request(image_url, urlencode({'image': base64.b64encode(file_content)})) # 调用文字识别服务

                # 解析返回结果
                result_json = json.loads(result)
                for words_result in result_json["words_result"]:
                    text = text + words_result["words"]

                text.replace(',', '，')
                text.replace(';', '；')
                # 打印文字
                print(text)
                spk.Speak(text)
            except:
                print(i,' ', 'failed')
