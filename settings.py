# settings
import logging

import os

__all__ = ['log', 'CONFIG']

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S')


log = logger = logging


default_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                     'Chrome/64.0.3282.204 Safari/537.36 '


class _Config:
    AUTH_REFRESH_URL = os.environ['AUTH_REFRESH_URL']
    AUTH_REFRESH_COOKIE: dict = os.environ['AUTH_REFRESH_COOKIE']
    HEADERS = {
        'Referer': 'https://v.qq.com',
        'User-Agent': default_user_agent,
        'Cookie': AUTH_REFRESH_COOKIE
    }
    SIGN_URL = 'https://vip.video.qq.com/fcgi-bin/comm_cgi?name=hierarchical_task_system&cmd=2'
    MOBILE_CHECKIN = 'http://v.qq.com/x/bu/mobile_checkin?isDarkMode=0&uiType=REGULAR'
    SCKEY = os.environ.get('SCKEY', '')


class ProductionConfig(_Config):
    LOG_LEVEL = logging.INFO


class DevelopmentConfig(_Config):
    LOG_LEVEL = logging.DEBUG


RUN_ENV = os.environ.get('RUN_ENV', 'dev')
if RUN_ENV == 'dev':
    CONFIG = DevelopmentConfig()
else:
    CONFIG = ProductionConfig()

log.basicConfig(level=CONFIG.LOG_LEVEL)


MESSGAE_TEMPLATE = '''
```
    {today:#^30}
    🔅[{nick}]
    签到积分: {checkin_score}
    签到结果: {message}
    手机签到: {mobile_checkin}
    {end:#^30}
```'''

CONFIG.MESSGAE_TEMPLATE = MESSGAE_TEMPLATE
