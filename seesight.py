import sys
sys.path.append("lib.bs4")
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import TimeoutException
import chromedriver_binary
import pandas as pd
import os
from tqdm import tqdm
from retrying import retry
import datetime as dt

dir_org = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_org+"\\output") #作業フォルダの移動

###############################################################
#---------------------- setting ------------------------------
###############################################################

### ログイン用の情報
URL = "https://kankouyohou.com/omotenashi-web/login"
UserID = ""
PW = ""

### 取得時期の始期と終期
sdate = dt.datetime.strptime("2018-01-01", "%Y-%m-%d") #始期
edate = dt.datetime.strptime("2020-03-31", "%Y-%m-%d") #終期
date_diff = (edate-sdate).days
date_list = [sdate+dt.timedelta(days=i) for i in range(date_diff+1)]

### 宿泊客が0の地域・日次
skip_list = ["岩手県20200428", "秋田県20200506", "山形県20200423", "山形県20200424", "山形県20200429",
             "山形県20200502", "山形県20200505", "山形県20200510", "山形県20200522", "福島県20200428",
             "福島県20200517", "茨城県20200426", "茨城県20200529", "埼玉県20200424", "埼玉県20200426",
             "埼玉県20200525", "福井県20200423", "福井県20200424", "福井県20200507", "福井県20200509",
             "福井県20200515", "福井県20200518", "福井県20200521", "福井県20200522", "福井県20200529",
             "福井県20200530", "福井県20200531", "福井県20200602", "奈良県20200414", "奈良県20200420",
             "奈良県20200522", "奈良県20200524", "奈良県20200526", "奈良県20200531", "徳島県20200604",
             "和歌山県20200506", "和歌山県20200512", "鳥取県20200423", "鳥取県20200424", "鳥取県20200426",
             "鳥取県20200427", "鳥取県20200428", "鳥取県20200429", "鳥取県20200430", "鳥取県20200527",
             "鳥取県20200528", "鳥取県20200529", "鳥取県20200531", "徳島県20200414", "徳島県20200417",
             "徳島県20200419", "徳島県20200421", "徳島県20200422", "徳島県20200423", "徳島県20200424",
             "徳島県20200427", "徳島県20200428", "徳島県20200430", "徳島県20200507", "徳島県20200508",
             "徳島県20200524", "徳島県20200525", "香川県20200421", "香川県20200426", "香川県20200427",
             "香川県20200429", "香川県20200430", "香川県20200504", "香川県20200505", "香川県20200511",
             "香川県20200520", "香川県20200521", "香川県20200522", "香川県20200524", "香川県20200527",
             "香川県20200528", "香川県20200531", "高知県20200418", "高知県20200419", "高知県20200421",
             "高知県20200422", "高知県20200424", "高知県20200501", "高知県20200813", "佐賀県20200427",
             "佐賀県20200429", "佐賀県20200430", "佐賀県20200530", "佐賀県20200531", "大分県20200531",
             "宮崎県20200501"]

### アクセス確認のための最大待機時間
seconds = 50

### 地域情報
region_list = ["長野県",
               "岐阜県","静岡県","愛知県","三重県","滋賀県",
               "京都府","大阪府","兵庫県","奈良県","和歌山県",
               "鳥取県","島根県","岡山県","広島県","山口県",
               "徳島県","香川県","愛媛県","高知県","福岡県",
               "佐賀県","長崎県","熊本県","大分県","宮崎県",
               "鹿児島県","沖縄県"]

"""
region_list = ["北海道","青森県","岩手県","宮城県","秋田県",
               "山形県","福島県","茨城県","栃木県","群馬県",
               "埼玉県","千葉県","東京都","神奈川県","新潟県",
               "富山県","石川県","福井県","山梨県","長野県",
               "岐阜県","静岡県","愛知県","三重県","滋賀県",
               "京都府","大阪府","兵庫県","奈良県","和歌山県",
               "鳥取県","島根県","岡山県","広島県","山口県",
               "徳島県","香川県","愛媛県","高知県","福岡県",
               "佐賀県","長崎県","熊本県","大分県","宮崎県",
               "鹿児島県","沖縄県"]
"""

###############################################################
#---------------------- xpath_setting -------------------------
###############################################################

### クロス表の表示情報
table_index_name = "居住都道府県"
table_columns_name = "年齢層"
table_cols_head = ["居住都道府県","合計"]
table_cols_candidate = ["不明","未成年","若年層","中年層","老年層"]


### 前月の日数_１月ずれていることに注意
pre_month_days_dic   = { "1":31,  "2":31, "3":28, "4":31,  "5":30,
                         "6":31,  "7":30, "8":31, "9":31, "10":30,
                         "11":31, "12":30}
# うるう年用
pre_month_days_dic_l = { "1":31,  "2":31, "3":29, "4":31,  "5":30,
                         "6":31,  "7":30, "8":31, "9":31, "10":30,
                        "11":31, "12":30}

### ログイン用のxpath
login_xpath_UserID = "/html/body/div/div/div/div[2]/div/form/div[1]/div/input"
login_xpath_PW     = "/html/body/div/div/div/div[2]/div/form/div[2]/div/input"
login_xpath_button = "/html/body/div/div/div/div[2]/div/form/p/button"

### クロス表の表示変更用のxpath
menu_cross           = "/html/body/div/form[1]/nav/div[2]/ul/li[3]/ul/li[2]/a"
table_index          = "/html/body/div/form[1]/div/div/div/div/div/div[1]/div[2]/div[1]/ul/li[2]/select"
table_columns        = "/html/body/div/form[1]/div/div/div/div/div/div[1]/div[2]/div[1]/ul/li[5]/select"
button_cross_collect = "/html/body/div/form[1]/div/div/div/div/div/div[1]/div[2]/div[1]/ul/li[7]/a"
button_cross_est     = "/html/body/div/form[1]/div/div/div/div/div/div[1]/div[2]/div[2]/div/div[2]/a[2]"
table_display_check  = "/html/body/div/form[1]/div/div/div/div/div/div[1]/div[2]/div[4]/div[1]/table/tbody/tr[1]/td[2]"

### 地域変更用のxpath
region_button          = "/html/body/div/form[1]/nav/div[1]/div[1]/div[4]/div/div[2]/a"
region_select_combobox = "/html/body/div[1]/form[1]/nav/div[1]/div[3]/div/div/div[2]/div[1]/select[1]"
region_update_button   = "/html/body/div[1]/form[1]/nav/div[1]/div[3]/div/div/div[3]/button"
region_display_check   = "/html/body/div/form[1]/nav/div[1]/div[1]/div[4]/div/div[2]/span[2]"

### 設定変更用のxpath
setting_button        = "/html/body/div/form[1]/nav/div[1]/div[1]/div[2]/ul/li[3]/a"
setting_move_botton   = "/html/body/div/form[1]/nav/div[1]/div[1]/div[2]/ul/li[3]/ul/li[2]/a"
register_info         = "/html/body/div/form[1]/div/div/div/div[1]/div[2]/ul/li[2]/a"
init_region_combobox  = "/html/body/div/form[1]/div/div/div/div[2]/div/div/div[2]/div/div/div[9]/div/select[1]"
setting_update_button = "/html/body/div/form[1]/div/div/div/div[2]/div/div/div[2]/div/div/div[10]/input"

### 表示期間変更用のxpath
period_form_button   = "/html/body/div/form[1]/nav/div[1]/div[1]/div[4]/div/div[1]/div/a"
period_from_button   = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[2]/div/button[1]"
period_to_button     = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[2]/div/button[2]"
period_mm_button     = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[2]/div/ul/li/div/table/thead/tr[1]/th[2]/button"
period_yy_button     = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[2]/div/ul/li/div/table/thead/tr/th[2]/button"
period_update_button = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[3]/button"

yy_xpath_base = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[2]/div/ul/li/div/table/tbody/"
yy_xpath_dict = {"2013":yy_xpath_base+"tr[3]/td[3]/button",
                 "2014":yy_xpath_base+"tr[3]/td[4]/button",
                 "2015":yy_xpath_base+"tr[3]/td[5]/button",
                 "2016":yy_xpath_base+"tr[4]/td[1]/button",
                 "2017":yy_xpath_base+"tr[4]/td[2]/button",
                 "2018":yy_xpath_base+"tr[4]/td[3]/button",
                 "2019":yy_xpath_base+"tr[4]/td[4]/button",
                 "2020":yy_xpath_base+"tr[4]/td[5]/button"}
mm_xpath_base = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[2]/div/ul/li/div/table/tbody/"
mm_xpath_dict = { "1":mm_xpath_base+"tr[1]/td[1]/button",
                  "2":mm_xpath_base+"tr[1]/td[2]/button",
                  "3":mm_xpath_base+"tr[1]/td[3]/button",
                  "4":mm_xpath_base+"tr[2]/td[1]/button",
                  "5":mm_xpath_base+"tr[2]/td[2]/button",
                  "6":mm_xpath_base+"tr[2]/td[3]/button",
                  "7":mm_xpath_base+"tr[3]/td[1]/button",
                  "8":mm_xpath_base+"tr[3]/td[2]/button",
                  "9":mm_xpath_base+"tr[3]/td[3]/button",
                 "10":mm_xpath_base+"tr[4]/td[1]/button",
                 "11":mm_xpath_base+"tr[4]/td[2]/button",
                 "12":mm_xpath_base+"tr[4]/td[3]/button"}
dd_xpath_base = "/html/body/div[1]/form[1]/nav/div[1]/div[2]/div/div/div[2]/div/ul/li/div/table/tbody/"
dd_xpath_dict = { "1":dd_xpath_base+"tr[1]/td[2]/button",
                  "2":dd_xpath_base+"tr[1]/td[3]/button",
                  "3":dd_xpath_base+"tr[1]/td[4]/button",
                  "4":dd_xpath_base+"tr[1]/td[5]/button",
                  "5":dd_xpath_base+"tr[1]/td[6]/button",
                  "6":dd_xpath_base+"tr[1]/td[7]/button",
                  "7":dd_xpath_base+"tr[1]/td[8]/button",
                  "8":dd_xpath_base+"tr[2]/td[2]/button",
                  "9":dd_xpath_base+"tr[2]/td[3]/button",
                 "10":dd_xpath_base+"tr[2]/td[4]/button",
                 "11":dd_xpath_base+"tr[2]/td[5]/button",
                 "12":dd_xpath_base+"tr[2]/td[6]/button",
                 "13":dd_xpath_base+"tr[2]/td[7]/button",
                 "14":dd_xpath_base+"tr[2]/td[8]/button",
                 "15":dd_xpath_base+"tr[3]/td[2]/button",
                 "16":dd_xpath_base+"tr[3]/td[3]/button",
                 "17":dd_xpath_base+"tr[3]/td[4]/button",
                 "18":dd_xpath_base+"tr[3]/td[5]/button",
                 "19":dd_xpath_base+"tr[3]/td[6]/button",
                 "20":dd_xpath_base+"tr[3]/td[7]/button",
                 "21":dd_xpath_base+"tr[3]/td[8]/button",
                 "22":dd_xpath_base+"tr[4]/td[2]/button",
                 "23":dd_xpath_base+"tr[4]/td[3]/button",
                 "24":dd_xpath_base+"tr[4]/td[4]/button",
                 "25":dd_xpath_base+"tr[4]/td[5]/button",
                 "26":dd_xpath_base+"tr[4]/td[6]/button",
                 "27":dd_xpath_base+"tr[4]/td[7]/button",
                 "28":dd_xpath_base+"tr[4]/td[8]/button",
                 "29":dd_xpath_base+"tr[5]/td[2]/button",
                 "30":dd_xpath_base+"tr[5]/td[3]/button",
                 "31":dd_xpath_base+"tr[5]/td[4]/button",
                 "32":dd_xpath_base+"tr[5]/td[5]/button",
                 "33":dd_xpath_base+"tr[5]/td[6]/button",
                 "34":dd_xpath_base+"tr[5]/td[7]/button",
                 "35":dd_xpath_base+"tr[5]/td[8]/button",
                 "36":dd_xpath_base+"tr[6]/td[2]/button",
                 "37":dd_xpath_base+"tr[6]/td[3]/button",
                 "38":dd_xpath_base+"tr[6]/td[4]/button",
                 "39":dd_xpath_base+"tr[6]/td[5]/button",
                 "40":dd_xpath_base+"tr[6]/td[6]/button",
                 "41":dd_xpath_base+"tr[6]/td[7]/button",
                 "42":dd_xpath_base+"tr[6]/td[8]/button"}

###############################################################
#---------------------- function ------------------------------
###############################################################

# driver上でxpathが選択できるまで最大sec秒待つ
@retry(stop_max_attempt_number=5)
def wait_loading(driver, sec, xpath):
  WebDriverWait(driver, sec).until(EC.presence_of_element_located((By.XPATH, xpath)))

#ボタンの出現を確認後にクリック
def wait_and_click(driver, sec, xpath):
  wait_loading(driver, sec, xpath)
  driver.find_element_by_xpath(xpath).click()

#欲しい日付の位置を取得する
#(カレンダー表示になっているので、年・月ごとに対象日の位置が異なる)
def search_dd_position(driver, sec, dd_xpath_dict, dd, pre_month_days):
  #日付通りの場合の位置を選んだ場合に帰ってくる日にちにを取得
  tmp_dd_xpath = dd_xpath_dict[dd]
  wait_loading(driver, sec, tmp_dd_xpath)
  init_num = driver.find_element_by_xpath(tmp_dd_xpath).text
  diff = int(dd)-int(init_num) # 欲しい日と日付の差分
  ### 押したい日と返りの差分によって調整してあげる
  if diff > 0:
    adj_key = int(dd)+diff
  elif diff < 0:
    adj_key = 2*int(dd)+(pre_month_days-int(init_num))
  else:
    adj_key = int(dd)
  ### 取得日の確認
  adj_xpath = dd_xpath_dict[str(adj_key)]
  if int(driver.find_element_by_xpath(adj_xpath).text) == int(dd):
    return adj_xpath #望みの位置となるxpathを返す
  else:
    print("日付が一致しないのでエラー処理")
    raise Exception

###############################################################
#---------------------- main routine --------------------------
###############################################################

### ブラウザの立ち上げ
options = Options()
options.set_headless(True) # Headlessモードを有効
driver = webdriver.Chrome(chrome_options=options)
driver.set_window_size('1200', '1000') #ブラウザを適当に大きく
driver.get(URL) #ブラウザでアクセスする

### ログイン
driver.find_element_by_xpath(login_xpath_UserID).send_keys(UserID)
driver.find_element_by_xpath(login_xpath_PW).send_keys(PW)
wait_and_click(driver, seconds, login_xpath_button)
print("ログイン完了")

for region_name in region_list:
  print(region_name)

  ### 地域情報の更新
  wait_and_click(driver, seconds, setting_button) #設定画面への遷移1
  wait_and_click(driver, seconds, setting_move_botton) #設定画面への遷移2
  wait_and_click(driver, seconds, register_info) #登録情報変更画面への遷移
  wait_loading(driver, seconds, init_region_combobox) #選択できるまで待機
  Select(driver.find_element_by_xpath(init_region_combobox)).select_by_visible_text(region_name) #地域の選択
  driver.implicitly_wait(10) # 早すぎて、地域の変更が反映されないから、ここでちょっと待つ
  wait_and_click(driver, seconds, setting_update_button) #設定の更新
  driver.implicitly_wait(10) # 早すぎて、地域の変更が反映されないから、ここでちょっと待つ

  ### 地域情報の更新のために再起動
  driver.delete_all_cookies() #全てのクッキーを削除
  driver.quit()
  options = Options()
  options.set_headless(True) # Headlessモードを有効
  driver = webdriver.Chrome(chrome_options=options)
  driver.set_window_size('1200', '1000') #ブラウザを適当に大きく
  driver.get(URL) #ブラウザでアクセスする

  ### ログイン
  driver.find_element_by_xpath(login_xpath_UserID).send_keys(UserID)
  driver.find_element_by_xpath(login_xpath_PW).send_keys(PW)
  wait_and_click(driver, seconds, login_xpath_button)

  ### 地域情報の更新
  wait_and_click(driver, seconds, setting_button) #設定画面への遷移1
  wait_and_click(driver, seconds, setting_move_botton) #設定画面への遷移2
  wait_and_click(driver, seconds, register_info) #登録情報変更画面への遷移
  wait_loading(driver, seconds, init_region_combobox) #選択できるまで待機
  Select(driver.find_element_by_xpath(init_region_combobox)).select_by_visible_text(region_name) #地域の選択
  driver.implicitly_wait(10) # 早すぎて、地域の変更が反映されないから、ここでちょっと待つ
  wait_and_click(driver, seconds, setting_update_button) #設定の更新
  driver.implicitly_wait(10) # 早すぎて、地域の変更が反映されないから、ここでちょっと待つ

  ### 地域情報の更新のために再起動
  driver.delete_all_cookies() #全てのクッキーを削除
  driver.quit()
  options = Options()
  options.set_headless(True) # Headlessモードを有効
  driver = webdriver.Chrome(chrome_options=options)
  driver.set_window_size('1200', '1000') #ブラウザを適当に大きく
  driver.get(URL) #ブラウザでアクセスする

  ### ログイン
  driver.find_element_by_xpath(login_xpath_UserID).send_keys(UserID)
  driver.find_element_by_xpath(login_xpath_PW).send_keys(PW)
  wait_and_click(driver, seconds, login_xpath_button)

  ### クロス集計への遷移と集計対象の調整
  wait_and_click(driver, seconds, menu_cross) #クロス集計への遷移
  wait_loading(driver, seconds, table_index) #選択できるまで待機
  Select(driver.find_element_by_xpath(table_index)).select_by_visible_text(table_index_name) #クロス集計の行の選択
  Select(driver.find_element_by_xpath(table_columns)).select_by_visible_text(table_columns_name) #クロス集計の列の選択

  for yymmdd in tqdm(date_list):
    yy, mm, dd = str(yymmdd.year), str(yymmdd.month), str(yymmdd.day)
    if region_name+yy+mm.zfill(2)+dd.zfill(2) in skip_list:
     ###出力
     tmp = pd.DataFrame()
     tmp.to_csv(region_name+"_"+yy+"_"+mm.zfill(2)+"_"+dd.zfill(2)+".csv", encoding="cp932")
    else:
      ### 集計期間の変更
      wait_and_click(driver, seconds, period_form_button) #期間変更のボタンを押す
      # xpathの取得
      yy_xpath = yy_xpath_dict[yy]
      mm_xpath = mm_xpath_dict[mm]
      #始期の変更
      wait_and_click(driver, seconds, period_from_button) #始期変更のボタンを押す
      wait_and_click(driver, seconds, period_mm_button) #月の選択画面へ遷移
      wait_and_click(driver, seconds, period_yy_button) #年の選択画面へ遷移
      wait_and_click(driver, seconds, yy_xpath) #年の選択
      wait_and_click(driver, seconds, mm_xpath) #月の選択
      # xpathの取得(日のみ)
      if int(yy)%4==0 and int(int(mm)-1)==2: #うるう年調整
        dd_xpath = search_dd_position(driver, seconds, dd_xpath_dict, dd, pre_month_days_dic_l[mm])
      else:
        dd_xpath = search_dd_position(driver, seconds, dd_xpath_dict, dd, pre_month_days_dic[mm])
      wait_and_click(driver, seconds, dd_xpath) #日の選択
      #終期の変更
      wait_and_click(driver, seconds, period_to_button) #終期変更のボタンを押す
      wait_and_click(driver, seconds, period_mm_button) #月の選択画面へ遷移
      wait_and_click(driver, seconds, period_yy_button) #年の選択画面へ遷移
      wait_and_click(driver, seconds, yy_xpath) #年の選択
      wait_and_click(driver, seconds, mm_xpath) #月の選択
      wait_and_click(driver, seconds, dd_xpath) #日の選択
      #期間の変更
      wait_and_click(driver, seconds, period_update_button)

      #地域変更が維持されているかここでチェック
      wait_loading(driver, seconds, region_display_check)
      if not region_name == driver.find_element_by_xpath(region_display_check).text:
        print("地域変更が反映されてない")
        raise Exception

      ### クロス表からのデータ抽出
      wait_and_click(driver, seconds, button_cross_collect) #クロス表で対象を集計
      wait_and_click(driver, seconds, button_cross_est) #クロス表で比率じゃなくて推計値を表示対象にする
      wait_loading(driver, seconds, table_display_check) #クロス表の表示確認
      soup = BeautifulSoup(driver.page_source, "lxml") #現在の表示画面のHTMLを取得
      table = pd.read_html(str(soup.find("div", class_="table-responsive pre-scrollable")))[0] #DataFrame化
      #列名の調整
      col_checker = "".join(["".join(i) for i in list(table.columns)])
      table_cols = table_cols_head + [ i for i in table_cols_candidate if i in col_checker ]
      table.columns = table_cols
      #行の調整
      table = table.set_index("居住都道府県")

      ###出力
      table.to_csv(region_name+"_"+yy+"_"+mm.zfill(2)+"_"+dd.zfill(2)+".csv", encoding="cp932")
