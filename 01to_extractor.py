import os
import pandas as pd
from pandas.io.common import EmptyDataError
from tqdm import tqdm
import datetime as dt

dir_org = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_org) #作業フォルダの移動

###############################################################
#---------------------- setting ------------------------------
###############################################################

### 取得時期の始期と終期
sdate = dt.datetime.strptime("2018-01-01", "%Y-%m-%d") #始期
edate = dt.datetime.strptime("2020-10-23", "%Y-%m-%d") #終期
date_diff = (edate-sdate).days
date_list = [sdate+dt.timedelta(days=i) for i in range(date_diff+1)]

### 地域情報
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

### 属性情報
attribute_list = ["合計", "不明","未成年","若年層","中年層","老年層"]

### 出力用の前準備
empty_df = pd.DataFrame( [ 0 for _ in region_list], index=region_list).T
empty_df_list = [pd.DataFrame(columns=region_list) for _ in attribute_list]

###############################################################
#---------------------- main_routine---------------------------
###############################################################

for region_name in region_list:
  print(region_name)
  output_dict = dict(zip(attribute_list, empty_df_list))
  for yymmdd in tqdm(date_list):
    yy, mm, dd = str(yymmdd.year), str(yymmdd.month), str(yymmdd.day)
    yy_mm_dd = yy+"_"+mm.zfill(2)+"_"+dd.zfill(2)
    try:
      df = pd.read_csv(".\\output\\"+region_name+"_"+yy_mm_dd+".csv", engine="python", index_col=0)
    except EmptyDataError:
      df = empty_df.copy()
    for attr in attribute_list:
      tmp = output_dict[attr]
      try:
        output_dict[attr] = pd.concat([tmp, df.loc[:,[attr]].T], axis=0, sort=False)
      except KeyError:
        output_dict[attr] = pd.concat([tmp, empty_df], axis=0, sort=False)

  for attr in attribute_list:
    output = output_dict[attr]
    output.index = date_list
    output = output.loc[:, region_list]
    output.to_csv(".\\to_analysis\\"+region_name+"_to_"+attr+".csv", encoding="cp932")
