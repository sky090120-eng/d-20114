import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# [1. 데이터 불러오기 및 캐싱]
# @st.cache_data 데코레이터를 사용하여 데이터를 매번 다시 로드하지 않고 캐싱(재사용)합니다.
# -----------------------------------------------------------------------------
DATA_URL = "https://raw.githubusercontent.com/keep-growing-park/data-science/refs/heads/main/dataset/kobis_1year_boxoffice.csv"

@st.cache_data
def load_data():
    # 1. CSV 데이터 로드
    df = pd.read_csv(DATA_URL)
    
    # 2. 결측치가 포함된 행 삭제
    df = df.dropna()
    
    # 3. "기준일자" 컬럼을 datetime 형식으로 변환
    df["기준일자"] = pd.to_datetime(df["기준일자"])
    
    # 4. 기준일자 오름차순 정렬
    df = df.sort_values(by="기준일자", ascending=True)
    
    return df

# 데이터 로드 실행
data = load_data()

# -----------------------------------------------------------------------------
# 앱 기본 설정 및 제목 표시
# -----------------------------------------------------------------------------
st.set_page_config(page_title="영화 박스오피스 분석", layout="wide")
st.title("🎬 영화 박스오피스 데이터 분석 웹앱")

# -----------------------------------------------------------------------------
# [3. 영화 선택 기능]
# -----------------------------------------------------------------------------
# 영화별 최대 누적관객수를 구해 누적관객수 내림차순으로 영화 목록 정렬
movie_audience = data.groupby("영화명")["누적관객수"].max().sort_values(ascending=False)
movie_list = movie_audience.index.tolist()

# 사이드바에서 분석할 영화 선택 (기본값: 누적관객수 1위 영화)
selected_movie = st.sidebar.selectbox("영화 선택", movie_list)

# 선택한 영화의 데이터만 필터링
filtered_data = data[data["영화명"] == selected_movie]

# -----------------------------------------------------------------------------
# [섹션 1] 선택한 영화의 일자별 관객 수 변화 (선 그래프)
# -----------------------------------------------------------------------------
st.subheader(f"📌 {selected_movie} - 일자별 관객 수 변화 (선 그래프)")

fig1 = px.line(
    filtered_data,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} 일별 관객 수 추이",
    labels={"기준일자": "날짜", "해당일관객수": "관객 수"},
    markers=True
)

st.plotly_chart(fig1, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "개봉 이후 날짜가 지남에 따라 일별 관객 수가 어떻게 변하는지(상승/하락세 및 주말 스파이크)를 파악할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# [섹션 2] 선택한 영화의 기준일자별 누적관객수 변화 (영역 차트)
# -----------------------------------------------------------------------------
st.subheader(f"📌 {selected_movie} - 기준일자별 누적관객수 변화 (영역 차트)")

fig2 = px.area(
    filtered_data,
    x="기준일자",
    y="누적관객수",
    title=f"{selected_movie} 누적관객수 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객 수"}
)

st.plotly_chart(fig2, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "시간 경과에 따라 누적관객수가 증가하는 속도와 최종 관객 수의 전체 규모를 직관적으로 파악할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# [섹션 3] TOP 10에 20일 이상 등장한 영화 중 누적관객수 TOP 5 다중 선 그래프
# -----------------------------------------------------------------------------
st.subheader("📌 TOP 10 차트 20일 이상 유지 영화 중 누적관객수 TOP 5 비교")

# 1. 영화별 차트 등장 일수(행 수) 집계
movie_counts = data["영화명"].value_counts()

# 2. 20일 이상 등장한 영화명 목록 추출
movies_over_20days = movie_counts[movie_counts >= 20].index

# 3. 해당 영화들 중 최대 누적관객수 상위 5개 영화 선택
top5_over_20days = (
    data[data["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .nlargest(5)
    .index
)

# 4. 상위 5개 영화의 일자별 데이터 필터링
top5_data = data[data["영화명"].isin(top5_over_20days)].sort_values("기준일자")

# 5. Plotly 다중 선 그래프 생성
fig3 = px.line(
    top5_data,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="장기 흥행 TOP 5 영화 누적관객수 추이 비교",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객 수", "영화명": "영화 제목"}
)

st.plotly_chart(fig3, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "20일 이상 상위권에 머무른 대형 흥행작 간의 누적 관객 모객 속도와 최종 흥행 규모의 격차를 비교할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# [섹션 4] 전체 TOP 10 영화 관객 수 총합 및 7일 이동평균선
# -----------------------------------------------------------------------------
st.subheader("📌 전체 TOP 10 영화 일별 관객 총합 및 7일 이동평균선")

# 1. 기준일자별 TOP10 영화의 '해당일관객수' 총합 계산
daily_total = data.groupby("기준일자")["해당일관객수"].sum().reset_index()

# 2. 7일 이동평균(Rolling Mean) 컬럼 생성
daily_total["7일_이동평균"] = daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()

# 3. Plotly Graph Objects를 사용하여 원본 선과 이동평균선 병합 생성
fig4 = go.Figure()

# 원본 일별 관객 총합 (연하고 얇은 선)
fig4.add_trace(go.Scatter(
    x=daily_total["기준일자"],
    y=daily_total["해당일관객수"],
    mode="lines",
    name="일별 관객 총합",
    line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5)
))

# 7일 이동평균선 (진하고 두꺼운 선)
fig4.add_trace(go.Scatter(
    x=daily_total["기준일자"],
    y=daily_total["7일_이동평균"],
    mode="lines",
    name="7일 이동평균",
    line=dict(color="#FF4B4B", width=3)
))

# Layout 설정
fig4.update_layout(
    title="극장가 일별 전체 관객 총합 및 7일 이동평균 추이",
    xaxis_title="날짜",
    yaxis_title="관객 수",
    legend_title="구분",
    hovermode="x unified"
)

st.plotly_chart(fig4, use_container_width=True)

st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "주말과 평일 사이의 단기적인 관객 수 변동성을 완화하여, 전체 영화 시장(극장가)의 전반적인 성수기·비수기 흥행 흐름과 트렌드를 파악할 수 있습니다."
)
