import csv
import os
import random
import requests
import time
from lxml import etree
from selenium.webdriver.common.by import By
from paramsters import __url__, __headers__
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GetModelParameter(object):
    """
    :parameter
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
    """
    __type__ = ['cell_phone', 'notebook', 'tablepc', 'digital_tv', 'wireless_router', 'camera_equipment', 'hd-player',
                'doorbell', 'GPSwatch', 'desktop_pc', 'Intelligentvoiceassistant']

    def __init__(self, savePath, mode, browserDriverPath):
        self.__savePath = savePath
        self.__mode = mode
        self.__type = GetModelParameter.__type__[mode]
        self.__browserDriverPath = browserDriverPath
        self.__browser = None

    def __getTerminalId(self, page):
        # 获取id
        url = __url__[self.__mode].format(page)
        # 发送 GET 请求获取品牌页面
        self.__browser.get(url)
        # time.sleep(2)

        if self.__mode in [2, 4, 5]:
            undo_ids = self.__browser.find_elements(By.XPATH, '//div[@class="list-item item-one clearfix"]//h3/a | //div[@class="list-item clearfix"]//h3/a')
        else:
            undo_ids = self.__browser.find_elements(By.XPATH, '//ul[@id="J_PicMode"]/li/h3/a')

        return undo_ids

    def __to_csv(self, terminalInfo):
        _id, _manufacturer, _ue_name, _ue_version = terminalInfo.get('id'), terminalInfo.get('brand'), terminalInfo.get(
            'ue_name'), terminalInfo.get('ue_version')

        _ue_model = terminalInfo.get('入网型号_jd') if terminalInfo.get('入网型号_jd') else terminalInfo.get('产品型号')

        _reference_price = terminalInfo.get('reference_price')
        _details = terminalInfo.get("detail_parameters")
        _details_jd = terminalInfo.get("detail_parameters_jd")
        _ue_type = '电视盒' if self.__mode == 6 else terminalInfo.get('type')
        _listing_date = terminalInfo.get('上市日期') if self.__mode == 0 else terminalInfo.get('上市时间')

        _net_type = terminalInfo.get('网络类型')
        conn_net = terminalInfo.get('通讯网络')
        if self.__mode == 0 and _net_type:
            _net_type = _net_type.split('，')[0]
        if self.__mode == 8 and conn_net:
            _net_type = conn_net

        cc_os = terminalInfo.get('出厂系统内核')
        cz_os = terminalInfo.get('操作系统')
        pp_os = terminalInfo.get('匹配系统')
        if cc_os:
            _ue_os = cc_os
        elif cz_os:
            _ue_os = cz_os
        else:
            _ue_os = pp_os

        row_data = (
            _id, _ue_model,  _ue_type, _manufacturer, _ue_name, _ue_version, _ue_os, _listing_date, _net_type,
            _reference_price, _details, _details_jd)
        header = (
            'id', 'ue_model', 'ue_type', 'manufacturer', 'ue_name', 'ue_version', 'ue_os', 'listing_date', 'net_type',
            'reference_price', 'detail_parameters', 'detail_parameters_jd')

        flag = os.path.exists(self.__savePath)
        with open(self.__savePath, mode='at', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if not flag:
                writer.writerow(header)
            writer.writerow(row_data)
        print(row_data)

    @staticmethod
    def __getJdDetails(divs, terminalInfo, detailInfo_jd):
        for div in divs:
            partition = dict()
            hd = div.find_element(By.XPATH, './h3').get_attribute("innerText")
            dls = div.find_elements(By.XPATH, './dl/dl')
            for dl in dls:
                k = dl.find_element(By.XPATH, './dt').get_attribute("innerText")
                try:
                    v = dl.find_elements(By.XPATH, './dd')[-1].get_attribute("innerText")
                except:
                    v = ''
                terminalInfo[k + '_jd'] = v
                partition[k] = v
            detailInfo_jd[hd] = partition
        terminalInfo["detail_parameters_jd"] = detailInfo_jd

    @staticmethod
    def __getZtoDetails(id, terminalInfo, detailInfo):
        url2 = "https://detail.zol.com.cn/{0}/{1}/param.shtml".format(id + 1, id)
        resp2 = requests.get(url2, headers=random.choice(__headers__))
        if resp2.status_code != 200:
            print('请求失败！')
            return
        tree2 = etree.HTML(resp2.text)
        tables = tree2.xpath("//div[@class='detailed-parameters']//table")
        for table in tables:
            partition = dict()
            trs = table.xpath(".//tr")
            if len(trs) < 3:
                continue
            tr_hd, trs = trs[0], trs[1:]
            hd = tr_hd.xpath("./td/text()")[0]
            for tr in trs:
                k = tr.xpath("./th/span/text() | ./th/a/text()")[0]
                try:
                    _v1 = tr.xpath("./td/span/text() | ./td/span/a/text()")
                    _v = [e.replace('>', '').strip() for e in _v1 if e]
                    v = "".join(_v)
                except:
                    v = ''
                terminalInfo[k] = v
                partition[k] = v
            detailInfo[hd] = partition
        terminalInfo["detail_parameters"] = detailInfo

    def __getTerminalDetails(self, href):
        _terminalInfo = dict()
        _detailInfo = dict()
        _detailInfo_jd = dict()
        # 获取参数
        id = href.get_attribute('href').split('/index')[1][:-6]
        self.__browser.execute_script("arguments[0].click();", href)
        # time.sleep(2)
        # 切换为当前工作的窗口
        self.__browser.switch_to.window(self.__browser.window_handles[-1])
        try:
            _terminalInfo['id'] = id
            _terminalInfo['type'] = WebDriverWait(self.__browser, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="breadcrumb"]/a[2]'))).text
            _terminalInfo['brand'] = self.__browser.find_element(By.XPATH, '//a[@id="_j_breadcrumb"]').text[:-len(_terminalInfo['type'])]
            full_name = self.__browser.find_element(By.XPATH, '//h1').text.replace(' (', '（').replace('(', '（').split('（')
            _terminalInfo['ue_name'] = full_name[0]
            if len(full_name) == 2:
                _terminalInfo['ue_version'] = full_name[1].replace('）', '').replace(')', '')
            else:
                _terminalInfo['ue_version'] = ''
            _terminalInfo['reference_price'] = self.__browser.find_element(By.XPATH, '//*[@class="price-type"] | //li[@class="b2c-jd"]/a[@class="price"]').text.replace('￥', '')
        except Exception as e:
            print('zto->%s' % e)

        # 修改原有属性
        jd_xpath = '//a[@class="select-hd _j_price_jd"] | //li[@class="b2c-jd"]/a[@class="price"] | //li[@class="b2c-jd"]/a | //a[@class="b2c-link"]'
        try:
            jd = self.__browser.find_element(By.XPATH, jd_xpath)
        except Exception as e:
            print('jd->%s' % e)
            pass
        else:
            self.__browser.execute_script("arguments[0].target='_self'", jd)
            # 进入京东
            # second = random.uniform(1.0, 10.0)
            # print('%s秒后进入京东' % round(second, 2))
            # time.sleep(second)
            self.__browser.find_element(By.XPATH, jd_xpath).click()
            self.__browser.switch_to.window(self.__browser.window_handles[-1])
            _divs = self.__browser.find_elements(By.XPATH, '//div[@class="tab-con"]/div[2]/div[@class="Ptable"]/div')
            # 获取京东详细参数
            self.__getJdDetails(_divs, _terminalInfo, _detailInfo_jd)

        # 获取中关村详细参数
        self.__getZtoDetails(eval(id), _terminalInfo, _detailInfo)

        self.__to_csv(_terminalInfo)

        # 关闭当前子窗口,回到主窗口
        self.__browser.close()
        self.__browser.switch_to.window(self.__browser.window_handles[-1])

    def __creatDriver(self):
        # 驱动配置
        opt = ChromeOptions()
        # ---设置不打开浏览器可视化页面---
        opt.add_argument("--headless")
        opt.add_argument("--disable-gpu")
        # --
        opt.add_experimental_option('excludeSwitches', ['enable-automation'])
        opt.add_experimental_option("detach", True)
        opt.add_argument("--disable-blink-features=AutomationControlled")
        service = Service(executable_path=self.__browserDriverPath)
        # -----实列化一个Chrome对象-----
        _browser = Chrome(options=opt, service=service)
        _browser.delete_all_cookies()
        _browser.implicitly_wait(10)
        # 解决特征识别的代码
        _browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                      get: () => undefined
                    })
                  """
        })
        return _browser

    def main(self, _startPage=1, _endPage=None):
        if _endPage:
            while _startPage <= _endPage:
                self.__browser = self.__creatDriver()
                print("获取第{}页中……".format(_startPage))
                undo_ids = self.__getTerminalId(_startPage)
                if not undo_ids:
                    break
                print("第{}页已经准备就绪！".format(_startPage))
                for undo_id in undo_ids:
                    self.__getTerminalDetails(undo_id)
                _startPage += 1
                self.__browser.quit()
            print("爬取已完成！")
        else:
            while True:
                self.__browser = self.__creatDriver()
                print("获取第{}页中……".format(_startPage))
                undo_ids = self.__getTerminalId(_startPage)
                if not undo_ids:
                    self.__browser.quit()
                    print("爬取已完成！")
                    break
                print("第{}页已经准备就绪！".format(_startPage))
                for undo_id in undo_ids:
                    self.__getTerminalDetails(undo_id)
                _startPage += 1
