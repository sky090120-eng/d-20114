import pandas as pd
import streamlit as st
import plotly.express as px

# -----------------------------------------------------------------------------
# [1. 데이터 불러오기]
# @st.cache_data 데코레이터를 사용하여 데이터를 매번 다시 로드하지 않고 캐싱(재사용)합니다.
# -----------------------------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"

@st.cache_data
def load_data():
    # 1. 데이터 불러오기
    df = pd.read_csv(DATA_URL)
    
    # 2. [날짜 전처리] 결측치가 있는 행 삭제
    df = df.dropna()
    
    # 3. [날짜 전처리] "기준일자" 컬럼을 datetime 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    
    # 4. [날짜 전처리] 기준일자 오름차순 정렬
    df = df.sort_values(by="기준일자", ascending=True)
    
    return df

# 데이터 로드 실행
data = load_data()

# -----------------------------------------------------------------------------
# 앱 레이아웃 설정
# -----------------------------------------------------------------------------
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")
st.title("🎬 영화 박스오피스 데이터 분석")

# -----------------------------------------------------------------------------
# [3. 영화 선택 기능]
# -----------------------------------------------------------------------------
# 영화별 최대 누적관객수를 구해 누적관객수 내림차순으로 영화 목록 정렬
movie_audience = data.groupby("영화명")["누적관객수"].max().sort_values(ascending=False)
movie_list = movie_audience.index.tolist()

# 사이드바에서 영화 선택 (기본값: 첫 번째 영화)
selected_movie = st.sidebar.selectbox("영화 선택", movie_list)

# 선택한 영화의 데이터만 필터링
filtered_data = data[data["영화명"] == selected_movie]

# -----------------------------------------------------------------------------
# 첫 번째 그래프: 일자별 관객 수 변화 (선 그래프)
# -----------------------------------------------------------------------------
st.subheader(f"📌 {selected_movie} - 일자별 관객 수 변화")

# Plotly 선 그래프 생성
fig1 = px.line(
    filtered_data,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} 일별 관객 수 추이",
    labels={"기준일자": "날짜", "해당일관객수": "관객 수"},
    markers=True
)

# 그래프 화면에 출력
st.plotly_chart(fig1, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "개봉 이후 날짜가 지남에 따라 일별 관객 수가 어떻게 변하는지(상승/하락세)를 파악할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# 두 번째 그래프: 기준일자별 누적관객수 변화 (영역 차트)
# -----------------------------------------------------------------------------
st.subheader(f"📌 {selected_movie} - 기준일자별 누적관객수 변화")

# Plotly 영역 차트(Area Chart) 생성
fig2 = px.area(
    filtered_data,
    x="기준일자",
    y="누적관객수",
    title=f"{selected_movie} 누적관객수 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객 수"}
)

# 그래프 화면에 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "시간 경과에 따라 누적관객수가 증가하는 속도와 최종 집계 관객 수의 전체 규모를 한눈에 시각적으로 파악할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# 세 번째 그래프: 누적관객수 TOP 5 영화 비교 (다중 선 그래프)
# -----------------------------------------------------------------------------
st.subheader("📌 누적관객수 TOP 5 영화 - 기준일자별 누적관객수 비교")

# 1. 누적관객수 상위 5개 영화 이름 추출
top5_movies = movie_audience.head(5).index.tolist()

# 2. TOP 5 영화에 해당하는 데이터만 필터링
top5_data = data[data["영화명"].isin(top5_movies)]

# 3. Plotly 다중 선 그래프 생성 (color="영화명" 속성으로 영화별 색상 및 범례 구분)
fig3 = px.line(
    top5_data,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="상위 5개 영화 누적관객수 추이 비교",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객 수", "영화명": "영화 제목"},
    markers=True
)

# 그래프 화면에 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "가장 흥행한 상위 5개 영화의 흥행 속도와 누적 관객 수의 차이를 직관적으로 비교·분석할 수 있습니다."
)
