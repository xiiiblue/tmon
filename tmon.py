#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from logging.config import fileConfig
import requests
import time, threading
import const
import datetime
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr, formatdate

fileConfig('log.conf')
logger = logging.getLogger(__name__)

result_sample_list = []

# 限制每日最大通知发送量
today_notify = {'date': datetime.datetime.now().strftime("%Y%m%d"), 'count': 0}


# 服务调用测试
def api_invoke(sys_id):
    logger.info('线程[%s]已启动', threading.current_thread().name)
    (svc_name, svc_desc, svc_url, svc_method, svc_request, svc_expect) = get_service_info(sys_id)

    while True:
        # 发起网络请求
        if svc_method == 'GET':
            try:
                response = requests.get(svc_url, timeout=const.REQUEST_TIMEOUT)
                elapsed = float(response.elapsed.microseconds / 1000)
                status = response.ok
            except requests.exceptions.RequestException as e:
                elapsed = -1
                status = False
        elif svc_method == 'POST':
            try:
                response = requests.post(url=svc_url, data=svc_request, timeout=const.REQUEST_TIMEOUT)
                elapsed = float(response.elapsed.microseconds / 1000)
                status = response.ok
            except requests.exceptions.RequestException as e:
                elapsed = -1
                status = False

        logger.info('应用：%s  检测URL：%s  状态：%s  时长：%s', svc_name, svc_url, status, elapsed)

        # 更新样本池
        result_sample_list[sys_id].insert(0, status)
        result_sample_list[sys_id].pop(-1)

        # 休眠
        time.sleep(const.INVOKE_INTERVAL)


# 应用健康度检测
def health_check(sys_id):
    logger.info('线程[%s]已启动', threading.current_thread().name)
    (svc_name, svc_desc, svc_url, svc_method, svc_request, svc_expect) = get_service_info(sys_id)
    re_notify_tag = True  # 通知标识，如果一直失败，则只通知一次

    while True:
        # 统计样本池中的失败个数
        fail_count = 0
        for sample in result_sample_list[sys_id]:
            if not sample:
                fail_count += 1

        # 如果失败数大于阈值则触发告警
        if fail_count >= const.MAX_FAILS:
            logger.info('应用：%s  健康度检测结果：失败  休眠：%s秒', svc_name, const.CHECK_FAIL_INTERVAL)
            if re_notify_tag:
                content = '应用健康度检测失败，请及时核查。服务名：{}'.format(svc_name)
                logger.info('准备发起告警')
                send_notify(content)
                logger.info('告警发送结束')
                # 禁止继续通知
                re_notify_tag = False
            # 失败后长时间休眠
            time.sleep(const.CHECK_FAIL_INTERVAL)
        else:
            logger.info('应用：%s  健康度检测结果：成功，休眠：%s秒', svc_name, const.CHECK_INTERVAL)
            # 恢复通知
            re_notify_tag = True
            # 成功后短时间休眠
            time.sleep(const.CHECK_INTERVAL)


# 多线程执行
def run():
    for i in range(0, len(const.SERVICE_LIST)):
        # 初始化检测结果样本池
        result_sample = [True for x in range(0, const.SAMPLE_SIZE)]
        result_sample_list.append(result_sample)

        thread_invoke = threading.Thread(target=api_invoke, args=(i,),
                                         name='thread_inv_' + const.SERVICE_LIST[i]['TAG'])
        thread_check = threading.Thread(target=health_check, args=(i,),
                                        name='thread_chk_' + const.SERVICE_LIST[i]['TAG'])
        thread_invoke.start()
        thread_check.start()


# 从配置中获取服务信息
def get_service_info(sys_id):
    service_info = const.SERVICE_LIST[sys_id]
    return (
        service_info['NAME'], service_info['DESC'], service_info['URL'],
        service_info['METHOD'], service_info['REQUEST'], service_info['EXPECT']
    )


# 检测每日最大通知数
def check_today_notify():
    nowdate = datetime.datetime.now().strftime("%Y%m%d")
    if today_notify['date'] == nowdate:
        today_notify['count'] += 1
    else:
        today_notify['date'] = nowdate
        today_notify['count'] = 0
    logger.info('今日通知发送量：%s', today_notify['count'])

    if today_notify['count'] >= const.NOTIFY_BREAK_COUNT:
        logger.info('今日通知数量超过阈值，已熔断')
        return False
    else:
        return True


# 格式化地址
def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


# 发送邮件
def send_mail(to_addrs, content):
    msg = MIMEMultipart()
    msg['From'] = _format_addr('NierBot <%s>' % const.MAIL_FROM_ADDR)
    msg['To'] = '%s' % ','.join([_format_addr('<%s>' % to_addr) for to_addr in to_addrs])
    msg['Subject'] = Header(const.MAIL_TITLE, 'utf-8').encode()
    msg['Date'] = formatdate()
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    try:
        server = smtplib.SMTP_SSL(const.MAIL_SMTP_SERVER, 465)
        server.set_debuglevel(1)
        server.login(const.MAIL_FROM_ADDR, const.MAIL_PASSWORD)
        server.sendmail(const.MAIL_FROM_ADDR, to_addrs, msg.as_string())
    except smtplib.SMTPException as e:
        logger.error(e)
        logger.error('邮件发送失败')
    finally:
        server.quit()


# 发送短信
def send_sms(to_numbers, content):
    for mobile in to_numbers:
        sms_url = const.SMS_URL + '?mobile=' + mobile + '&content=' + content
        logger.info('sms_url: %s', sms_url)
        try:
            requests.get(sms_url)
        except:
            logger.error('短信发送失败')


# 发送通知
def send_notify(content):
    # 检测是否已配置禁用通知
    if const.NOTIFY_FLAG:
        # 检测是否已达今日上限
        if check_today_notify():
            if 'MAIL' in const.NOTIFY_TYPE.split('|'):
                logger.info('邮件通知开始...')
                send_mail(const.MAIL_TO_ADDRS, content)
            if 'SMS' in const.NOTIFY_TYPE.split('|'):
                logger.info('短信通知开始...')
                send_sms(const.SMS_TO_NUMBERS, content)
        else:
            logger.info('通知数量已达每日上限')
    else:
        logger.info('邮件与短信通知已禁用')


if __name__ == '__main__':
    run()
