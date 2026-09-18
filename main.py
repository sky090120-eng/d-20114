import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="영화 데이터 그래프 - 분포와 관계",
    layout="wide",
)

st.title("영화 데이터 그래프 - 분포와 관계")


# 데이터 로드 및 전처리
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"
    df = pd.read_csv(url)

    # genre 열에서 첫 번째 장르만 추출 ('|' 구분자 처리)
    df["genre"] = (
        df["genre"].astype(str).apply(lambda x: x.split("|")[0].strip())
    )

    return df


df = load_data()

# -------------------------------------------------------------------
# 1. 장르별 영화 편수 (도넛 그래프)
# -------------------------------------------------------------------
st.header("1. 장르별 영화 편수 분포")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig_genre = px.pie(
    genre_counts,
    values="count",
    names="genre",
    hole=0.4,
    title="장르별 영화 비율",
    hover_data=["count"],
)
fig_genre.update_traces(
    textposition="inside",
    textinfo="percent+label",
    hovertemplate="<b>장르:</b> %{label}<br><b>편수:</b> %{value}편<br><b>비율:</b> %{percent}",
)

st.plotly_chart(fig_genre, use_container_width=True)

with st.container():
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.write(
        f"박스오피스 상위권 영화 중 가장 비중이 높은 주요 장르는 **{genre_counts.iloc[0]['genre']}**이며, 특정 인기 장르 쏠림 현상을 확인할 수 있습니다."
    )

st.divider()

# -------------------------------------------------------------------
# 2. 개봉 첫 주 관객수 vs 총 관객수 (산점도)
# -------------------------------------------------------------------
st.header("2. 개봉 첫 주 관객수와 총 관객수의 관계")

fig_scatter = px.scatter(
    df,
    x="first_week_audi",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    size="days_in_top10",
    labels={
        "first_week_audi": "개봉 첫 주 관객수",
        "total_audi": "총 관객수",
        "genre": "장르",
        "days_in_top10": "Top10 진입 일수",
    },
    title="개봉 첫 주 관객수 vs 총 관객수 (점 크기: Top10 유지 일수)",
)

st.plotly_chart(fig_scatter, use_container_width=True)

with st.container():
    st.subheader("💡 이 그래프로 알 수 있는 것")
    st.write(
        "개봉 첫 주 관객수가 많은 영화일수록 대체로 총 관객수도 높으며, Top10에 오래 머문 영화일수록 초반 관객 대비 최종 흥행 성공률이 높음을 알 수 있습니다."
    )
