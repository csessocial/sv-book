"""SV Book 관련성 필터 — 문제집/소설/잡지 제거 + 주제 점수 기반 추천"""

import re
from datetime import datetime, timedelta

# ── 제외 패턴 ──────────────────────────────────────────────
EXCLUDE_TITLE_PATTERNS = [
    r"^20\d\d\s",           # 연도로 시작하는 수험서 (2026 고시넷 등)
    r"공무원",
    r"수험[서생]?",
    r"문제집",
    r"기출[문제]?",
    r"NCS",
    r"EBS",
    r"모의고사",
    r"실기",
    r"필기",
    r"자격[증시]",
    r"한권으로 끝",
    r"속성[완성]?",
    r"시험[대비]?",
    r"합격[의]?",
    r"기사\s*시험",
    r"TOEIC|IELTS|TOEFL",
    r"초등|중등|고등\s*[수국영]",
    # 순수 AI 기술서 — 코딩/개발/모델 구현 중심
    r"파이썬.*(AI|딥러닝|머신러닝)",
    r"(딥러닝|머신러닝|강화학습).*(입문|기초|실습|코딩|프로그래밍|구현|튜토리얼)",
    r"(ChatGPT|GPT|LLM|RAG|프롬프트).*(활용법|사용법|마스터|완전정복|입문|실습)",
    r"(AI|인공지능).*(개발|코딩|프로그래밍|엔지니어링|아키텍처|모델링)",
    r"(텐서플로|파이토치|사이킷런|케라스|허깅페이스)",
    r"(자연어처리|NLP|컴퓨터비전|CV).*(실습|구현|코딩)",
    # 투자/재테크 상품서
    r"ETF",
    r"(주식|펀드|채권|코인|암호화폐).*(투자|매매|분석|전략|입문|완전정복)",
    r"(부동산|아파트).*(투자|매매|경매)",
    # 특정 정치인 이름이 제목에 들어간 책 (저자가 아닌 제목 기준)
    r"^(조국|이재명|윤석열|한동훈|홍준표|안철수|이낙연|문재인|박근혜|이명박).*(의|이|선택|회고|생각|정치|일기|편지|자서전)",
    r"(의 선택|의 시간|의 길|의 꿈)$",
    # 좁은 실무·안전보건·산업규격 ESG
    r"(안전보건|산업안전|소방|위험성평가|KOSHA|OHSAS|ISO\s*45001).*(ESG|경영|관리)",
    r"ESG.*(안전보건|산업안전|소방|위험성평가)",
    r"(안전보건경영|안전관리론|소방안전관리)",
    # 스포츠 설계·스포츠 경영 실무서
    r"스포츠.*(설계|경영|마케팅|트레이닝|코칭|매니지먼트)",
    # 기초 교과서·개론서
    r"(개론|입문|기초|기본).*(기술|공학|화학|물리|수학|생물|지구과학)",
    r"(수소|원자력|핵융합|반도체|배터리).*(기술|개론|입문|기초|공학|원리)",
    r"(대학교재|교과서|강의교재|학습서)$",
]

EXCLUDE_PUBLISHERS = {
    "시대고시기획", "시대에듀", "고시넷", "에듀윌", "이기적",
    "한빛아카데미", "영진닷컴", "길벗", "박문각", "해커스",
    "메가스터디", "이투스", "오르비", "수경출판사",
    "하이앤북", "시대고시", "나라비전", "공단기",
    "선비북스",
}

# ── 소설·잡지·생활취미 제외 ───────────────────────────────
EXCLUDE_CATEGORIES = {
    "국내소설", "외국소설", "소설", "시/에세이", "시집",
    "만화", "웹툰", "라이트노벨", "판타지/무협",
    "잡지", "매거진",
    # 생활·취미·스포츠
    "건강/취미", "스포츠/레저", "요리/살림", "여행", "반려동물",
    "육아/교육", "임신/출산", "뷰티/패션", "원예/인테리어",
    "종교", "운동", "취미/실용", "가정/살림",
    # 아동·청소년
    "어린이", "유아", "초등", "청소년", "아동", "그림책",
    "중학생", "고등학생", "어린이도서", "청소년도서",
}

EXCLUDE_NOVEL_TITLE_PATTERNS = [
    r"(장편|단편)\s*(소설|판타지)",
    r"소설$",
    r"\d+권$",
    r"웹툰|웹소설",
    # 아동·청소년 대상 명시
    r"(어린이|청소년|아동|초등|중등)\s*(을 위한|을위한|의|도서|추천|필독)",
    r"10대\s*(를 위한|를위한|의|가 꼭|들의)",
    r"쫌 아는 10대",
    r"쫌아는 10대",
    r"어린이\s*(가|과|의|를)",
    r"그림책",
    # 쉽게 읽기 / 입문 시리즈
    r"(쉽게 읽는|쉽게읽는|만화로 보는|만화로보는|만화로 배우는).*(경제|역사|과학|사회|철학|정치|법)",
    r"(초등|중학|고등).*(필독|추천|교과|과학|사회|역사)",
    r"어린이\s*(경제|과학|역사|사회|철학)",
    # 학습/독후감 유도형 어린이·청소년 교양서
    r"(초등학생|중학생|고등학생).*(읽어야|알아야|필독|추천)",
    r"(세상을 바꾼|역사 속|위인|인물).*(어린이|청소년|10대)",
    r"(어린이|청소년).*(위인|인물|역사|세계사|한국사)",
    r"아이들.*(생각|이야기|미래|함께|세상)",
    r"(쉽게|쉽게읽는|쉽게배우는)\s*(배우는|읽는|보는|이해하는)",
    r"교과서에\s*(없는|나오는|담긴)",
]

EXCLUDE_MAGAZINE_PATTERNS = [
    r"(월간|주간|격주|계간|연간)\s*\w+",
    r"vol\.\s*\d+",
    r"no\.\s*\d+",
    r"issue\s*\d+",
    r"\d+호$",
    r"한경\s*ESG",
    r"한국경제\s*ESG",
]

# ── 제목/내용에 이 단어 있으면 무조건 제외 ──────────────────
EXCLUDE_CONTENT_KEYWORDS = [
    # 투자/금융 상품
    "ETF", "etf",
    # 좁은 실무 안전보건 (ESG 제목이어도 내용이 산업안전 실무면 제외)
    "안전보건경영시스템", "위험성평가", "KOSHA", "ISO 45001",
    # 스포츠 실기
    "스포츠 설계", "트레이닝 프로그램", "코칭 방법론",
    # 아동·청소년 대상 내용 키워드
    "초등학생", "중학생", "고등학생",
    "청소년을 위한", "어린이를 위한", "10대를 위한",
    "청소년이 꼭", "어린이가 꼭", "청소년 여러분", "어린이 여러분",
    "독후감", "방학 숙제", "교과서에 나오는",
    "풋살", "축구", "야구", "농구", "골프", "테니스", "배드민턴",
    "다이어트", "운동법", "헬스", "요가", "필라테스",
    "요리", "레시피", "쿠킹", "베이킹",
    "뜨개질", "자수", "캘리그라피",
    "반려견", "반려묘", "강아지", "고양이",
    "임신", "출산", "육아", "태교",
    "성경", "불교", "기도", "명상법",
    "부동산 투자", "주식 투자", "코인", "재테크 방법",
]

# 제목에 이 단어만 있고 사회적 맥락 키워드가 없으면 제외 (순수 기술서 판별)
PURE_TECH_AI_PATTERNS = [
    r"(AI|인공지능).*(프로그래밍|코딩|개발|엔지니어|구현|모델|API|서비스 개발)",
    r"(ChatGPT|GPT-?\d|claude|gemini).*(사용법|활용법|완전정복|업무 자동화|비즈니스 활용)",
    r"(딥러닝|머신러닝|강화학습)",
    r"(파이썬|Python).*(AI|인공지능|데이터)",
    r"(LLM|RAG|벡터|임베딩|파인튜닝|프롬프트 엔지니어링)",
    r"(텐서플로|파이토치|사이킷런|케라스|허깅페이스|랭체인)",
]

# 이 키워드가 함께 있으면 순수기술서 제외에서 구제 (사회적 인사이트 책)
SOCIAL_CONTEXT_KEYWORDS = [
    "사회", "인간", "윤리", "거버넌스", "불평등", "미래", "인재", "교육",
    "민주주의", "노동", "일자리", "정책", "가치", "공정", "권력", "문화",
    "경제", "젠더", "환경", "지속가능", "임팩트", "조직", "리더",
    "society", "ethics", "governance", "human", "future", "work",
]

# 출판일 범위: 최근 N개월 이내만 포함
DATE_RANGE_MONTHS = 12

# ── SV Book 주제 점수 ──────────────────────────────────────
TOPIC_SCORES = [
    # ★★★★ 최우선 주제 (6점) — AI×사회 교차점, 우리가 가장 원하는 책
    (["AI 시대 사회적가치", "AI와 사회적가치", "인공지능 사회적가치"], 6),
    (["AI 인재", "인공지능 인재", "AI 시대 인재", "디지털 인재"], 6),
    (["AI 거버넌스", "알고리즘 편향", "AI 윤리", "AI 불평등", "AI와 민주주의"], 6),
    (["AI 시대 일의 미래", "자동화 사회", "AI와 노동", "AI와 일자리"], 6),

    # ★★★ 핵심 주제 (5점)
    (["사회적 가치", "사회가치", "social value", "impact investing", "임팩트 투자"], 5),
    (["사회연대경제", "협동조합", "사회적기업", "공정무역"], 5),
    (["ESG", "esg"], 5),
    (["기후변화", "기후 위기", "climate change", "탄소중립", "넷제로", "net zero", "기후정의"], 5),
    (["생물다양성", "biodiversity", "생태계 위기", "지구온난화"], 4),
    (["거버넌스", "governance", "민주주의", "democracy", "정치 개혁", "공공정책"], 4),
    (["불평등", "inequality", "형평성", "equity", "사회 격차", "빈곤"], 4),
    (["지속가능", "sustainable", "sustainability", "SDGs"], 4),

    # ★★ 중요 주제 (3점)
    (["AI 시대", "인공지능과 인간", "AI와 인간", "디지털 전환과 사회"], 3),
    (["에너지 전환", "재생에너지", "renewable energy", "탈탄소", "탈석탄"], 3),
    (["다양성", "diversity", "포용", "inclusion", "DEI"], 3),
    (["사회 혁신", "social innovation", "시스템 변화"], 3),
    (["자본주의", "capitalism", "경제 체제", "신자유주의 비판", "경제민주화"], 3),
    (["지정학", "국제질서", "패권", "geopolitics", "다극체제"], 3),
    (["여성", "젠더", "gender", "성평등", "페미니즘", "women leadership"], 3),

    # ★ 관련 주제 (2점)
    (["인재", "인재경영", "talent", "인재개발"], 2),
    (["미래사회", "미래 사회", "future of work", "일의 미래"], 2),
    (["인구", "저출생", "고령화", "이주", "난민", "migration"], 2),
    (["공동체", "community", "협력", "연대", "시민사회"], 2),
    (["인권", "human rights", "민권", "시민권", "노동권"], 2),
    (["보건", "공중보건", "health equity", "의료 격차"], 2),
    (["식량", "food security", "농업", "식량주권"], 2),

    # 일반 관련 (1점)
    (["혁신", "innovation", "스타트업", "기업가정신"], 1),
    (["경제", "economy", "노동", "일자리"], 1),
]

# ── 저자 신뢰도 가중치 ───────────────────────────────────────
AUTHOR_BOOST_KEYWORDS = ["교수", "박사", "연구원", "연구소", "저널리스트", "작가", "전문가", "소장", "원장"]


def _parse_date(date_str: str) -> str | None:
    """출판일 문자열 → 'YYYY-MM-DD' 정규화. 파싱 실패 시 None"""
    s = (date_str or "").strip()
    # 2026.03.25 / 2026.03
    m = re.match(r"(\d{4})\.(\d{1,2})(?:\.(\d{1,2}))?", s)
    if m:
        y, mo, d = m.group(1), m.group(2).zfill(2), (m.group(3) or "01").zfill(2)
        return f"{y}-{mo}-{d}"
    # Aug 11, 2026 / August 29, 2026
    m = re.match(
        r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{1,2}),?\s+(\d{4})",
        s, re.IGNORECASE
    )
    if m:
        months = {"jan":"01","feb":"02","mar":"03","apr":"04","may":"05","jun":"06",
                  "jul":"07","aug":"08","sep":"09","oct":"10","nov":"11","dec":"12"}
        mo = months[m.group(1)[:3].lower()]
        return f"{m.group(3)}-{mo}-{m.group(2).zfill(2)}"
    return None


def is_excluded(book: dict) -> tuple[bool, str]:
    """제외 여부 판단. (제외여부, 이유) 반환"""
    title     = book.get("도서명", "")
    publisher = book.get("출판사", "")
    category  = book.get("카테고리", "")
    date_str  = book.get("출판일", "")

    # 출판사 필터
    if publisher in EXCLUDE_PUBLISHERS:
        return True, f"수험서 출판사: {publisher}"

    # 제목 패턴 — 수험서
    for pattern in EXCLUDE_TITLE_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return True, f"수험서 제목: {pattern}"

    # 카테고리 필터 — 소설/잡지
    if category in EXCLUDE_CATEGORIES:
        return True, f"장르 제외: {category}"

    # 제목 패턴 — 소설
    for pattern in EXCLUDE_NOVEL_TITLE_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return True, f"소설 패턴: {pattern}"

    # 제목 패턴 — 잡지
    for pattern in EXCLUDE_MAGAZINE_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return True, f"잡지 패턴: {pattern}"

    # 제목/내용 키워드 — 완전 무관 주제
    content = book.get("책 내용", "")
    for kw in EXCLUDE_CONTENT_KEYWORDS:
        if kw in title or kw in content:
            return True, f"무관 주제: {kw}"

    # 순수 AI 기술서 제외 (사회적 맥락 없는 개발/코딩서)
    full_text = title + " " + content
    for pat in PURE_TECH_AI_PATTERNS:
        if re.search(pat, full_text, re.IGNORECASE):
            has_social = any(kw in full_text for kw in SOCIAL_CONTEXT_KEYWORDS)
            if not has_social:
                return True, f"순수 AI 기술서: {pat[:30]}"

    # 날짜 범위 필터 — 최근 N개월 이내만
    parsed = _parse_date(date_str)
    if parsed:
        cutoff = datetime.today() - timedelta(days=DATE_RANGE_MONTHS * 30)
        try:
            pub_dt = datetime.strptime(parsed, "%Y-%m-%d")
            if pub_dt < cutoff:
                return True, f"출판일 오래됨: {date_str}"
        except ValueError:
            pass

    return False, ""


def score_book(book: dict) -> int:
    """SV Book 주제 관련성 점수 계산 (1~5점)

    CSES 선정 도서 기준:
    - 전문가가 쓴 날카로운 시각의 교양서/전망서
    - AI×사회, 기후×경제, 인구×정책 등 교차 주제
    - 원론서/개론서가 아닌 구체적 thesis 제시
    """
    title = book.get("도서명", "")
    content = book.get("책 내용", "")
    full = (title + " " + content).lower()
    title_lower = title.lower()

    pts = 0

    # ── 1) 제목 주제 매칭 (0~2점) ──
    # 제목에 핵심 SV 키워드가 직접 등장하면 강한 신호
    TITLE_TIER1 = [  # 2점: 교차 주제 / CSES 핵심
        "사회적가치", "사회가치", "social value",
        "AI 시대", "AI와 사회", "AI와 인간", "인공지능과 인간",
        "AI 거버넌스", "AI 윤리", "알고리즘",
        "사회연대경제", "임팩트", "ESG",
        "기후위기", "기후변화", "탄소중립", "넷제로",
        "사회혁신", "경제민주화",
    ]
    TITLE_TIER2 = [  # 1점: 관련 주제
        "불평등", "인구", "저출생", "고령화", "인재",
        "거버넌스", "민주주의", "지정학", "패권", "국제질서",
        "에너지", "탄소", "지속가능", "다양성", "포용",
        "자본주의", "노동", "일자리", "미래사회", "미래",
        "인간", "로봇", "디지털", "전환", "혁신",
        "세계", "글로벌", "경제", "사회", "공동체",
        "기후", "환경", "생태", "여성", "젠더",
        "inequality", "climate", "sustainability", "democracy",
        "geopolitics", "future", "AI", "governance",
    ]
    t1_match = any(kw.lower() in title_lower for kw in TITLE_TIER1)
    t2_match = any(kw.lower() in title_lower for kw in TITLE_TIER2)
    if t1_match:
        pts += 2
    elif t2_match:
        pts += 1

    # ── 2) 내용 주제 깊이 (0~2점) ──
    THEME_GROUPS = [
        ["AI", "인공지능", "로봇", "알고리즘", "디지털", "자동화"],
        ["기후", "탄소", "환경", "에너지", "생태", "넷제로", "온난화"],
        ["불평등", "빈곤", "격차", "형평", "공정", "정의"],
        ["인구", "저출생", "고령화", "이주", "난민", "인구감소"],
        ["거버넌스", "민주주의", "정치", "정책", "제도", "시민"],
        ["경제", "자본주의", "노동", "일자리", "산업", "성장"],
        ["사회", "공동체", "연대", "복지", "돌봄", "인권", "문명"],
        ["지정학", "패권", "국제", "글로벌", "안보", "전쟁", "질서"],
    ]
    themes_hit = sum(
        1 for grp in THEME_GROUPS
        if any(kw in full for kw in grp)
    )
    if themes_hit >= 4:
        pts += 2
    elif themes_hit >= 2:
        pts += 1

    # ── 3) 저자 전문성 (0~1점) ──
    author_info = (book.get("비고 (저자 설명)", "") or "") + " " + (book.get("저자", "") or "")
    EXPERT_KEYWORDS = [
        "교수", "석좌교수", "박사", "연구원", "연구소", "소장", "원장",
        "CEO", "대표", "전문가", "저널리스트", "작가", "기자",
        "이사", "위원", "센터장", "학회",
        "professor", "PhD", "researcher", "director",
    ]
    if any(kw in author_info for kw in EXPERT_KEYWORDS):
        pts += 1

    # ── 4) 전망·논쟁서 보너스 (0~1점) ──
    THESIS_PATTERNS = [
        r"어떻게.*(될|바꾸|만드|할)",
        r"왜.*(않|못|없|실패|탈퇴|부족)",
        r"(의 미래|의 시대|의 탄생|의 종말|의 전쟁)",
        r"(을 바꾸|를 바꾸|을 만드|를 만드|이 온다|가 온다)",
        r"(무엇을|어디로|누가|무엇이).*(할|갈|될|인가|일까)",
        r"(넘어|너머|이후|다음|전환|대전환|응전)",
        r"(선언|선택|도전|혁명|위기|충격|전망|예보)",
        r"(사라지|무너지|붕괴|멸종|절벽|습격)",
    ]
    # 제목 또는 내용에서 thesis 패턴 매칭
    if any(re.search(pat, title) for pat in THESIS_PATTERNS):
        pts += 1
    elif any(re.search(pat, content[:100]) for pat in THESIS_PATTERNS):
        pts += 1

    # ── 5) 내용 SV 밀도 보너스 (0~1점) ──
    # 제목에 키워드가 없더라도, 내용에 SV 핵심어가 3개 이상이면 보정
    SV_DENSITY_KW = [
        "사회적가치", "탄소", "기후", "불평등", "ESG", "거버넌스",
        "인공지능", "AI", "민주주의", "에너지 전환", "지속가능",
        "인구", "사회혁신", "임팩트", "다양성", "공동체",
        "문명", "인류", "윤리", "공정", "연대",
    ]
    content_sv_hits = sum(1 for kw in SV_DENSITY_KW if kw.lower() in full)
    if content_sv_hits >= 3 and pts < 3:
        pts += 1

    # ── 6) 원론서·교과서·리포트 감점 (-1~-2점) ──
    TEXTBOOK_PATTERNS = [
        r"(의 이해|의 기초|의 원리|의 원론|의 개론|의 모든 것)",
        r"(입문|개론|원론|총론|통론|교과서|학개론|학원론)$",
        r"(큰글자책|큰글씨|대활자)",
        r"(제\d+판|개정판|증보판|\d+판$)",
        r"(유망\s*핵심\s*기술|시장\s*전망과\s*사업화|사업\s*분석|시장동향)",
        r"(중견기업용|산업\s*분석|실무\s*가이드|실무서|매뉴얼)",
        r"SDG.*ESG.*보고서",
        r"(경영보고서|지속가능.*보고서|보고서.*모든 것)",
        r"(건축기준|설계기준|시공기준|기술기준)",
    ]
    TEXTBOOK_CONTENT = [
        "교재", "강의", "학습목표", "연습문제", "학기",
        "수업", "커리큘럼", "교육과정", "학점",
    ]
    # 학술·전문 출판사 감점
    ACADEMIC_PUBS = {
        "커뮤니케이션북스", "한국학술정보", "박영사", "법문사", "율곡출판사",
        "교문사", "학지사", "청목출판사", "도서출판 오래", "진한엠앤비",
    }
    publisher = book.get("출판사", "")

    penalty = 0
    if any(re.search(pat, title) for pat in TEXTBOOK_PATTERNS):
        penalty += 2
    elif any(kw in content[:200] for kw in TEXTBOOK_CONTENT):
        penalty += 1
    # 학술 출판사
    if publisher in ACADEMIC_PUBS:
        penalty += 1
    # 키워드 나열형 제목 (A와 B, A·B·C 등 2개 이상 핵심어 조합)
    title_sv_count = sum(1 for kw in ["ESG", "SDG", "AI", "기후", "탄소", "거버넌스", "지속가능", "사회적"] if kw in title)
    if title_sv_count >= 3:
        penalty += 1
    # 저자 다수(외 7, 외 11 등) + 나열형 = 학술서
    author = book.get("저자", "")
    if re.search(r"외\s*\d+", author) and re.search(r"(와|과|·|,)", title):
        penalty += 1

    pts -= penalty
    return max(1, min(5, pts))


# ── 4대 카테고리 분류 ──────────────────────────────────────────
CATEGORY_RULES = [
    ("Tech & Future", [
        "AI", "인공지능", "로봇", "데이터", "디지털 전환", "디지털전환", "자동화",
        "알고리즘", "플랫폼", "기술 혁신", "기술혁신", "빅데이터", "사이버",
        "반도체", "퀀텀", "바이오테크", "미래 기술", "tech", "digital", "robot",
        "automation", "algorithm", "data", "cyber", "quantum",
    ]),
    ("ESG & Sustainability", [
        "ESG", "기후", "탄소", "넷제로", "순환경제", "지속가능", "생물다양성",
        "재생에너지", "에너지 전환", "탈탄소", "환경", "green", "climate",
        "carbon", "sustainability", "sustainable", "net zero", "biodiversity",
        "renewable", "ecology", "생태", "기업 책임", "공급망",
    ]),
    ("Social & Human", [
        "불평등", "인구", "저출생", "고령화", "세대", "다양성", "젠더", "여성",
        "노동", "일자리", "일의 미래", "빈곤", "이주", "난민", "공동체", "연대",
        "사회적 가치", "사회가치", "사회혁신", "인권", "복지", "돌봄", "민주주의",
        "inequality", "diversity", "labor", "poverty", "migration", "community",
        "social", "human rights", "welfare", "gender",
    ]),
    ("Geopolitics & Strategy", [
        "지정학", "패권", "국제질서", "공급망", "무역", "안보", "전쟁", "외교",
        "중국", "미국", "러시아", "유럽", "아시아", "글로벌", "다극", "제국",
        "geopolitics", "global", "supply chain", "trade", "security", "war",
        "diplomacy", "hegemony", "international",
    ]),
]


def assign_category(book: dict) -> str:
    """책 제목 + 내용으로 4대 카테고리 중 하나 배정"""
    text = (book.get("도서명", "") + " " + book.get("책 내용", "")).lower()
    scores = {}
    for cat_name, keywords in CATEGORY_RULES:
        scores[cat_name] = sum(1 for kw in keywords if kw.lower() in text)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "Social & Human"


def filter_and_score(books: list[dict], min_score: int = 3) -> list[dict]:
    """
    전체 도서 목록에서:
    1. 문제집/수험서 제거
    2. 주제 점수 계산
    3. min_score 미만 제거
    4. 점수 높은 순 정렬
    """
    results = []
    cnt = {"수험서": 0, "소설/잡지/취미": 0, "오래된책": 0, "무관주제": 0, "AI기술서": 0, "관련성낮음": 0}

    for book in books:
        excluded, reason = is_excluded(book)
        if excluded:
            if "수험서" in reason or "제목 패턴" in reason:
                cnt["수험서"] += 1
            elif "장르" in reason or "소설" in reason or "잡지" in reason:
                cnt["소설/잡지/취미"] += 1
            elif "출판일" in reason:
                cnt["오래된책"] += 1
            elif "무관 주제" in reason:
                cnt["무관주제"] += 1
            elif "AI 기술서" in reason:
                cnt["AI기술서"] += 1
            else:
                cnt["수험서"] += 1
            continue

        s = score_book(book)
        if s < min_score:
            cnt["관련성낮음"] += 1
            continue

        book = dict(book)
        book["_score"] = s
        book["_category"] = assign_category(book)
        results.append(book)

    results.sort(key=lambda b: b["_score"], reverse=True)

    print(f"  → 수험서 제외: {cnt['수험서']}건")
    print(f"  → 소설/잡지/취미 제외: {cnt['소설/잡지/취미']}건")
    print(f"  → 무관 주제 제외: {cnt['무관주제']}건")
    print(f"  → 순수 AI 기술서 제외: {cnt['AI기술서']}건")
    print(f"  → 오래된 책 제외: {cnt['오래된책']}건")
    print(f"  → 관련성 낮음 제외: {cnt['관련성낮음']}건")
    print(f"  → 최종 추천: {len(results)}건")

    return results
