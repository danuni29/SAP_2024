import pandas as pd

# CSV 파일을 읽어옴 (파일 경로를 적절히 변경하세요)
df = pd.read_csv('../input/weather_data/813_청도.csv', encoding='euc-kr')

# 날짜 관련 컬럼을 분리하여 'year', 'month', 'day', 'date'로 변환
df['일시'] = pd.to_datetime(df['일시'], format='%Y-%m-%d')
df['year'] = df['일시'].dt.year
df['month'] = df['일시'].dt.month
df['day'] = df['일시'].dt.day
df['date'] = df['일시'].dt.date

# 원하는 컬럼 이름으로 변경
df.rename(columns={
    '최고기온(°C)': 'tmax',
    '최저기온(°C)': 'tmin',
    '평균기온(°C)': 'tavg',
    '일강수량(mm)': 'rainfall',
    '평균 풍속(m/s)': 'wind'
    # 나머지 컬럼은 필요에 따라 추가로 매핑합니다.
}, inplace=True)

# 불필요한 컬럼을 제거하거나, 필요한 컬럼만 선택하여 새로운 데이터프레임으로 정리
df_cleaned = df[['year', 'month', 'day', 'date', 'tmax', 'tavg', 'tmin', 'rainfall', 'wind']]

# 결과 저장
df_cleaned.to_csv('813_청도.csv', index=False)

print("데이터가 정리되고 저장되었습니다.")