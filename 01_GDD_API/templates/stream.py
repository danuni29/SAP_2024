import streamlit as st
from sklearn.neighbors import NearestNeighbors
import numpy as np

# 데이터 준비: 근육 그룹별 훈련법, 설명, 이미지, 동영상 (실제 이미지와 동영상 링크 필요)
workout_data = {
    '가슴': {
        'workouts': ['벤치 프레스', '덤벨 플라이', '체스트 프레스', '푸쉬업'],
        'descriptions': ['바벨을 눕힌 상태에서 수직으로 들어 올립니다.', '덤벨을 이용해 가슴 근육을 늘리고 수축합니다.', '기계를 이용한 체스트 훈련.',
                         '팔을 벌려 몸을 들어올리는 훈련.'],
        'images': ['https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzAzMDNfMjg1%2FMDAxNjc3Nzc4NjU5MTA4.PTNc-AnxEtN6fXQwayra1my0e2M07742VmmUkoS07MIg.wTImYLil9fdosJM7fF-A9ds7wo6gcZheFBe4LgfDyvAg.PNG.fitness_day4%2F%25BD%25BA%25C5%25A9%25B8%25B0%25BC%25A6_2023-03-03_%25BF%25C0%25C0%25FC_2.37.32.png&type=sc960_832', 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMzA4MTBfMTcg%2FMDAxNjkxNjYyNzAxODYz.xU7zM7wnaDJUSF3H5vBiMJscAHNhxcsRWNd93DZvlQcg.q8aFjPpCwP01mr-729yBKA3TwoHTYrN3wnNpYAM8Spkg.PNG.younggulis%2F%25B4%25FD%25BA%25A7%25C7%25C3%25B6%25F3%25C0%25CC.png&type=sc960_832', 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyMDEyMDRfMTQz%2FMDAxNjA3MDc3MDMxNDUx.QEimpjhovuT500bmaVRuEJ7FwTVGbPmGqUE8oBwxU1Ag.3wPqCZTuwNrn92VzpdVrML3fjpxxSYx1crzae4qJQ48g.PNG.fitness_the_moment%2F%25B1%25A4%25B1%25B3%25C7%25EF%25BD%25BA%25C0%25E5_%25B1%25A4%25B1%25B3%25C7%25EF%25BD%25BA_%25C3%25BC%25BD%25BA%25C6%25AE%25C7%25C1%25B7%25B9%25BD%25BA.PNG&type=sc960_832', 'https://search.pstatic.net/common/?src=http%3A%2F%2Fblogfiles.naver.net%2FMjAyNDA3MjNfMjUx%2FMDAxNzIxNzI2Njc2OTQ2.Ptz0CmR7dN5WjJmauzzS8mtKwq1bZtrJRD7CbNewhkAg.pdN_mzoECsBXEfU7va_0k_wuOK7uxhA7Kds0ur2E0ocg.JPEG%2F%25BB%25E7%25C1%25F82.jpg&type=sc960_832'],
        'videos': ['https://www.youtube.com/watch?v=A2kHURY746E', 'https://www.youtube.com/shorts/-1SM42SMCMU', 'https://www.youtube.com/shorts/eLbsMnfoCq8', 'https://www.youtube.com/shorts/tLP4k0JKI8Q']
    },
    '등': {
        'workouts': ['풀업', '바벨 로우', '데드리프트', '랫 풀다운'],
        'descriptions': ['턱걸이를 통해 등 근육을 강화.', '바벨을 이용한 등 근육 수축 운동.', '하체와 등의 힘을 동시에 사용하는 운동.', '머신을 이용한 풀다운 운동.'],
        'images': ['https://img1.daumcdn.net/thumb/C500x500/?fname=http://t1.daumcdn.net/brunch/service/user/4KiG/image/Rx3CX6ioDLgmtAz3FBaSQJP8jO0.jpg', 'https://mblogthumb-phinf.pstatic.net/MjAyMjA2MDNfMjYx/MDAxNjU0MjUwOTQ4NDI2.a_w7bl_OVcH_wvet8ictkfNyhZlNnnYm4GbcxYRIYicg.z4-5MiTPi2tqvK5h1DB0ruelXjhtVsDumo7rEQ7C0osg.PNG.mtns1/n4.png?type=w800', 'https://blog.kakaocdn.net/dn/v3sBL/btqCeu5LC1f/2dlhnMv9cpeYWdXDdWP9oK/img.jpg', 'https://blog.kakaocdn.net/dn/6yVPH/btsATVPj2Zj/UQCbr3DRQyLoLJobB3nbA1/img.jpg'],
        'videos': ['https://www.youtube.com/shorts/Ka1uGBFHoRU', 'https://www.youtube.com/shorts/_sdc6D6WvtU', 'https://www.youtube.com/shorts/eip18bNyWMQ', 'https://www.youtube.com/shorts/BKtt7m8_bsw']
    },
    '어깨': {
        'workouts': ['밀리터리 프레스', '사이드 레터럴 레이즈', '덤벨 숄더 프레스'],
        'descriptions': ['바벨을 이용해 어깨 근육을 수직으로 들어 올립니다.', '옆으로 덤벨을 들어 어깨를 자극합니다.', '덤벨로 어깨를 강화하는 운동입니다.'],
        'images': ['https://blog.kakaocdn.net/dn/bpIUPa/btqDZNiVgvi/xhcthRvct2uPEMhNIvM5F0/img.png', 'https://blog.kakaocdn.net/dn/chS45A/btrVecy4SSM/Uz2II2yTXiK9rx19WGyHuk/img.png', 'https://blog.kakaocdn.net/dn/csARhE/btrVkV9TOGc/nMPcXTKoYHsgc1GiVnWP60/img.jpg'],
        'videos': ['https://www.youtube.com/watch?v=ZjtrVA2uyS4', 'https://www.youtube.com/watch?v=iNgwwI3WBTo', 'https://www.youtube.com/shorts/hcp5tnX89N0']
    },
    '팔': {
        'workouts': ['바벨 컬', '덤벨 컬', '트라이셉스 푸쉬다운', '덤벨 킥백'],
        'descriptions': ['바벨을 이용해 이두근을 강화합니다.', '덤벨을 이용해 이두근을 강화합니다.', '머신을 이용해 삼두근을 강화합니다.', '덤벨을 뒤로 밀어 삼두근을 강화합니다.'],
        'images': ['https://mblogthumb-phinf.pstatic.net/MjAxOTA2MDRfMTE4/MDAxNTU5NjU4OTkwMjky.GhHJllU0SbeXeKj0Ev2xVjduM1uV77UoLEHJfctXyfUg.VHajee0El_28-K-4iZ8BPl9naaBTm-ULfFc8mp43li4g.PNG.0307mini/%EC%9D%B4%EB%91%90%EC%9A%B4%EB%8F%99_%EC%8A%A4%ED%83%A0%EB%94%A9_%EB%B0%94%EB%B2%A8%EC%BB%AC_%ED%8C%94%EC%9A%B4%EB%8F%99_(1).png?type=w800', 'https://burnfit.io/wp-content/uploads/2023/11/DB_PREA_CURL.gif', 'https://blog.kakaocdn.net/dn/cWiuKi/btshCfNFgyG/PC0rURlyLDzE0cpByzkI50/img.jpg', 'https://www.lyfta.app/_next/image?url=%2Fthumbnails%2F03331201.jpg&w=3840&q=20'],
        'videos': ['https://www.youtube.com/watch?v=Dlg0W_5mq98', 'https://www.youtube.com/watch?v=0Vl5X_Qa6aE', 'https://www.youtube.com/watch?v=ObEtLS9heOo',
                   'https://www.youtube.com/watch?v=w2JyIqOfqpc']
    },
    '하체': {
        'workouts': ['스쿼트', '레그 프레스', '런지', '레그 컬'],
        'descriptions': ['하체 전반을 강화하는 대표 운동입니다.', '기계를 이용해 하체 근육을 집중적으로 자극합니다.', '걷는 동작을 통해 하체를 단련하는 운동입니다.',
                         '기계를 이용해 허벅지 뒤쪽을 강화합니다.'],
        'images': ['https://health.chosun.com/site/data/img_dir/2022/06/24/2022062402201_0.jpg', 'https://mblogthumb-phinf.pstatic.net/MjAyMjA0MjVfOTQg/MDAxNjUwODQ5NzU3MDA1.cyXjoxpqc3JIjp6w-Wzob1_A-sZWocL--gUeGENOOywg.sSa1Vb9Ch6P3Gd12F0CZUgC_M78gWSTos_SMa5Pe7dsg.PNG.fitnessbeauty/%EB%A0%88%EA%B7%B8%ED%94%84%EB%A0%88%EC%8A%A4.png?type=w800', 'https://dnvefa72aowie.cloudfront.net/businessPlatform/bizPlatform/profile/center_biz_1792961/1690202096571/e28dd30c43d235833ed8ee2f6670772c23ac87d6a303e585e409499d95c5ffb2.png?q=95&s=1440x1440&t=inside', 'https://blog.kakaocdn.net/dn/oKOOl/btqz7pzhAue/72rC9wcsIXJC3b76kAuwuk/img.jpg'],
        'videos': ['https://www.youtube.com/shorts/RGb4Di4Dk_k', 'https://www.youtube.com/watch?v=EV0F_3S7Sks', 'https://www.youtube.com/watch?v=7IZtFeqtdGE', 'https://www.youtube.com/watch?v=6I0NiRc6yww']
    }
}

# 머신러닝용 샘플 데이터 생성 (운동 강도, 주당 훈련 빈도에 따라 추천)
training_data = np.array([
    [3, 5],  # 예시: 가슴 운동(3회), 주당 5회 훈련
    [4, 3],  # 예시: 등 운동(4회), 주당 3회 훈련
    [5, 4],  # 예시: 어깨 운동(5회), 주당 4회 훈련
    [4, 3],  # 예시: 팔 운동(4회), 주당 3회 훈련
    [5, 6],  # 예시: 하체 운동(5회), 주당 6회 훈련
])

# 머신러닝 모델 준비 (K-Nearest Neighbors)
model = NearestNeighbors(n_neighbors=1)
model.fit(training_data)

# Streamlit 애플리케이션
st.title('개인 맞춤형 웨이트 트레이닝 추천')

# 사용자가 훈련하고 싶은 근육 그룹 선택
muscle_group = st.selectbox('훈련하고 싶은 근육 그룹을 선택하세요:', workout_data.keys())

# 트레이닝 경험 선택
experience = st.radio('트레이닝 경험을 선택하세요:', ['초보자', '중급자', '고급자'])

# 주당 훈련 횟수 선택
days_per_week = st.slider('주당 훈련 횟수를 선택하세요:', 1, 7, 3)

# 체지방량(%) 입력
body_fat_percentage = st.slider('체지방량(%)을 입력하세요:', 5, 50, 20)

# 골격근량(kg) 입력
muscle_mass = st.slider('골격근량(kg)을 입력하세요:', 20, 50, 30)

# 머신러닝 모델을 사용한 개인 맞춤형 추천
user_data = np.array([[len(workout_data[muscle_group]['workouts']), days_per_week]])
distances, indices = model.kneighbors(user_data)

# 추천 운동 출력
st.write(f'**{muscle_group}** 훈련을 위한 추천 운동:')
for i, workout in enumerate(workout_data[muscle_group]['workouts']):
    st.write(f'### {workout}')
    st.write(f'**설명**: {workout_data[muscle_group]["descriptions"][i]}')

    # 이미지 출력 (실제 이미지 파일 경로 또는 URL로 대체)
    image_path = workout_data[muscle_group]["images"][i]
    st.image(image_path, caption=workout, use_column_width=True)

    # "동영상 보기" 텍스트 클릭 시 유튜브 링크로 이동
    video_url = workout_data[muscle_group]["videos"][i]
    st.markdown(f'[동영상 보기]({video_url})', unsafe_allow_html=True)



# 경험 레벨에 따른 세트, 반복 수, 휴식 시간 추천
experience_levels = {
    '초보자': {'sets': 3, 'reps': 12, 'rest': 60},
    '중급자': {'sets': 4, 'reps': 10, 'rest': 90},
    '고급자': {'sets': 5, 'reps': 8, 'rest': 120}
}
sets = experience_levels[experience]['sets']
reps = experience_levels[experience]['reps']
rest = experience_levels[experience]['rest']


# 체지방량에 따라 유산소 운동 추천
if body_fat_percentage > 25:
    cardio_minutes = 30 + (body_fat_percentage - 25) * 0.5
    st.write(f'체지방량이 높으므로 유산소 운동을 추천드립니다: **{int(cardio_minutes)}분**의 유산소 운동을 포함하세요.')
else:
    cardio_minutes = 20
    st.write(f'유산소 운동은 **{int(cardio_minutes)}분**을 추천드립니다.')

# 골격근량에 따라 세트 및 반복 수 조정
if muscle_mass > 40:
    sets += 1
    reps -= 2

st.write(f'경험 수준: **{experience}**')
st.write(f'권장 세트 수: **{sets}세트**')
st.write(f'권장 반복 수: **{reps}회**')
st.write(f'세트 간 휴식 시간: **{rest}초**')

# 주당 훈련 횟수에 따른 추가 정보
st.write(f'주당 **{days_per_week}회** 훈련을 추천드립니다.')