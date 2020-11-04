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
empty_df_list = [pd.DataFrame(index=date_list) for _ in region_list]

###############################################################
#---------------------- main_routine---------------------------
###############################################################

for attr in attribute_list:
  output_dict = dict(zip(region_list, empty_df_list))
  for to_region in tqdm(region_list):
    df = pd.read_csv(".\\to_analysis\\"+to_region+"_to_"+attr+".csv", engine="python", index_col=0)
    for from_region in region_list:
      tmp = output_dict[from_region]
      target = df.loc[:,[from_region]]
      target.columns = [to_region]
      output_dict[from_region] = pd.concat([tmp, target], axis=1, sort=False)

  for from_region in region_list:
    output = output_dict[from_region]
    output = output.loc[:, region_list]
    output.to_csv(".\\from_analysis\\"+from_region+"_from_"+attr+".csv", encoding="cp932")
