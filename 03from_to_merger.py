import os
import pandas as pd
from tqdm import tqdm
import openpyxl

dir_org = os.path.dirname(os.path.abspath(__file__))
os.chdir(dir_org) #作業フォルダの移動

###############################################################
#---------------------- setting ------------------------------
###############################################################

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

###############################################################
#---------------------- main_routine---------------------------
###############################################################

for region_name in tqdm(region_list):
  ### ファイルの存在有無をしてなければファイルの作成
  if not os.path.exists(".\\from_to_analysis\\"+region_name+".xlsx"):
    wb = openpyxl.Workbook() #ファイルの作成
    wb.create_sheet(title="まとめ") #シートの追加
    wb.remove_sheet(wb.get_sheet_by_name("Sheet")) #初期にできるシートの削除
    wb.save(".\\from_to_analysis\\"+region_name+".xlsx") #ファイルの作成

  ### シート追記用にExcelWriterで開く
  with pd.ExcelWriter(".\\from_to_analysis\\"+region_name+".xlsx",
                      engine="openpyxl", mode="a") as writer:
    for attr in attribute_list:
      df_from = pd.read_csv(".\\from_analysis\\"+region_name+"_from_"+attr+".csv",
                            engine="python", index_col=0)
      df_to   = pd.read_csv(".\\to_analysis\\"+region_name+"_to_"+attr+".csv",
                            engine="python", index_col=0)
      df_from.to_excel(writer, sheet_name="from_"+attr, encoding="cp932")
      df_to.to_excel(writer, sheet_name="to_"+attr, encoding="cp932")
