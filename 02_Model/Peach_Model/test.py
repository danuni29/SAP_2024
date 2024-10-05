import os
import pandas as pd

# 디렉터리 경로 설정
directory = r"C:\code\SAP_2024\02_Model\Peach_Model\peach_observed_data"

# 디렉터리 내 모든 CSV 파일에 대해 반복
for filename in os.listdir(directory):
    if filename.endswith(".csv"):
        file_path = os.path.join(directory, filename)

        # CSV 파일 읽기
        df = pd.read_csv(file_path)

        # '만개기'라는 칼럼명을 'Date'로 변경
        if '만개기' in df.columns:
            df.rename(columns={'만개기': 'Date'}, inplace=True)

            # 수정된 데이터프레임을 원래 파일에 다시 저장
            df.to_csv(file_path, index=False)
            print(f"Updated {filename}")

print("All files updated.")