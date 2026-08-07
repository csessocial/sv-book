# SV Book 인수인계 문서

CSES(사회적가치연구원) 관심 주제 신간 도서 큐레이션 사이트의 운영 안내서입니다.
새 편집자가 이 문서만 보고 사이트를 운영할 수 있도록 정리했습니다.

---

## 1. 이 사이트가 하는 일

여러 서점·도서관에서 신간을 자동 수집 → 사회적가치(SV) 관련성으로 필터링·채점
→ AI 요약 추가 → 웹페이지로 생성 → GitHub Pages로 배포합니다.

- **배포 주소(추정)**: https://csessocial.github.io/sv-book/
- **주제 4축**: Tech & Future / ESG & Sustainability / Social & Human / Geopolitics & Strategy

---

## 2. 전체 동작 흐름 (파이프라인)

```
[수집]  교보문고 · 국회도서관 · 네이버도서   (스크래퍼 3종)
   ↓
[필터·점수]  sv_filter.py  — 수험서·소설·종교·순수기술서 등 제거, 1~5점 채점
   ↓
[누적 저장]  sv_books_data.json  (기존 데이터에 신간만 추가, 옛 책 유지)
   ↓
[AI 요약]  summarizer.py — Claude가 2~3문장 요약 (API 키 있을 때만)
   ↓
[HTML 생성]  generate.py → SV_Book.html → index.html 로 복사
   ↓
[배포]  GitHub Pages (main 브랜치의 index.html)
```

---

## 3. 파일별 역할

| 파일 | 역할 |
|------|------|
| `generate.py` | **메인 실행 파일.** 수집→필터→요약→HTML 생성 총괄. `python generate.py`로 실행 |
| `sv_filter.py` | **편집자가 가장 자주 만지는 파일.** 제외 규칙 + 점수 로직 + 큐레이션 목록 |
| `config.py` | 검색 키워드, API 키 설정 |
| `kyobo_scraper.py` | 교보문고 수집기 |
| `nanet_scraper.py` | 국회도서관 "금주의 신간" 수집기 (최근 3개월) |
| `naver_scraper.py` | 네이버 도서 API 수집기 (최근 3개월) |
| `summarizer.py` | Claude API로 도서 요약 생성 |
| `index.html` | **배포되는 실제 사이트 (자동 생성물 — 직접 수정 금지)** |
| `SV_Book.html` | 생성 직후의 결과물 (자동 생성물 — 직접 수정 금지) |
| `sv_books_data.json` | 누적된 전체 도서 데이터 (자동 생성물) |
| `.github/workflows/update.yml` | 자동 실행 스케줄 정의 |

---

## 4. 사이트 업데이트(수집·배포) 방법

### 정기 자동 실행
- 매주 **월요일 오전 10시(KST)** 자동 수집·배포 (`.github/workflows/update.yml`의 cron)

### 수동 실행 (3가지 중 편한 방법)
1. **사이트의 "지금 실행" 버튼** — 본인 GitHub Personal Access Token을 입력하면 수집이 시작됨.
   약 10~15분 후 사이트를 새로고침하면 반영됨.
   (토큰 권한: 저장소 `workflow` dispatch 실행 권한 필요)
2. **GitHub 저장소 → Actions 탭 → "SV Book 자동 수집" → Run workflow** 버튼
3. **로컬 실행**: 저장소를 받은 뒤 아래 "로컬에서 실행하기" 참고

---

## 5. 편집자가 실제로 조정하는 것 ⭐

운영하면서 손대는 지점은 대부분 **`sv_filter.py`** 와 **`config.py`** 안에 있습니다.

### (1) 밀고 싶은 책 강제 노출 — `sv_filter.py`의 `CURATED_TITLES`
- 이 목록에 책 **제목(일부)**을 넣으면 알고리즘 점수를 무시하고 **무조건 5점 + 이달의 추천 후보**가 됩니다.
- 편집자가 직접 큐레이션하는 핵심 도구.

### (2) 걸러내고 싶은 책 강등 — `sv_filter.py`의 `DEMOTED_TITLES`
- 이 목록에 제목을 넣으면 **무조건 1점**으로 강등 (원론서·교과서·리포트 등).

### (3) 검색 주제 조정 — `config.py`의 `KEYWORDS_KO` / `KEYWORDS_EN`
- 어떤 키워드로 신간을 검색할지 결정. 관심 주제가 바뀌면 여기서 추가/삭제.

### (4) 제외 규칙 — `sv_filter.py`의 `EXCLUDE_*` 목록
- `EXCLUDE_PUBLISHERS`: 특정 출판사(수험서 등) 통째 제외
- `EXCLUDE_TITLE_PATTERNS` / `EXCLUDE_CATEGORIES` / `EXCLUDE_CONTENT_KEYWORDS`: 장르·주제 제외
- 예: 종교서, 소설, 아동·청소년서, 순수 코딩/기술서, 투자 상품서 등이 이미 제외됨

### (5) 점수 기준 — `sv_filter.py`의 `score_book()`
- 제목 주제 매칭 + 내용 깊이 + 저자 전문성 + 전망·논쟁서 여부 등을 종합해 1~5점 산정.
- 세부 가중치를 바꾸고 싶을 때만 건드리면 됩니다 (평소엔 위 (1)(2)로 충분).

---

## 6. API 키 / 시크릿 관리

> ⚠️ 실제 키 값은 이 문서(공개 저장소)에 적지 않습니다. 위치만 안내합니다.

| 키 | 위치 | 용도 |
|----|------|------|
| 네이버 도서 API (`NAVER_CLIENT_ID`, `NAVER_CLIENT_SECRET`) | `config.py` 상단 | 네이버 신간·책 소개 검색 |
| `ANTHROPIC_API_KEY` | GitHub 저장소 **Settings → Secrets and variables → Actions** | AI 요약(Claude) — 자동 실행 시 환경변수로 주입 |
| `NL_API_KEY` (국회도서관 Open API) | `config.py` | 현재 placeholder (`nanet_scraper`는 공개 웹페이지 스크래핑 방식이라 미사용) |

### 보안 권장사항
- 네이버 API 키가 현재 `config.py`에 하드코딩되어 있습니다. 저장소가 공개라면
  키가 노출된 상태이므로, 여유가 되면 **환경변수/Secrets로 이전**을 권장합니다.
- `ANTHROPIC_API_KEY`가 Secrets에 없으면 AI 요약이 생략되고 원문 설명만 표시됩니다.

---

## 7. 로컬에서 실행하기

```bash
# 1) 패키지 설치
pip install requests beautifulsoup4 lxml anthropic pdfplumber

# 2) (선택) AI 요약을 원하면 API 키 설정
export ANTHROPIC_API_KEY="your_key_here"     # Windows: set ANTHROPIC_API_KEY=...

# 3) 실행 — 수집·필터·요약·HTML 생성까지 자동
python generate.py

# 결과: SV_Book.html 생성 → 배포하려면 index.html 로 복사 후 커밋/푸시
cp SV_Book.html index.html
```

기본 수집 소스는 `generate.py` 하단의 `sources = ["kyobo", "nanet", "naver"]` 에서 조정합니다.

---

## 8. ⚠️ 운영 시 주의사항

1. **데이터는 누적됩니다.** `sv_books_data.json`에 신간만 추가되고 옛 책은 자동 삭제되지 않습니다.
   목록을 정리·리셋하려면 이 파일을 직접 편집해야 합니다.
2. **`index.html` / `SV_Book.html`은 직접 수정 금지.** 자동 생성물이라 다음 실행 시 덮어써집니다.
   디자인·레이아웃을 바꾸려면 `generate.py`의 `generate_html()` 함수를 수정하세요.
3. **배포 기준 브랜치는 `main`** 입니다. GitHub Pages가 `main`의 `index.html`을 서빙합니다.
4. AI 요약 없이 돌리면 요약 품질이 떨어집니다 — 정기 배포 전 Secrets 등록 여부를 확인하세요.

---

## 9. 화면 구성 (사이트 UI)

Hero 배너 · 이달의 추천 캐러셀 · 취향 미니 테스트(퀴즈) · 소스/키워드 필터
· 최신순/추천순 정렬 · 도서 카드 그리드
