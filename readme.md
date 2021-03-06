# tmon
## 简介
tmon - 一个简陋的应用健康度检测系统，基于Python3。  
请注意，这是一个重复的轮子，源于某项目的紧急救火过程中，需要快速搭建一套监控系统实时监控几套后台服务的需求。  
相较于使用现成的开源系统，花时间进行技术选型、部署、修改源码等操作，重写一套系统花费的时间更少，定制性更高。  
本系统不再继续完善，仅供学习目的使用，类以的，有更多更为成熟的开源应用，请自行搜索比较。  

## 功能特性
- 参数可配置化，可同时配置检测多个后台服务  
- 多线程并行检测  
- 支持邮件、短信两种通知方式  
- 防止重复通知机制、每日频繁通知融熔断机制  

## 检测方式及流程
可配置检测多个服务，针对某一个单独的服务，分别启两个线程，一个用于服务调用测试（收集样本），另一个用于健康度检测（裁决）  

服务调用测试线程：
1. 每隔一定时间（默认5秒）向特定的URL发起一次GET或POST请求。
2. 如果请求的返回结果不是HTTP 2XX，或直接请求失败，则向一个FIFO的测试结果样本池（默认20个）中新增一条失败记录，反之增加一条成功记录。

健康度检测线程：
1. 每隔一定时间（默认20秒），统计样本池中失败的次数，如果大于阈值（默认2个），则发起告警通知，并休眠一定时间。反之，认为系统运行正常，不做任何操作，仅休眠一定时间。
2. 告警通知分为短信和邮件两类，参数配置实现。
3. 首先判断今日的通知次数是否大于阈值（10次），如果是，则进行熔化断操作，不予发送。避免每天发送过量的SPAM通知。
4. 然后判断re_notify_tag（每次检测时，如果成功，则re_notify_tag会置为True，反之为False），如果为真才会发送通知。re_notify_tag用于避免系统宕机后，重复发送通知。


## 安装及运行
### venv虚拟环境安装配置
```
sudo pip3 install virtualenv
virtualenv venv
. venv/bin/activate
```

### 第三方依赖安装
```
pip3 install -r requirements.txt

```

### 守护进程启动
```
nohup ./tmon.py 2>&1 &
```