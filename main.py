import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="서울·양평 기온 및 전력수요 분석", layout="wide")

st.title("🏙️ 기온 비교를 통한 열섬현상 및 전력수요 관계 분석")
st.markdown("""
본 웹앱은 2025년 시간별 데이터를 바탕으로 두 가지 분석을 제공합니다.
* **탭 1**: 서울(도심)과 양평(교외)의 기온 비교를 통한 **도시 열섬현상** 분석
* **탭 2**: 서울의 기온 변화에 따른 **전력수요(MWh)**의 상관관계 분석
""")

# 데이터 로드 및 전처리 함수
@st.cache_data
def load_all_data():
    try:
        # 1. 기온 데이터 로드 (encoding="cp949")
        seoul = pd.read_csv("서울_기온.csv", encoding="cp949")
        yangpyeong = pd.read_csv("양평_기온.csv", encoding="cp949")
        
        seoul['일시'] = pd.to_datetime(seoul['일시'])
        yangpyeong['일시'] = pd.to_datetime(yangpyeong['일시'])
        
        seoul = seoul[['일시', '기온(°C)']].rename(columns={'기온(°C)': '서울_기온'})
        yangpyeong = yangpyeong[['일시', '기온(°C)']].rename(columns={'기온(°C)': '양평_기온'})
        
        # 2. 전력수요 데이터 로드 (encoding="cp949")
        power = pd.read_csv("전력수요.csv", encoding="cp949")
        power['일시'] = pd.to_datetime(power['일시'])
        power = power[['일시', '전력수요(MWh)']]
        
        # 3. 데이터 병합
        # 기온 데이터 병합 (탭 1용)
        df_temp = pd.merge(seoul, yangpyeong, on='일시', how='inner')
        df_temp['월'] = df_temp['일시'].dt.month
        df_temp['시각'] = df_temp['일시'].dt.hour
        df_temp['기온차(서울-양평)'] = df_temp['서울_기온'] - df_temp['양평_기온']
        
        # 기온 + 전력 데이터 병합 (탭 2용)
        df_power = pd.merge(seoul, power, on='일시', how='inner')
        df_power['월'] = df_power['일시'].dt.month
        df_power['시각'] = df_power['일시'].dt.hour
        
        # 기온 구간 범주화 (5도 단위 예시: -10~-5, -5~0, ...)
        df_power['기온구간'] = pd.cut(df_power['서울_기온'], 
                                   bins=range(-20, 45, 5), 
                                   labels=[f"{i}~{i+5}°C" for i in range(-20, 40, 5)])
        
        return df_temp, df_power
    except Exception as e:
        st.error(f"데이터를 로드하는 중 오류가 발생했습니다: {e}")
        st.info("같은 폴더 내에 '서울_기온.csv', '양평_기온.csv', '전력수요.csv' 파일이 모두 정합성 있게 존재하는지 확인해 주세요.")
        return None, None

df_temp, df_power = load_all_data()

if df_temp is not None and df_power is not None:
    
    # 탭 생성
    tab1, tab2 = st.tabs(["🏙️ 탭 1: 열섬 분석", "⚡ 탭 2: 전력 연결"])
    
    # ----------------------------------------------------
    # [탭1: 열섬 분석]
    # ----------------------------------------------------
    with tab1:
        st.header("도시 열섬현상(UHI) 분석")
        st.markdown("도심(서울)과 교외(양평)의 지역별 기온 편차를 시각화합니다.")
        
        # ① 1년간 두 지역 기온 변화 (선그래프)
        st.subheader("① 1년간 두 지역 기온 변화")
        line_data = df_temp.set_index('일시')[['서울_기온', '양평_기온']].rename(columns={'서울_기온':'서울', '양평_기온':'양평'})
        st.line_chart(line_data)
        
        st.write("---")
        col1, col2 = st.columns(2)
        
        with col1:
            # ② 시각(0~23시)별 평균 기온차, 서울-양평 (막대그래프)
            st.subheader("② 시각(0~23시)별 평균 기온차 (서울 - 양평)")
            hourly_diff = df_temp.groupby('시각')['기온차(서울-양평)'].mean()
            st.bar_chart(hourly_diff)
            
        with col2:
            # ③ 월(1~12월)별 평균 기온차, 서울-양평 (막대그래프)
            st.subheader("③ 월(1~12월)별 평균 기온차 (서울 - 양평)")
            monthly_diff = df_temp.groupby('월')['기온차(서울-양평)'].mean()
            st.bar_chart(monthly_diff)
            
    # ----------------------------------------------------
    # [탭2: 전력 연결]
    # ----------------------------------------------------
    with tab2:
        st.header("기온과 전력수요의 상관관계 분석")
        st.markdown("서울의 기온 변화가 전체 전력수요(MWh)에 미치는 영향을 분석합니다.")
        
        # ① 기온(가로)과 전력수요(세로)의 산점도
        st.subheader("① 기온과 전력수요의 상관 산점도")
        st.markdown("기온이 매우 낮거나(동절기 난방) 매우 높을 때(하절기 냉방) 전력수요가 급증하는 V자 곡선(혹은 U자 곡선) 형태를 띠는지 확인해보세요.")
        
        # streamlit 내장 scatter_chart 사용 (x축: 서울_기온, y축: 전력수요)
        st.scatter_chart(data=df_power, x='서울_기온', y='전력수요(MWh)')
        
        st.write("---")
        col3, col4 = st.columns(2)
        
        with col3:
            # ② 기온 구간별 평균 전력수요 (막대그래프)
            st.subheader("② 서울 기온 구간별 평균 전력수요")
            st.markdown("5°C 단위 구간별 평균 전력소비량 분포입니다.")
            
            # 구간별 평균 계산 후 데이터가 존재하는 구간만 시각화
            group_by_range = df_power.groupby('기온구간', observed=True)['전력수요(MWh)'].mean()
            st.bar_chart(group_by_range)
            
        with col4:
            # ③ 월(1~12월)별 평균 전력수요 (막대그래프)
            st.subheader("③ 월(1~12월)별 평균 전력수요")
            st.markdown("계절별 전력수요 변화 추이를 나타냅니다.")
            
            monthly_power = df_power.groupby('월')['전력수요(MWh)'].mean()
            st.bar_chart(monthly_power)
