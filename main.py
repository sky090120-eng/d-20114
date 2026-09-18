import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    layout="wide",
)

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    # 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 추출
    df["장르"] = df["genre"].astype(str).str.split("|").str[0].str.strip()
    return df


df = load_data()

# ── 그래프 1. 장르별 영화 편수 도넛 ──
st.header("1. 장르별 영화 편수 (도넛)")

genre_count = df["장르"].value_counts().reset_index()
genre_count.columns = ["장르", "편수"]

fig1 = px.pie(
    genre_count,
    names="장르",
    values="편수",
    hole=0.45,
    title="장르별 영화 비율",
)

# 호버 시 편수와 비율 표기
fig1.update_traces(
    hovertemplate="<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}<extra></extra>"
)

st.plotly_chart(fig1, use_container_width=True)

# 그래프 분석 내용 안내 구역
with st.container():
    top_genre = genre_count.iloc[0]["장르"]
    top_count = genre_count.iloc[0]["편수"]
    st.info(
        f"💡 **이 그래프로 알 수 있는 것:** 분석 대상 영화 중 가장 많은 비중을 차지하는 장르는 **{top_genre}**({top_count}편)이며, 일부 상위 장르에 편중되어 있음을 알 수 있습니다."
    )

st.divider()

# ── 그래프 2. 개봉 첫 주 관객수 vs 총 관객수 ──
st.header("2. 개봉 첫 주 관객수와 총 관객수의 관계")

fig2 = px.scatter(
    df,
    x="first_week_audi",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    size="days_in_top10",
    labels={
        "first_week_audi": "개봉 첫 주 관객수",
        "total_audi": "총 관객수",
        "days_in_top10": "Top10 진입 일수",
    },
    title="개봉 첫 주 관객수 vs 총 관객수 (점 크기: Top10 유지 일수)",
)

st.plotly_chart(fig2, use_container_width=True)

with st.container():
    st.info(
        "💡 **이 그래프로 알 수 있는 것:** 개봉 첫 주 관객수가 많은 영화일수록 최종 총 관객수도 높으며, Top10 머문 날수가 길수록 흥행 규모가 커지는 상관관계를 나타냅니다."
    )
