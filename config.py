# =============================================
# SV Book Automation - 설정 파일
# =============================================

# 국회도서관 Open API 키
NL_API_KEY = "YOUR_NL_API_KEY_HERE"

# 네이버 책 검색 API (책 소개 보완용)
NAVER_CLIENT_ID     = "JLKKvYTPT41YH_j2kzjW"
NAVER_CLIENT_SECRET = "FSOzICIszn"

# Google Sheets 설정
SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"  # URL에서 /d/ 뒤의 ID
SHEET_NAME = "SV Book"                         # 탭 이름

# Google 서비스 계정 키 파일 경로
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# 검색 키워드 — 핵심 주제 중심으로 집중
KEYWORDS_KO = [
    # AI·기술
    "AI 인재", "인공지능 인재", "AI 시대", "AI 거버넌스",
    # 사회적 가치·임팩트
    "사회적가치", "사회가치", "사회연대경제", "임팩트",
    # ESG·지속가능
    "ESG", "탄소중립", "기후변화", "기후위기", "생물다양성",
    # 거버넌스·민주주의
    "거버넌스", "민주주의", "정치개혁", "공공정책",
    # 경제·불평등
    "불평등", "사회혁신", "자본주의 전환", "지속가능경제",
    # 에너지·환경
    "에너지전환", "재생에너지", "탈탄소",
    # 인재·미래
    "미래사회", "인재경영", "다양성 포용", "여성 리더십",
]

KEYWORDS_EN = [
    "ESG", "social value", "social enterprise", "impact investing",
    "climate change", "net zero", "biodiversity", "sustainability",
    "AI governance", "future of work", "inequality", "democracy",
    "energy transition", "renewable energy", "social innovation",
    "diversity equity inclusion", "women leadership",
]

# 검색 설정
SEARCH_START_DATE = None   # None이면 최근 6개월 자동 계산
RESULTS_PER_KEYWORD = 10   # 키워드당 최대 검색 결과
MAX_TOTAL_RESULTS = 200    # 전체 최대 결과 수

# 소스 이름 (스프레드시트 '매체명' 컬럼에 표시)
SOURCE_NL = "국회도서관"
