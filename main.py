import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide"
)
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    # 1년간 박스오피스 10위권에 든 영화 216편의 요약표를 불러옵니다
    df = pd.read_csv(DATA_URL)
    # 장르가 세로막대 기호(|)로 여러 개 적힌 영화는 첫 번째 장르만 씁니다
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
    hole=0.45,  # 가운데 구멍을 뚫어 도넛 모양으로
)
# 조각에 마우스를 올리면 편수와 비율이 보이게 합니다
fig1.update_traces(
    hovertemplate="%{label}<br>%{value}편 (%{percent})<extra></extra>"
)
st.plotly_chart(fig1, use_container_width=True)

# '이 그래프로 알 수 있는 것' 한 문장을 적는 자리
st.text_input("이 그래프로 알 수 있는 것", key="note1")

st.divider()

# ── 그래프 2. 장르별 영화 관객수 분포 (트리맵) ──
st.header("2. 장르별 영화 관객수 분포 (트리맵)")

labels = []
parents = []
values = []

# 1. 루트 노드 (장르 모음)
for genre in df["장르"].unique():
    labels.append(genre)
    parents.append("")
    values.append(df[df["장르"] == genre]["total_audi"].sum())

# 2. 리프 노드 (각 장르에 속한 영화들)
for _, row in df.iterrows():
    labels.append(row["movieNm"])
    parents.append(row["장르"])
    values.append(row["total_audi"])

fig2 = go.Figure(
    go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        hovertemplate="<b>%{label}</b><br>총 관객수: %{value:,}명<extra></extra>",
    )
)

fig2.update_layout(
    margin=dict(t=30, l=10, r=10, b=10), title="장르 및 영화별 총 관객수"
)

st.plotly_chart(fig2, use_container_width=True)

# '이 그래프로 알 수 있는 것' 한 문장을 적는 자리
st.text_input("이 그래프로 알 수 있는 것", key="note2")

st.divider()

# ── 그래프 3. 총 관객수 분포 (히스토그램) ──
st.header("3. 총 관객수 분포 (히스토그램)")

# 관객수 데이터 계산 (최고 관객 영화 및 구간 분석)
top_movie = df.loc[df["total_audi"].idxmax()]
top_movie_name = top_movie["movieNm"]
top_movie_audi = top_movie["total_audi"]

fig3 = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    title="영화별 총 관객수 분포",
    labels={"total_audi": "총 관객수", "count": "영화 수"},
)

fig3.update_traces(
    hovertemplate="<b>총 관객수 구간:</b> %{x}명<br><b>영화 수:</b> %{y}편<extra></extra>"
)

st.plotly_chart(fig3, use_container_width=True)

# 그래프 설명 문구 출력
insight_text = f"대부분의 영화는 관객수 100만~200만 명 이하 구간에 밀집되어 있으며, 가장 관객이 많은 영화는 **'{top_movie_name}'**({top_movie_audi:,}명)입니다."

st.text_input("이 그래프로 알 수 있는 것", value=insight_text, key="note3")

st.divider()

# ── 그래프 4. 개봉일 스크린수 vs 총 관객수 (산점도) ──
st.header("4. 개봉일 스크린수와 총 관객수의 관계 (산점도)")

fig4 = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="장르",
    hover_name="movieNm",
    title="개봉일 스크린수 vs 총 관객수",
    labels={
        "first_scrn": "개봉일 스크린수 (개)",
        "total_audi": "총 관객수 (명)",
        "장르": "장르",
    },
)

fig4.update_traces(
    hovertemplate="<b>%{hovertext}</b><br>개봉일 스크린수: %{x:,}개<br>총 관객수: %{y:,}명<extra></extra>"
)

st.plotly_chart(fig4, use_container_width=True)

# '이 그래프로 알 수 있는 것' 한 문장을 적는 자리
st.text_input("이 그래프로 알 수 있는 것", key="note4")

st.divider()
# 앞으로 그래프를 계속 추가할 구역
st.header("5. (다음 그래프를 여기에 추가)")
