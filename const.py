# -*- coding: utf-8 -*-

# 通知配置
NOTIFY_FLAG = True  # 通知标识
NOTIFY_TYPE = 'MAIL|SMS'  # 通知方式
NOTIFY_BREAK_COUNT = 10  # 通知熔断，每天发送的最大通知数

# 短信通知配置
SMS_URL = 'http://xx.xx.xx.xx/jiayi/sms.php'
SMS_TO_NUMBERS = ['18612341234']  # 短信接收人

# 邮件通知配置
MAIL_FROM_ADDR = 'foobar@qq.com'
MAIL_TO_ADDRS = ['foo1@bar.com', 'foo2@bar.com']  # 邮件接收人
MAIL_PASSWORD = 'foobarfoobar'
MAIL_SMTP_SERVER = 'smtp.qq.com'
MAIL_TITLE = '服务健康度告警'

# 样本配置
SAMPLE_SIZE = 20  # 检测结果样本池大小
MAX_FAILS = 2  # 允许最大失败次数

# 时间间隔配置
INVOKE_INTERVAL = 5  # 时间间隔
CHECK_INTERVAL = 20  # 检测时间间隔
CHECK_FAIL_INTERVAL = 60  # 检测失败后时间间隔
REQUEST_TIMEOUT = 10  # 请求超时时间

# 服务配置
SERVICE1 = {
    'TAG': 'foobar01',
    'NAME': 'XXX生产环境01',
    'DESC': 'xx.xx.xx.xx:19011',
    'URL': 'http://xx.xx.xx.xx:19011/health',
    'METHOD': 'GET',
    'REQUEST': '',
    'EXPECT': '{"status":"UP"}'
}

SERVICE2 = {
    'TAG': 'foobar02',
    'NAME': 'XXX生产环境02',
    'DESC': 'xx.xx.xx.xx:19012',
    'URL': 'http://xx.xx.xx.xx:19012/health',
    'METHOD': 'GET',
    'REQUEST': '',
    'EXPECT': '{"status":"UP"}'
}

SERVICE_LIST = [SERVICE1, SERVICE2]
