import pandas as pd
import os

# CSV 파일 읽기
df = pd.read_csv('장호원황도.csv', encoding='cp949')

# 지역명 열이 'location'이라고 가정
grouped = df.groupby('지역')

# 새로운 디렉토리 경로 설정 (모든 지역 파일을 저장할 폴더)
output_dir = 'peach_observed_data'

# 디렉토리가 없는 경우 생성
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 그룹별로 새로운 CSV 파일로 저장
for location, group in grouped:
    # 파일명: 지역명.csv
    output_file = os.path.join(output_dir, f"flowering_date_{location}_jhw.csv")

    # 그룹별 데이터를 새로운 CSV로 저장
    group.to_csv(output_file, index=False)
    print(f"{output_file} 저장 완료")