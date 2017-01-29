#!/opt/anaconda3/bin/python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import *

from bs4 import BeautifulSoup

import sys
import time
import re

driver = webdriver.PhantomJS()
driver.get("https://www.kakeibo.tepco.co.jp/dk/aut/login/")

# ID/PASS
ID   = ""
PASS = ""
if len(sys.argv) > 1:
    MINDATE = sys.argv[1]
else:
    MINDATE = ""

WEEKDAY_LIST = ["月", "火", "水","木","金","土","日"]

print("[START] Retrieve Tepco Data...")
print("[INFO] MINDATE : %s" % MINDATE)

# 表示している日付のデータ取得
def getValueOfDate(driver, minDate, dataList):
    # テーブルヘッダから日付を取得
    headTable = driver.find_element_by_class_name("graph_head_table")
    targetDate = driver.find_elements_by_tag_name("td")[1].text[0:10]

    if minDate != "":
        if minDate > targetDate:
            return None

    # 進行状況の出力
    print("[INFO] データ取得中... (%s)" % targetDate)
    

    # ページソースから電気使用量を取得
    data = driver.page_source

    # Javascriptの該当箇所から数値の配列を取得する。
    ptn = r"var items = \[\[[^0-9; ]+,([0-9\. ,]+)\]\];"
    matchTxt = re.search(ptn, data)
    retData = (targetDate + "," + matchTxt.group(1))
 
    # 前日のデータ表示
    driver.find_element_by_id("doPrevious").click()

    # データの追加
    dataList.append(retData)

    return True

try:
    # ID/Pass/Loginボタンを取得	
    idObj = driver.find_element_by_id("idId")
    idPass = driver.find_element_by_id("idPassword")
    loginBtn = driver.find_element_by_id("idLogin")

    # ID/Passを入力
    idObj.clear()
    idObj.send_keys(ID)
    idPass.clear()
    idPass.send_keys(PASS)

    # Loginボタンを押下
    loginBtn.click()

    # 画面遷移(メイン画面->電気量表示画面)
    driver.find_element_by_id("idNotEmptyImg_contents01.jpg").click()
    # 電気量表示画面->時間別電気量表示画面
    driver.find_element_by_id("bt_time_view.jpg").click()

    # ヘッダ出力
    header = "Date,"
    for hh in range(24):
        for mm in [0, 30]:
            header = header + "%02d:%02d," % (hh, mm)
    header = header + "END"

    # 各日のデータ取得
    dataList = []
    try:
        while getValueOfDate(driver, MINDATE, dataList):
            pass
    except:
        pass

    print("[INFO] データ取得完了")

    # データ出力
    minData = dataList[-1].split(",")[0].replace("/", "")
    maxData = dataList[0].split(",")[0].replace("/", "")

    fname = "Tepco-Data_%s-%s.csv" % ( minData, maxData )
    f = open(fname, "w")
    f.write( header + "\n")
    for data in sorted(dataList):
        f.write( data.replace(" ", "") + "\n" )
    f.close()

finally:
    driver.close()
