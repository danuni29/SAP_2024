import matplotlib.pyplot as plt

# 'Malgun Gothic' 폰트 설정 (Windows에서 사용 가능)
plt.rcParams['font.family'] = 'Malgun Gothic'

# 마이너스 기호 깨짐 방지
plt.rcParams['axes.unicode_minus'] = False

# 한글 출력 테스트
plt.text(0.5, 0.5, '테스트 한글 출력', fontsize=15)
plt.show()