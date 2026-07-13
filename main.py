import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울-양평 기온 비교 (도시 열섬현상)", layout="wide")

st.title("🏙️ 서울 vs 🌲 양평 기온 비교를 통한 도시 열섬현상 분석")
st.markdown("""
본 웹앱은 서울(도심)과 양평(외곽/교외)의 2025년 시간별 기온 데이터를 비교하여 
**도시 열섬현상(Urban Heat Island Effect)**을 시각적으로 확인하기 위해 제작되었습니다.
""")

# 데이터 로드 함수
@st.cache_data
def load_data():
    try:
        # 한글 인코딩 cp949 적용하여 파일 읽기
        seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
        
        # 일시 컬럼을 datetime으로 변환
        seoul['일시'] = pd.to_datetime(seoul['일시'])
        yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
        
        # 필요한 열만 선택 및 이름 변경
        seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울'})
        yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평'})
        
        # 일시 기준으로 데이터 병합
        df = pd.merge(seoul, yangpyeong, on='일시', how='inner')
        
        # 파생 변수(월, 시각, 기온차) 생성
        df['월'] = df['일시'].dt.month
        df['시각'] = df['일시'].dt.hour
        df['기온차(서울-양평)'] = df['서울'] - df['양평']
        
        return df
    except Exception as e:
        st.error(f"데이터를 읽어오는 중 오류가 발생했습니다: {e}")
        st.info("파일 이름이 '서울_기온.csv' 및 '양평_기온.csv'이며, 스크립트와 같은 폴더에 있는지 확인해주세요.")
        return None

df = load_data()

if df is not None:
    # 1. 상단 핵심 지표 요약 (Metrics)
    seoul_mean = df['서울'].mean()
    yang_mean = df['양평'].mean()
    mean_diff = df['기온차(서울-양평)'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("연간 서울 평균 기온", f"{seoul_mean:.2f} °C")
    col2.metric("연간 양평 평균 기온", f"{yang_mean:.2f} °C")
    col3.metric("평균 기온차 (서울 - 양평)", f"{mean_diff:.2f} °C", delta=f"{mean_diff:.2f} °C", delta_color="inverse")
    
    st.write("---")
    
    # ① 1년간 두 지역의 기온 변화 (선그래프)
    st.subheader("① 1년간 두 지역의 기온 변화")
    st.markdown("2025년 1년 동안의 서울과 양평의 전체 기온 추이입니다. 마우스 스크롤로 확대/축소하여 상세히 볼 수 있습니다.")
    
    # 시계열 그래프 표현을 위해 일시를 인덱스로 설정
    line_chart_data = df.set_index('일시')[['서울', '양평']]
    st.line_chart(line_chart_data)
    
    st.write("---")
    
    # 레이아웃 분할 (좌측: 시각별 기온차, 우측: 월별 기온차)
    col_left, col_right = st.columns(2)
    
    with col_left:
        # ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
        st.subheader("② 시각(0~23시)별 평균 기온차 (서울 - 양평)")
        st.markdown("하루 중 몇 시에 도심과 외곽의 기온 격차가 가장 크게 벌어지는지 확인합니다.")
        
        hourly_diff = df.groupby('시각')['기온차(서울-양평)'].mean()
        st.bar_chart(hourly_diff)
        
    with col_right:
        # ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
        st.subheader("③ 월(1~12월)별 평균 기온차 (서울 - 양평)")
        st.markdown("계절의 변화에 따라 도시 열섬현상의 강도가 어떻게 달라지는지 분석합니다.")
        
        monthly_diff = df.groupby('월')['기온차(서울-양평)'].mean()
        st.bar_chart(monthly_diff)
        
    st.write("---")
    st.info("💡 **도시 열섬현상 관찰 포인트**:\n"
            "1. **시각별 데이터**에서 주로 태양 복사열이 식는 **야간 및 새벽 시간대**에 서울의 기온이 양평보다 유의미하게 높게 유지되는지 확인해보세요.\n"
            "2. **월별 데이터**를 통해 여름철 혹은 겨울철 중 어느 계절에 두 지역 간의 열 집적 차이가 뚜렷하게 나타나는지 비교해보세요.")
