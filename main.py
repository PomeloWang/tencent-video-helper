import datetime
import json
import re
import sys

import requests
import urllib.parse
from requests.exceptions import HTTPError

from settings import *

request = requests.session()

today = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def to_python(json_str: str):
    return json.loads(json_str)


def to_json(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)


def cookie_2_python(cookie):
    obj = {}
    for header in cookie.split(";"):
        param = header.split("=")
        obj[param[0].strip()] = param[1]
    return obj


def cookie_2_param(cookie_obj: dict):
    param = ""
    for k, v in cookie_obj.items():
        param += "{k}={v}; ".format(**locals())
    return param[:-2]


def decode_json_str(s):
    pattern = re.compile('{.*}')
    return json.loads(pattern.search(s).group())


def notify(title, message):
    if not CONFIG.SCKEY:
        log.info('未配置SCKEY,正在跳过推送')
        sys.exit(-1)

    log.info('准备推送通知...')
    url = 'https://sc.ftqq.com/{}.send'.format(CONFIG.SCKEY)
    payload = {'text': '{}'.format(title), 'desp': message}

    try:
        response = to_python(requests.post(url, data=payload).text)
    except Exception as e:
        log.error(e)
        raise HTTPError

    errmsg = response['errmsg']
    if errmsg == 'success':
        log.info('推送成功')
    else:
        log.error('{}: {}'.format('推送失败', errmsg))
    return log.info('任务结束')


def decode_urldecode(s):
    return urllib.parse.unquote(s)


def main():
    message = {
        'today': today,
        'ret': -1,
        'nick': '未知',
        'end': ''
    }
    # 主要是判断是否登陆成功以及刷新cookie参数
    response = request.get(url=CONFIG.AUTH_REFRESH_URL, headers=CONFIG.HEADERS).text
    auth_refresh_obj = decode_json_str(response)

    if (auth_refresh_obj.get('errcode', 9999) != 0) or (not auth_refresh_obj.get('nick', None)):
        log.error("刷新cookie参数失败, {msg}".format(**auth_refresh_obj))
        message.update({
            'ret': auth_refresh_obj.get('errcode', -1),
            'nick': decode_urldecode(auth_refresh_obj.get('nick', "未知")),
        })
        notify("腾讯视频 签到失败", CONFIG.MESSGAE_TEMPLATE.format(**message))
        sys.exit(-1)

    old_cookie_obj = cookie_2_python(CONFIG.HEADERS['Cookie'])
    need_update_fields = {
        'vuserid': 'vqq_vuserid',
        'vusession': 'vqq_vusession',
        'access_token': 'vqq_access_token'
    }

    log.info("更新Cookie参数")
    # 更新Cookie参数
    for k, v in need_update_fields.items():
        old_cookie_obj[v] = auth_refresh_obj[k]

    # 使用更新过的Cookie参数替换CONFIG.HEADERS中的Cookie参数
    CONFIG.HEADERS.update({
        'Cookie': cookie_2_param(old_cookie_obj),
        'Referer': 'https://m.v.qq.com'
    })
    log.info("更新Cookie参数成功, 开始签到")

    # QZOutputJson=({ "ret": 0,"checkin_score": 0,"msg":"OK"});
    sign_response = request.get(url=CONFIG.SIGN_URL, headers=CONFIG.HEADERS).text
    sign_obj = decode_json_str(sign_response)
    log.info(sign_obj)

    message.update({
        'ret': sign_obj['ret'],
        'nick': decode_urldecode(auth_refresh_obj['nick']),
        'message': sign_obj['msg']

    })
    log.info("签到成功 {}".format(CONFIG.MESSGAE_TEMPLATE.format(**message)))
    notify("腾讯视频 签到成功", CONFIG.MESSGAE_TEMPLATE.format(**message))


if __name__ == '__main__':
    main()
