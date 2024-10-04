import os
import pandas as pd

# 경로 설정
observe_dir = '../input/observe_data'
output_dir = '../Pear_Model_output'

# 지역명 매핑 (영어 이름 -> 한글 이름)
region_mapping = {
    'Cheonan': '천안',
    'Icheon': '이천',
    'naju': '나주',
    'sacheon': '사천',
    'Sangju': '상주',
    'ulju': '두서',
    'Wanju': '완주',
    'Yeongcheon': '영천'
}

# observe_data 파일들을 순회
for file_name in os.listdir(observe_dir):
    if file_name.endswith('.csv'):  # CSV 파일만 처리
        base_file_name = os.path.splitext(file_name)[0]  # 확장자 제거

        # 지역명이 매핑에 있는 경우 처리
        for eng_name, kor_name in region_mapping.items():
            if eng_name in base_file_name:  # 예: 'Cheonan'이 파일명에 있으면
                observe_file_path = os.path.join(observe_dir, file_name)

                # output_dir에서 파일명을 확인하여 지역명이 맞는지 체크
                for result_file_name in os.listdir(output_dir):
                    if result_file_name.endswith('.csv') and kor_name in result_file_name:  # 예: 'CD_Model_result_천안.csv'
                        cd_model_file_path = os.path.join(output_dir, result_file_name)

                        # 두 파일 불러오기
                        observe_df = pd.read_csv(observe_file_path)
                        cd_model_df = pd.read_csv(cd_model_file_path)

                        # date 열에서 연도를 추출하여 병합
                        observe_df['year'] = observe_df['Date'].str[:4]  # 'Date' 열에서 연도 추출
                        merged_df = pd.merge(cd_model_df, observe_df[['Date', 'year']], left_on='full_bloom_date', right_on='year')

                        # 병합된 결과를 원래 경로에 덮어쓰기 저장
                        merged_df.to_csv(cd_model_file_path, index=False)

                        print(f'{file_name} 파일이 {result_file_name}에 병합되어 {cd_model_file_path}에 저장되었습니다.')