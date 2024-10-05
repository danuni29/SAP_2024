import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
import os
import geopandas as gpd
import folium
from folium import Choropleth



def draw_bloom_date_graph(predicted_df, observed_data, select_region):
    predicted_df['full_bloom_date'] = pd.to_datetime(predicted_df['full_bloom_date'])

    # 연도를 추출해서 x축에 사용할 열 생성
    predicted_df['year'] = predicted_df['full_bloom_date'].dt.year

    # y축에 사용할 월-일 형식 만들기 (임시로 2000년을 기준으로 설정해 연도 없이 날짜 순서로 정렬)
    predicted_df['bloom_day'] = pd.to_datetime(predicted_df['full_bloom_date'].dt.strftime('2000-%m-%d'))

    # 그래프 그리기
    fig = go.Figure()

    # 예측된 개화일 그래프 추가
    fig.add_trace(go.Scatter(x=predicted_df['year'], y=predicted_df['bloom_day'],
                             mode='lines+markers', name='예측일', showlegend=True))

    # 관측된 개화일 데이터가 있을 때만 처리
    if observed_data is not None:
        observed_data['Date'] = pd.to_datetime(observed_data['Date'])
        observed_data['year'] = observed_data['Date'].dt.year
        observed_data['bloom_day'] = pd.to_datetime(observed_data['Date'].dt.strftime('2000-%m-%d'))

        # 관측된 개화일 그래프 추가
        fig.add_trace(go.Scatter(x=observed_data['year'], y=observed_data['bloom_day'],
                                 mode='lines+markers', name='실제 관측일', showlegend=True))

    # 그래프 레이아웃 설정
    fig.update_layout(
        title=f"Full Bloom Dates in {select_region}",
        xaxis_title="Year",
        yaxis_title="Full Bloom Date",
        xaxis=dict(type='category'),  # 연도별로 나열
        yaxis=dict(tickformat='%m-%d'),  # y축을 월-일 형식으로 표시
        legend_title="Type",
        hovermode="x unified"
    )

    # 그래프 보여주기
    st.plotly_chart(fig)
def main():
    st.title('2024 스마트농업프로그래밍')
    st.sidebar.title('개화 시기 예측 모델🌸')

    # 작물 선택
    select_species = st.sidebar.selectbox(
        '작물을 선택하세요',
        ['배🍐', '복숭아🍑']
    )

    # 복숭아를 선택했을 때 품종 선택
    if select_species == '복숭아🍑':
        select_variety = st.sidebar.selectbox(
            '품종을 선택하세요',
            ['유명', '창방조생', '천중도백도', '장호원백도', '청홍']
        )

        # 품종에 따른 지역 선택
        if select_variety == '청홍':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['춘천', '수원', '청주', '나주', '진주']
            )
        elif select_variety == '유명':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['춘천', '수원', '청주', '청도', '나주', '진주']
            )
        elif select_variety == '창방조생':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['수원']
            )
        elif select_variety == '장호원백도':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['청도']
            )
        elif select_variety == '천중도백도':
            select_region = st.sidebar.selectbox(
                '지역을 선택하세요',
                ['청도']
            )

    # 배를 선택했을 때 지역 선택
    elif select_species == '배🍐':
        select_region = st.sidebar.selectbox(
            '지역을 선택하세요',
            ['이천', '천안', '상주', '영천', '완주', '나주', '사천', '울주']
        )

    # 연도 선택 (2004~2024)
    select_year = st.sidebar.slider('연도를 선택하세요', 2004, 2024, 2024)

    # 그래프 보기 체크박스
    st.sidebar.write("보고 싶은 그래프를 선택하세요:")
    show_temp = st.sidebar.checkbox('평균온도변화')
    show_precip = st.sidebar.checkbox('강수량변화')
    show_bloom = st.sidebar.checkbox('개화일변화')

    # 메인 타이틀
    st.title(f"{select_species} 개화 예측 모델")

    # 선택 사항 출력 (디버깅용)
    # st.write(f"선택한 작물: {select_species}")
    # if select_species == '복숭아🍑':
    #     st.write(f"선택한 품종: {select_variety}")
    # st.write(f"선택한 지역: {select_region}")
    # st.write(f"선택한 연도: {select_year}")

    # 메인 화면에서 모델 선택
    # st.write(f"### {select_species} 모델을 선택하세요:")

    if select_species == '배🍐':
        select_model = st.radio(
            '사용할 모델을 선택하세요',
            ['DVR', 'mDVR', 'CD']  # 배에 해당하는 모델들
        )
    elif select_species == '복숭아🍑':
        select_model = st.radio(
            '사용할 모델을 선택하세요',
            ['DVR', 'CD', 'NCD']  # 복숭아에 해당하는 모델들
        )


    # 여기서부터 이제 결과 표시~~~~

    if select_species == '배🍐':
        predicted_df = pd.read_csv(rf"C:\code\SAP_2024\02_Model\Pear_Model_output\{select_model}_Model_result_{select_region}.csv")
        # st.write(df)

        filtered_data = predicted_df[predicted_df['full_bloom_date'].str[:4] == str(select_year)]
        observed_data = pd.read_csv(rf"C:\code\SAP_2024\02_Model\input\observe_data\flowering_date_{select_region}.csv")

        st.subheader(f"{select_region} 지역 {select_year}년 개화일: {filtered_data.iloc[0]['full_bloom_date']}")


        # 그래프에 대한 로직은 여기에 추가하면 됩니다.
        if show_temp:
            st.write("평균온도변화 그래프를 표시합니다.")
            # 그래프 표시 로직 추가
        if show_precip:
            st.write("강수량변화 그래프를 표시합니다.")
            # 그래프 표시 로직 추가
        if show_bloom:
            st.write("개화일변화 그래프를 표시합니다.")
            draw_bloom_date_graph(predicted_df, observed_data, select_region)

    elif select_species == '복숭아🍑':
        variety_dict = {
            '유명': 'ymn',
            '창방조생': 'cbj',
            '천중도백도': 'cjo',
            '장호원백도': 'jhw',
            '청홍': 'chh'
        }
        predicted_df = pd.read_csv(rf"C:\code\SAP_2024\02_Model\Peach_Model\Peach_Model_output\{select_region}_{variety_dict[select_variety]}_{select_model}.csv")

        filtered_data = predicted_df[predicted_df['full_bloom_date'].str[:4] == str(select_year)]
        observed_data_path =rf"C:\code\SAP_2024\02_Model\Peach_Model\peach_observed_data\flowering_date_{select_region}_{variety_dict[select_variety]}.csv"

        st.subheader(f"{select_region} 지역 {select_year}년 개화일: {filtered_data.iloc[0]['full_bloom_date']}")

        if os.path.exists(observed_data_path):
            observed_data = pd.read_csv(observed_data_path)
        else:
            observed_data = None

        # 그래프에 대한 로직은 여기에 추가하면 됩니다.
        if show_temp:
            st.write("평균온도변화 그래프를 표시합니다.")
            # 그래프 표시 로직 추가
        if show_precip:
            st.write("강수량변화 그래프를 표시합니다.")
            # 그래프 표시 로직 추가
        if show_bloom:
            st.write("개화일변화 그래프를 표시합니다.")
            draw_bloom_date_graph(predicted_df, observed_data, select_region)

if __name__ == '__main__':
    main()
