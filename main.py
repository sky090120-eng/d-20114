from datetime import datetime, timedelta
import pandas as pd
import pytz
import requests
import streamlit as st

# 페이지 기본 설정 (타이틀 및 레이아웃)
st.set_page_config(
    page_title="일별 박스오피스 순위", page_icon="🎬", layout="wide"
)


# 1. API 요청 결과 캐싱 함수 (1시간 동안 기억)
@st.cache_data(ttl=3600)
def fetch_box_office_data(target_date, api_key):
    """KOBIS API를 호출하여 데이터를 가져옵니다.

    1시간 동안 동일한 날짜의 데이터는 다시 요청하지 않고 캐시된 값을 사용합니다.
    """
    url = "https://www.kobis.or.kr/kobisopenapi/webservice/rest/boxoffice/searchDailyBoxOfficeList.json"
    params = {"key": api_key, "targetDt": target_date}

    try:
        response = requests.get(url, params=params, timeout=10)
        # HTTP 요청 성공 여부 확인
        if response.status_code != 200:
            return None, f"서버 응답 에러 (상태 코드: {response.status_code})"

        data = response.json()

        # 인증키 오류 등 KOBIS API 자체 오류 메시지(faultInfo)가 포함되어 온 경우
        if "faultInfo" in data:
            error_msg = data["faultInfo"].get(
                "message", "인증 오류가 발생했습니다."
            )
            return None, f"API 오류: {error_msg}"

        # 정상 데이터 추출
        box_office_result = data.get("boxOfficeResult", {})
        daily_list = box_office_result.get("dailyBoxOfficeList", [])

        # 결과 목록이 비어 있는 경우
        if not daily_list:
            return None, "그날은 아직 집계 전입니다."

        return daily_list, None

    except requests.exceptions.RequestException as e:
        return None, f"네트워크 요청 중 오류가 발생했습니다: {str(e)}"


# --- 메인 화면 구성 ---
st.title("🎬 일별 박스오피스 순위")

# 2. 한국 시간(KST) 기준 어제 날짜 계산 (달력에서 선택 가능한 최대 날짜)
kst = pytz.timezone("Asia/Seoul")
now_kst = datetime.now(kst)
yesterday_kst = (now_kst - timedelta(days=1)).date()

# 3. 사이드바 또는 상단에서 사용자가 조회 날짜를 직접 선택
selected_date = st.date_input(
    label="조회할 날짜를 선택하세요 (최대 어제까지 선택 가능)",
    value=yesterday_kst,
    max_value=yesterday_kst,  # 오늘은 아직 집계 전이므로 선택 제한
)

# 선택한 날짜를 API에 전달할 YYYYMMDD 형태 문자열로 변환
target_date = selected_date.strftime("%Y%m%d")
display_date = selected_date.strftime("%Y년 %m월 %d일")

st.caption(f"선택한 기준 일자: **{display_date}**")

# 4. Streamlit Secrets에서 API Key 가져오기
api_key = st.secrets.get("KOBIS_KEY")

if not api_key:
    # API 키가 설정되지 않은 경우 안내 메시지 출력
    st.error("🔑 API 키(KOBIS_KEY)가 설정되지 않았습니다.")
    st.info(
        """
    **확인 방법:**
    1. Streamlit Cloud의 앱 설정 메뉴(Settings -> Secrets)로 이동하세요.
    2. 아래 형식으로 API 키를 추가해 주세요.
    ```toml
    KOBIS_KEY = "발급받은_KOBIS_인증키"
    ```
    """
    )
    st.stop()

# 5. API 데이터 호출
daily_list, error_message = fetch_box_office_data(target_date, api_key)

# 6. 예외 및 오류 처리
if error_message:
    # 목록이 비어있는 경우("그날은 아직 집계 전입니다.")는 일반 안내 문구(warning/info)로 표시
    if error_message == "그날은 아직 집계 전입니다.":
        st.warning(f"ℹ️ {error_message}")
    else:
        st.error(
            f"🚨 데이터를 가져오는 데 실패했습니다.\n\n**오류 내용:** {error_message}"
        )
        st.warning(
            """
        **조치 방법:**
        - Secrets에 입력한 `KOBIS_KEY` 값이 정확한지 확인해 주세요.
        - KOBIS 서버의 일시적인 장애일 수 있으니 잠시 후 다시 시도해 주세요.
        """
        )
    st.stop()

# 7. 데이터 전처리 (문자열 -> 숫자 변환)
df = pd.DataFrame(daily_list)

df["rank"] = pd.to_numeric(df["rank"])
df["rankInten"] = pd.to_numeric(df["rankInten"])  # 전날 대비 순위 증감
df["audiCnt"] = pd.to_numeric(df["audiCnt"])
df["audiAcc"] = pd.to_numeric(df["audiAcc"])
df["scrnCnt"] = pd.to_numeric(df["scrnCnt"])

# 순위 기준 정렬
df = df.sort_values("rank")


# 8. 전날 대비 순위 증감 텍스트 변환 함수 (양수: 🔺, 음수: 🔻, 0: -)
def format_rank_inten(val):
    if val > 0:
        return f"🔺 {val}"
    elif val < 0:
        return f"🔻 {abs(val)}"
    else:
        return "-"


df["순위변화"] = df["rankInten"].apply(format_rank_inten)


# 9. 누적관객 100만 명 돌파 시 트로피(🏆) 이모지 추가 함수
def format_movie_title(row):
    title = row["movieNm"]
    if row["audiAcc"] >= 1_000_000:
        return f"🏆 {title}"
    return title


df["displayMovieNm"] = df.apply(format_movie_title, axis=1)

# 10. 1위 영화 하이라이트 지표 카드 세 장 출력
top_1 = df.iloc[0]

st.subheader(f"🥇 1위: {top_1['displayMovieNm']}")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("일일 관객수", f"{top_1['audiCnt']:,} 명")
with col2:
    st.metric("누적 관객수", f"{top_1['audiAcc']:,} 명")
with col3:
    st.metric("상영 스크린수", f"{top_1['scrnCnt']:,} 개")

st.divider()

# 11. 관객수 상위 5편 막대그래프 (영화명에 트로피 이모지 적용)
st.subheader("📊 관객수 상위 5개 영화")
top_5_df = df.head(5)

st.bar_chart(data=top_5_df, x="displayMovieNm", y="audiCnt")

st.divider()

# 12. 전체 박스오피스 순위 표 출력
st.subheader("📋 전체 박스오피스 순위 (1위~10위)")

# 출력에 사용할 컬럼 정리 및 이름 변경
table_df = df[
    [
        "rank",
        "순위변화",
        "displayMovieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
    ]
].copy()
table_df.columns = [
    "순위",
    "전날대비",
    "영화명",
    "개봉일",
    "관객수(명)",
    "누적관객(명)",
    "스크린수(개)",
]

# 화면에 표 표시 (index 숨김 처리)
st.dataframe(
    table_df.style.format(
        {"관객수(명)": "{:,}", "누적관객(명)": "{:,}", "스크린수(개)": "{:,}"}
    ),
    use_container_width=True,
    hide_index=True,
)
