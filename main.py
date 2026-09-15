import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

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
movie_audience = (
    data.groupby("영화명")["누적관객수"].max().sort_values(ascending=False)
)
movie_list = movie_audience.index.tolist()

# 사이드바에서 영화 선택 (기본값: 첫 번째 영화)
selected_movie = st.sidebar.selectbox("영화 선택", movie_list)

# 선택한 영화의 데이터만 필터링
filtered_data = data[data["영화명"] == selected_movie]

# -----------------------------------------------------------------------------
# 섹션 1: 선택한 영화의 일별 관객 수 추이 (선 그래프)
# -----------------------------------------------------------------------------
st.subheader(f"📌 {selected_movie} - 일자별 관객 수 변화")

# Plotly를 활용한 선 그래프 생성
fig1 = px.line(
    filtered_data,
    x="기준일자",
    y="해당일관객수",
    title=f"{selected_movie} 일별 관객 수",
    labels={"기준일자": "날짜", "해당일관객수": "관객 수"},
    markers=True,
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
# 섹션 2: 선택한 영화의 기준일자별 누적관객수 변화 (영역 차트)
# -----------------------------------------------------------------------------
st.subheader(f"📌 {selected_movie} - 기준일자별 누적관객수 변화 (영역 차트)")

# Plotly를 활용한 영역 차트 생성
fig2 = px.area(
    filtered_data,
    x="기준일자",
    y="누적관객수",
    title=f"{selected_movie} 누적관객수 추이",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객 수"},
)

# 그래프 화면에 출력
st.plotly_chart(fig2, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "시간 흐름에 따른 관객 수의 누적 성장을 한눈에 직관적으로 확인할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# 섹션 3: TOP 10 20일 이상 등장 영화 중 누적관객수 TOP 5 다중 선 그래프
# -----------------------------------------------------------------------------
st.subheader("📌 TOP 10 20일 이상 유지 영화 중 누적관객수 TOP 5 비교")

# 1. 영화별 차트 등장 일수 계산
movie_counts = data["영화명"].value_counts()

# 2. 등장 일수가 20일 이상인 영화목록 필터링
movies_over_20days = movie_counts[movie_counts >= 20].index

# 3. 20일 이상 등장한 영화들 중에서 누적관객수 상위 5개 추출
top5_over_20days = (
    data[data["영화명"].isin(movies_over_20days)]
    .groupby("영화명")["누적관객수"]
    .max()
    .nlargest(5)
    .index
)

# 4. 상위 5개 영화 데이터 추출 및 정렬
top5_data = data[data["영화명"].isin(top5_over_20days)].sort_values("기준일자")

# 5. Plotly 다중 선 그래프 생성
fig3 = px.line(
    top5_data,
    x="기준일자",
    y="누적관객수",
    color="영화명",
    title="TOP 10 20일 이상 상영 영화 TOP 5의 누적관객수 추이 비교",
    labels={"기준일자": "날짜", "누적관객수": "누적 관객 수", "영화명": "영화 제목"},
)

# 그래프 화면에 출력
st.plotly_chart(fig3, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "차트에 20일 이상 장기 흥행한 대형 영화 Top 5 간의 흥행 속도와 최종 관객 수 차이를 한눈에 비교할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# 섹션 4: 전체 TOP10 영화 일별 관객수 총합 & 7일 이동평균선
# -----------------------------------------------------------------------------
st.subheader("📌 전체 박스오피스 일별 관객수 총합 및 7일 이동평균선")

# 1. 기준일자별 전체 관객수 합계 계산
daily_total = (
    data.groupby("기준일자")["해당일관객수"].sum().reset_index()
)

# 2. 7일 이동평균 계산 (rolling window=7)
daily_total["7일이동평균"] = (
    daily_total["해당일관객수"].rolling(window=7, min_periods=1).mean()
)

# 3. Plotly graph_objects를 이용해 2개의 선을 겹쳐 그리기
fig4 = go.Figure()

# 원본 일별 총 관객수 선 (연한 색상)
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["해당일관객수"],
        mode="lines",
        name="일별 관객 총합",
        line=dict(color="rgba(150, 150, 150, 0.4)", width=1.5),
    )
)

# 7일 이동평균선 (진한 색상)
fig4.add_trace(
    go.Scatter(
        x=daily_total["기준일자"],
        y=daily_total["7일이동평균"],
        mode="lines",
        name="7일 이동평균",
        line=dict(color="#E50914", width=3),
    )
)

# 그래프 레이아웃 설정
fig4.update_layout(
    title="일별 전체 관객수 합계 및 7일 이동평균 추이",
    xaxis_title="날짜",
    yaxis_title="관객 수",
    legend_title="구분",
    hovermode="x unified",
)

# 그래프 화면에 출력
st.plotly_chart(fig4, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "요일별 관객 수 변동(주말 급증, 평일 감소) 노이즈를 다듬어 전체 극장가의 관객수 흐름과 계절/성수기 트렌드를 명확하게 파악할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# 섹션 5: 월별 전체 관객수 합계 (막대그래프)
# -----------------------------------------------------------------------------
st.subheader("📌 월별 전체 관객수 총합 (막대그래프)")

# 1. 기준일자를 'YYYY-MM' 형식의 연-월 컬럼으로 생성
daily_total["연월"] = daily_total["기준일자"].dt.strftime("%Y-%m")

# 2. 연-월 단위로 그룹화하여 월별 전체 관객수 합계 계산
monthly_total = (
    daily_total.groupby("연월")["해당일관객수"].sum().reset_index()
)

# 3. Plotly 막대그래프 생성
fig5 = px.bar(
    monthly_total,
    x="연월",
    y="해당일관객수",
    title="월별 극장가 관객수 합계",
    labels={"연월": "년-월", "해당일관객수": "총 관객 수"},
    text_auto=".2s",
)

# 막대 색상 및 스타일 조정
fig5.update_traces(marker_color="#2b5c8f")
fig5.update_layout(xaxis_type="category")

# 그래프 화면에 출력
st.plotly_chart(fig5, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "월별 극장 관객 총합을 통해 연중 영화 시장의 성수기(방학/연휴 등)와 비성수기를 한눈에 비교 파악할 수 있습니다."
)

st.divider()

# -----------------------------------------------------------------------------
# 섹션 6: 날짜별 관객수 히트맵 (캘린더 히트맵)
# -----------------------------------------------------------------------------
st.subheader("📌 요일 x 주차별 일별 전체 관객수 캘린더 히트맵")

# 1. 주차(Week) 및 요일(Day of Week) 정보 추출
heatmap_df = daily_total.copy()
heatmap_df["연도주차"] = heatmap_df["기준일자"].dt.strftime("%Y-%U주")  # YYYY-주차
heatmap_df["요일숫자"] = heatmap_df["기준일자"].dt.dayofweek  # 월:0, 화:1 ... 일:6
heatmap_df["날짜문자열"] = heatmap_df["기준일자"].dt.strftime("%Y-%m-%d")

# 요일 이름을 월요일부터 일요일 순서로 한글 지정
day_labels = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]

# Pivot 테이블 생성 (X: 연도주차, Y: 요일숫자, 값: 관객수합계/날짜문자열)
pivot_total = heatmap_df.pivot(index="요일숫자", columns="연도주차", values="해당일관객수")
pivot_dates = heatmap_df.pivot(index="요일숫자", columns="연도주차", values="날짜문자열")

# 2. Plotly 히트맵 생성
fig6 = go.Figure(
    data=go.Heatmap(
        z=pivot_total.values,
        x=pivot_total.columns,
        y=[day_labels[i] for i in pivot_total.index],
        text=pivot_dates.values,  # 마우스 호버 시 보여줄 yyyy-mm-dd 날짜 데이터
        colorscale="YlOrRd",      # 관객수가 많을수록 붉어지는 칼라맵
        hovertemplate="<b>날짜</b>: %{text}<br><b>요일</b>: %{y}<br><b>관객수</b>: %{z:,.0f}명<extra></extra>",
    )
)

fig6.update_layout(
    title="일자별/요일별 전체 관객수 분포 (캘린더 뷰)",
    xaxis_title="주차 (Year-Week)",
    yaxis_title="요일",
    yaxis=dict(autorange="reversed"),  # 월요일이 제일 위로 오도록 y축 순서 정렬
)

# 그래프 화면에 출력
st.plotly_chart(fig6, use_container_width=True)

# 그래프 하단 설명 문구 영역
st.info(
    "💡 **이 그래프로 알 수 있는 것:** "
    "주말 및 특정 명절/공휴일 등 일자별 극장 관객 몰림 현상과 주차별 관객 변화 양상을 캘린더 형태로 직관적으로 파악할 수 있습니다."
)
