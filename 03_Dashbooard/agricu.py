import streamlit as st
import pandas as pd
import datetime as dt
from io import BytesIO

# 초기 데이터 설정: 토양 상태 기록
if 'soil_data' not in st.session_state:
    st.session_state.soil_data = {
        '날짜': [],
        'pH': [],
        '습도 (%)': [],
        '온도 (°C)': [],
        '질소 (N) mg/kg': [],
        '인 (P) mg/kg': [],
        '칼륨 (K) mg/kg': []
    }

# Streamlit 앱 타이틀
st.title("토양 상태 기록 및 분석 도구")

# 1. 사용자 입력 섹션
st.header("토양 상태 입력")
date_input = st.date_input("날짜", dt.date.today())
ph = st.number_input("pH 값", min_value=0.0, max_value=14.0, step=0.1)
humidity = st.number_input("습도 (%)", min_value=0, max_value=100, step=1)
temperature = st.number_input("온도 (°C)", min_value=-30, max_value=50, step=1)
nitrogen = st.number_input("질소 (N) mg/kg", min_value=0, step=1)
phosphorus = st.number_input("인 (P) mg/kg", min_value=0, step=1)
potassium = st.number_input("칼륨 (K) mg/kg", min_value=0, step=1)

# 2. 데이터 추가 버튼
if st.button("토양 상태 추가"):
    new_entry = {
        '날짜': date_input,
        'pH': ph,
        '습도 (%)': humidity,
        '온도 (°C)': temperature,
        '질소 (N) mg/kg': nitrogen,
        '인 (P) mg/kg': phosphorus,
        '칼륨 (K) mg/kg': potassium
    }

    # 새 데이터 추가
    for key in new_entry:
        st.session_state.soil_data[key].append(new_entry[key])

    st.success("토양 상태가 추가되었습니다!")

# 3. 토양 상태 기록 표시
st.header("토양 상태 기록")
df = pd.DataFrame(st.session_state.soil_data)
st.dataframe(df)

# 4. 데이터 분석 및 시각화
st.header("토양 상태 분석")
if not df.empty:
    st.subheader("pH 값 변화")
    st.line_chart(df[['날짜', 'pH']].set_index('날짜'))

    st.subheader("온도 변화")
    st.line_chart(df[['날짜', '온도 (°C)']].set_index('날짜'))

    st.subheader("습도 변화")
    st.line_chart(df[['날짜', '습도 (%)']].set_index('날짜'))

    st.subheader("영양 성분 변화")
    st.line_chart(df[['날짜', '질소 (N) mg/kg', '인 (P) mg/kg', '칼륨 (K) mg/kg']].set_index('날짜'))


# 5. 스케줄 다운로드 기능 (Excel 파일)
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='토양 상태')
    return output.getvalue()


if st.button("토양 데이터 다운로드 (Excel)"):
    if not df.empty:
        excel_data = to_excel(df)
        st.download_button(
            label="다운로드",
            data=excel_data,
            file_name='soil_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
    else:
        st.warning("다운로드할 데이터가 없습니다.")
