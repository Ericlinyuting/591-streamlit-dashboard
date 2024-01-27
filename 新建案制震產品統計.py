import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import json
import numpy as np

ALL_data = pd.read_excel("asset/ALL_data.xlsx")
ALL_data.drop("Unnamed: 0",axis=1,inplace=True)
selling_cases = len(ALL_data)
ALL_data["制震宅"]=ALL_data["制震宅"].map({0:False,1:True,None:False})
AST_data = ALL_data[ALL_data["制震宅"]]
NON_AST_data = ALL_data[~ALL_data["制震宅"]]
# 利用json模組，讀入geojson檔案：
# 讀取geojson
with open('asset/mapdata202301070205/COUNTY_MOI_1090820.geojson', encoding='utf8') as response:
    mapGeo = json.load(response)
def Choropleth_Data(df):
     # 利用json模組，讀入geojson檔案：
    # 讀取geojson
    with open('asset/mapdata202301070205/COUNTY_MOI_1090820.geojson', encoding='utf8') as response:
        mapGeo = json.load(response)
    #Choropleth Map資料處理流程
    df["單價"] = pd.to_numeric(df['單價'], errors='coerce')
    df_Price = df[df['單位'] == '萬/坪'].groupby('縣市')['單價'].agg('mean').reset_index()
    df_Price["縣市"] = df_Price["縣市"].str.replace("台", "臺")
    df_Price["單價"] = round(df_Price["單價"],1)

    #此處依據geojson檔案內記載的鄉鎮市區清單資訊，建立一個Pandas表格，待會要將此表做為主表，把價格資料併進來：
    # 依據圖資資料建立鄉鎮市區清單
    country_df = pd.DataFrame.from_dict([i['properties'] for i in mapGeo['features']])
    county_price_table = pd.merge(country_df, df_Price, left_on='COUNTYNAME', right_on='縣市', how='left')
    return county_price_table

def Brand_count(product,AST_data):
    product_data = AST_data[AST_data[product].notna()]
    product_data = product_data[product].str.split(',').explode()# 使用逗號進行拆分，並展平成一維的 Series
    product_data = product_data.str.strip()# 移除空白字元
    SDW_brand_count = product_data.value_counts()
    return SDW_brand_count
# 主要的Streamlit應用程序
def main():
    # Page icon
    # icon = Image.open('asset/page_icon.png')
    #region content region
    st.set_page_config(page_title='新建案制震產品銷售統計', 
                    layout='wide',)
                    # page_icon=icon)

    # 置中標題
    st.markdown("<h1 style='text-align: center;'>新建案制震產品銷售統計</h1>", unsafe_allow_html=True)
    st.markdown("<hr/>", unsafe_allow_html=True)
    #region Dashboard part
    AST_Case_count=len(AST_data)
    st.markdown(f"<h4 style='text-align: start;'>591在售新建案計{selling_cases}案，而制震宅共{AST_Case_count}案(截至2023/12/29)</h4>", unsafe_allow_html=True)
    st.markdown(f"<h5 style='text-align: start;'>制震宅約佔{round(AST_Case_count/selling_cases*100)}%，其中明確指定所使用之制震產品建案統計如下：", unsafe_allow_html=True)
    Product1,Product2,Product3 = st.columns(3)
    with Product1:
        st.markdown("**阻尼器**")
        try:
            FVD_count=len(AST_data[AST_data["阻尼器"].notna()])
        except:
            FVD_count=0
        FVD = st.markdown(f"<h1 style='text-align:center;color:red'>{FVD_count}案</h1>", unsafe_allow_html=True)
    with Product2:
        st.markdown("**制震壁**")
        try:
            SDW_count=len(AST_data[AST_data["制震壁"].notna()])
        except:
            SDW_count=0
        SDW = st.markdown(f"<h1 style='text-align:center;color:red'>{SDW_count}案</h1>", unsafe_allow_html=True)
    with Product3:
        st.markdown("**消能斜撐**")
        try:
            SDB_count=len(AST_data[AST_data["斜撐"].notna()])
        except:
            SDB_count=0
        SDB = st.markdown(f"<h1 style='text-align:center;color:red'>{SDB_count}案</h1>", unsafe_allow_html=True)
    #endregion
    st.markdown("<hr/>", unsafe_allow_html=True)
    row1 = st.columns(2)
    with row1[0]:
        Non_AST_Pie = px.pie(NON_AST_data, names='縣市', title='各縣市非制震宅建案數量統計')
        st.plotly_chart(Non_AST_Pie)
    with row1[1]:
        AST_Pie = px.pie(AST_data, names='縣市', title='各縣市制震宅建案數量統計')
        st.plotly_chart(AST_Pie)
    st.markdown("<hr/>", unsafe_allow_html=True)
    #region chropleth map
    row2 = st.columns(2)
    with row2[0]:
        NON_AST_country_Price_table = Choropleth_Data(NON_AST_data)
        # 繪製地坪單價地圖
        NON_AST_choropleth_map = px.choropleth_mapbox(NON_AST_country_Price_table,                                                # 資料表
                                geojson=mapGeo,                                    # 地圖資訊
                                locations='COUNTYCODE',                           # df要對應geojson的id名稱
                                featureidkey='properties.COUNTYCODE',             # geojson對應df的id名稱
                                color='單價',                                      # 顏色區分對象
                                color_continuous_scale='YlOrRd',                  # 設定呈現的顏色 (RdPu)
                                range_color=(round(np.nanmin(NON_AST_country_Price_table['單價'])),    # 顏色的值域範圍
                                                round(np.nanmax(NON_AST_country_Price_table['單價']))),   
                                mapbox_style='carto-positron',                    # mapbox地圖格式
                                zoom=6,                                           # 地圖縮放大小: 數字愈大放大程度愈大
                                center={'lat': 23.5832, 'lon': 120.5825},         # 地圖中心位置: 此處設定台灣地理中心碑經緯度
                                opacity=0.7,                                      # 設定顏色區塊的透明度 數值愈大愈不透明
                                hover_data=['縣市', "單價"]  # 設定游標指向資訊
                                )
        # 在地圖上加上標題
        NON_AST_choropleth_map.update_layout(title='全台非制震宅新建案地坪單價圖',title_x=0.02 ,title_y=0.95)  # 調整 title_x 和 title_y
        NON_AST_choropleth_map.update_layout(margin={'r':0, 't':0, 'l':0, 'b':0},coloraxis_colorbar=dict(title='單價(萬/坪)'))
        st.plotly_chart(NON_AST_choropleth_map,use_container_width=True)
    with row2[1]:
        AST_country_Price_table=Choropleth_Data(AST_data)
        # 繪製地坪單價地圖
        AST_choropleth_map = px.choropleth_mapbox(AST_country_Price_table,                                                # 資料表
                                geojson=mapGeo,                                    # 地圖資訊
                                locations='COUNTYCODE',                           # df要對應geojson的id名稱
                                featureidkey='properties.COUNTYCODE',             # geojson對應df的id名稱
                                color='單價',                                      # 顏色區分對象
                                color_continuous_scale='YlOrRd',                  # 設定呈現的顏色
                                range_color=(round(np.nanmin(AST_country_Price_table['單價'])),    # 顏色的值域範圍
                                                round(np.nanmax(AST_country_Price_table['單價']))),   
                                mapbox_style='carto-positron',                    # mapbox地圖格式
                                zoom=6,                                           # 地圖縮放大小: 數字愈大放大程度愈大
                                center={'lat': 23.5832, 'lon': 120.5825},         # 地圖中心位置: 此處設定台灣地理中心碑經緯度
                                opacity=0.7,                                               # 設定顏色區塊的透明度 數值愈大愈不透明
                                hover_data=['縣市', "單價"]  # 設定游標指向資訊
                                )
        # 在地圖上加上標題
        AST_choropleth_map.update_layout(title='全台制震宅新建案地坪單價圖',title_x=0.02 ,title_y=0.95)  # 調整 title_x 和 title_y
        AST_choropleth_map.update_layout(margin={'r':0, 't':0, 'l':0, 'b':0},coloraxis_colorbar=dict(title='單價(萬/坪)'))
        st.plotly_chart(AST_choropleth_map,use_container_width=True)
    #endregion
    st.markdown("<hr/>", unsafe_allow_html=True)
    row3 = st.columns(3)
    with row3[0]:
        FVD_brand_count = Brand_count("阻尼器", AST_data)
        FVD_Pie = px.pie(names=FVD_brand_count.index, values=FVD_brand_count.values, title='阻尼器使用廠牌統計')
        st.plotly_chart(FVD_Pie,use_container_width=True)
    with row3[1]:
        SDW_brand_count = Brand_count("制震壁", AST_data)
        SDW_Pie = px.pie(names=SDW_brand_count.index, values=SDW_brand_count.values, title='制震壁使用廠牌統計')
        st.plotly_chart(SDW_Pie,use_container_width=True)
    with row3[2]:
        SDB_brand_count = Brand_count("斜撐", AST_data)
        SDB_Pie = px.pie(names=SDB_brand_count.index, values=SDB_brand_count.values, title='斜撐使用廠牌統計')
        st.plotly_chart(SDB_Pie,use_container_width=True)
    #st.dataframe(AST_data,hide_index=True,use_container_width=True)
    #endregion

# 啟動應用程式
if __name__ == "__main__":
    main()