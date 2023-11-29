# 自动获取终端详细参数
## 一、目标源：
###   中关村（https://detail.zol.com.cn/）   +    京东
## 二、环境要求：
    #支持selenium版本 >= 4.0
    pip install selenium
    pip install lxml

    # 下载谷歌浏览器驱动
    http://chromedriver.storage.googleapis.com/index.html
    # 注意：chromedriver版本要仅小于或等于你谷歌浏览器目前的版本
    # 记住你解压后所在的位置（例如：D:\chromedriver.exe）
## 三、参数：
    savePath：输出文件的路径
    browserDriverPath：谷歌驱动所在路径（D:\chromedriver）
    mode：要爬取的终端类型
      主要对以下终端信息爬取：
        mode:0-->手机
        mode:1-->笔记本电脑
        mode:2-->平板电脑
        mode:3-->电视
        mode:4-->路由器
        mode:5-->监控摄像机
        mode:6-->电视盒
        mode:7-->智能门锁
        mode:8-->智能手表
        mode:9-->台式电脑
        mode:10-->智能音箱
    _startPage：开始爬取的页码
    _endPage：结束爬取的页码。默认爬取所有
