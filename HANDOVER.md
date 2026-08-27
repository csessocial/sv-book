# SV Book 운영 매뉴얼 (담당자용)

CSES 관심 주제 신간 도서 큐레이션 사이트의 운영 안내서입니다.
**새 담당자는 이 문서만 보고 사이트를 운영할 수 있습니다.**

- **사이트 주소**: https://csessocial.github.io/sv-book/
- **저장소**: `csessocial/sv-book` (GitHub)
- **운영 주기**: 자동 주 1회 + 필요할 때 수동 실행 (권장: 2개월마다 점검·수동 실행)

---

## 1. 이 사이트가 하는 일

여러 서점·도서관에서 신간을 자동 수집 → 사회적가치(SV) 관련성으로 필터링·채점
→ (선택) AI 요약 추가 → 웹페이지 생성 → GitHub Pages로 자동 배포합니다.

- **수집 소스 3곳**: 교보문고 · 국회도서관(금주의 신간, 최근 3개월) · 카카오 책(네이버 대체, KAKAO_REST_KEY 필요)
- **주제 4축**: Tech & Future / ESG & Sustainability / Social & Human / Geopolitics & Strategy

---

## 2. 동작 흐름 (한눈에)

```
[수집] 교보문고 · 국회도서관 · 카카오 책
   ↓
[필터·점수] sv_filter.py — 수험서·소설·종교·순수기술서 등 제거, 관련도 1~5점
   ↓
[누적 저장] sv_books_data.json (기존 데이터에 신간만 추가, 옛 책 유지)
   ↓
[AI 요약] summarizer.py — Claude 2~3문장 요약 (API 키 있을 때만)
   ↓
[HTML 생성] generate.py → SV_Book.html → index.html 로 복사
   ↓
[배포] github-actions[bot]이 main에 커밋 → GitHub Pages 자동 반영
```

---

## 3. 📌 수집 실행하기 (가장 중요)

수집을 한 번 돌리면 위 전 과정이 자동으로 끝까지 진행됩니다. **약 6~13분** 후 사이트에 반영됩니다.

### 자동 실행
- 매주 **월요일 오전 10시(KST)** 자동 수집·배포. 담당자가 아무것도 안 해도 돌아갑니다.

### 수동 실행 (셋 중 편한 것)
1. **GitHub → Actions 탭 → "SV Book 자동 수집" → "Run workflow" 버튼** ← 가장 간단, 권장
2. **사이트의 "지금 실행" 버튼** — 본인 GitHub Personal Access Token 입력 시 시작
   (토큰 권한: 저장소 `workflow` 실행 권한)
3. **로컬 실행**: `python generate.py` (아래 6장 참고)

### ⚠️ 딱 하나 지킬 규칙: **한 번에 하나만 실행**
- 이미 수집이 도는 중에 또 실행하거나 버튼을 두 번 누르면, 나중 실행이
  **push 충돌로 실패**합니다. (사이트가 깨지진 않음 — 데이터는 누적이라 안전)
- 실행 후에는 **Actions 탭에서 초록 ✅ 로 끝나는 것만 확인**하고 기다리면 됩니다.

### 반영 확인
- 브라우저 **탭 제목**의 날짜(`SV Book — YYYY.MM.DD HH:MM`)가 방금 실행 시각이면 최신본.
- 안 바뀌면 **강력 새로고침(Ctrl+Shift+R)** — GitHub Pages는 최대 10분 캐싱합니다.

---

## 4. 편집자가 조정하는 것 ⭐

대부분 **`sv_filter.py`** 와 **`config.py`** 에서 조정합니다. 수정 후 3장의 "수동 실행"을 돌리면 반영됩니다.

### (1) 밀고 싶은 책 강제 노출 — `sv_filter.py` 의 `CURATED_TITLES`
- 이 목록에 책 **제목(일부)** 을 넣으면 알고리즘 점수를 무시하고 **무조건 5점 + 이달의 추천 후보**가 됩니다.
- 편집자가 직접 큐레이션하는 핵심 도구.

### (2) 걸러내고 싶은 책 강등 — `sv_filter.py` 의 `DEMOTED_TITLES`
- 이 목록에 제목을 넣으면 **무조건 1점**으로 강등 (원론서·교과서·리포트 등).

### (3) 검색 주제 조정 — `config.py` 의 `KEYWORDS_KO` / `KEYWORDS_EN`
- 어떤 키워드로 신간을 검색할지 결정. 관심 주제가 바뀌면 여기서 추가/삭제.

### (4) 제외 규칙 — `sv_filter.py` 의 `EXCLUDE_*` 목록
- `EXCLUDE_PUBLISHERS`: 특정 출판사(수험서 등) 통째 제외
- `EXCLUDE_TITLE_PATTERNS` / `EXCLUDE_CATEGORIES` / `EXCLUDE_CONTENT_KEYWORDS`: 장르·주제 제외
- (이미 종교서·소설·아동청소년서·순수 코딩서·투자상품서 등이 제외되어 있음)

---

## 5. "이달의 추천(캐러셀)" 동작 방식

- `generate.py` 의 `select_featured()` 가 자동 선정합니다.
- **기준: 최근 3개월 이내 발간 + 관련도 5점 신간만, 최대 10권.** (오래된 책은 안 올라옴)
  - 국회도서관 '금주의 신간'은 서지정보가 연도(`2026`)만 있어도, 애초에 최근 3개월 신간만 수집되므로 최신으로 인정합니다.
  - 최근 5점 신간이 10권보다 적으면 **있는 만큼만** 노출됩니다(보통 5~8권).
- **자연 물갈이**: 2개월마다 수집을 돌리면 지난 신간은 대부분 3개월이 지나 자동으로 빠지고 새 신간이 올라옵니다. 별도 작업 불필요.
- 같은 책의 소스별 중복(네이버본·국회도서관본)은 자동 제거됩니다.
- **특정 책을 이달의 추천에서 빼고 싶을 때** → `featured_history.json`(제외 목록)에 제목 추가.
  - 형식: JSON 배열, 부제·괄호 없이 핵심 제목만. 예: `["호모카르보", "질서의종말"]`
  - 여기 넣은 책은 이달의 추천에 다시 안 뜹니다(목록에서 지우면 다시 후보가 됨).
- 저자 소개 한 줄은 데이터가 있을 때만 표시됩니다(없으면 자동 숨김). 채우려면 아래 7장의 AI 요약을 켜야 합니다.

---

## 6. 로컬에서 실행하기 (선택)

```bash
# 1) 패키지 설치
pip install requests beautifulsoup4 lxml anthropic pdfplumber

# 2) (선택) AI 요약을 원하면 API 키 설정
export ANTHROPIC_API_KEY="your_key_here"     # Windows: set ANTHROPIC_API_KEY=...

# 3) 실행 — 수집·필터·요약·HTML 생성까지 자동
python generate.py

# 4) 배포하려면 결과를 index.html로 복사 후 커밋/푸시
cp SV_Book.html index.html
git add index.html sv_books_data.json featured_history.json
git commit -m "수동 업데이트"
git push
```

기본 수집 소스는 `generate.py` 하단 `sources = ["kyobo", "nanet", "kakao"]` 에서 조정합니다.

---

## 7. API 키 / 시크릿

| 키 | 위치 | 용도 |
|----|------|------|
| ~~네이버 도서 API~~ | `config.py` | **2026.07.31 서비스 종료 — 사용 불가** |
| 카카오 책 API (`KAKAO_REST_KEY`) | GitHub Secrets(또는 환경변수) | 네이버 대체. 신간·책소개·표지 검색. 카카오 개발자센터 무료 REST 키 |
| `ANTHROPIC_API_KEY` | GitHub **Settings → Secrets and variables → Actions** | AI 요약(Claude). 없으면 요약 생략, 원문 설명만 표시 |
| `NL_API_KEY` (국회도서관) | `config.py` | 현재 미사용(스크래핑 방식) |

- **AI 요약 켜는 법**: 저장소 Settings → Secrets and variables → Actions → New repository secret →
  Name `ANTHROPIC_API_KEY`, Secret = Anthropic 콘솔에서 발급한 키 → 저장. 다음 실행부터 요약(및 저자 소개)이 붙습니다.
- 보안 권장: `config.py`의 네이버 키가 저장소에 노출되어 있으므로, 여유 있을 때 Secrets/환경변수로 이전 권장.

---

## 8. ⚠️ 알려진 이슈 (확인 필요)

1. **네이버 도서 API 종료 → 카카오로 대체** — 네이버 '책' 검색 API가 2026.07.31 종료됨.
   카카오 책 스크래퍼로 교체 완료. **활성화하려면 카카오 REST 키가 필요합니다**:
   카카오 개발자센터(developers.kakao.com)에서 앱 생성 → REST API 키 발급(무료) →
   저장소 Secrets에 `KAKAO_REST_KEY` 로 등록 → 재수집. 키 없으면 카카오 소스는 조용히 건너뜀(교보·국회도서관은 정상).
2. **AI 요약·저자 소개(생성) 비활성** — `ANTHROPIC_API_KEY` 미등록. 켜면 요약·저자소개가 AI로 채워짐.
   (키 없이도 카카오/네이버 책소개에서 저자 문장은 추출되어 표시됨)

---

## 9. ⚠️ 운영 주의사항

1. **데이터는 누적됩니다.** `sv_books_data.json`에 신간만 추가되고 옛 책은 자동 삭제되지 않습니다.
   목록을 정리·리셋하려면 이 파일을 직접 편집해야 합니다.
2. **`index.html` / `SV_Book.html`은 직접 수정 금지.** 자동 생성물이라 다음 실행 시 덮어써집니다.
   디자인·레이아웃 변경은 `generate.py`의 `generate_html()` 함수를 수정하세요.
3. **배포 기준 브랜치는 `main`.** GitHub Pages가 `main`의 `index.html`을 서빙합니다.
4. 자동 생성물 3종(`index.html`, `sv_books_data.json`, `featured_history.json`)은 워크플로가 자동 커밋합니다.

---

## 10. 파일별 역할 (참고)

| 파일 | 역할 |
|------|------|
| `generate.py` | **메인 실행 파일.** 수집→필터→요약→HTML 생성 총괄 |
| `sv_filter.py` | **가장 자주 만지는 파일.** 제외 규칙 + 점수 로직 + 큐레이션 목록 |
| `config.py` | 검색 키워드, API 키 |
| `kyobo_scraper.py` / `nanet_scraper.py` / `naver_scraper.py` | 소스별 수집기 |
| `summarizer.py` | Claude API 도서 요약 |
| `index.html` | 배포되는 실제 사이트 (자동 생성물 — 직접 수정 금지) |
| `sv_books_data.json` | 누적 전체 도서 데이터 (자동 생성물) |
| `featured_history.json` | 이달의 추천 **제외 목록** (수동 관리) |
| `.github/workflows/update.yml` | 자동 실행 스케줄 + 배포 정의 |

---

## 11. 문제 해결 (Troubleshooting)

| 증상 | 원인·조치 |
|------|-----------|
| 실행이 실패(빨간 X)로 끝남 | Actions 탭 → 해당 run → 로그 확인. **push 충돌(non-fast-forward)** 이면 다른 실행과 겹친 것 → 잠시 후 한 번만 다시 실행 |
| 국회도서관만 빠졌다 | 국회도서관 서버 일시적 타임아웃. 코드가 자동으로 건너뛰고 나머지로 진행하니, 다음 실행 때 대개 정상 |
| 사이트에 신간이 안 보임 | ①강력 새로고침(Ctrl+Shift+R) ②탭 제목 날짜 확인 ③Actions에서 최근 run이 성공(✅)했는지 확인 |
| 이달의 추천이 비거나 너무 적음 | 최근 3개월 5점 신간이 적을 때 발생. `CURATED_TITLES`에 최근 신간을 추가하거나, `featured_history.json`(제외 목록)을 줄이면 늘어남 |
| 특정 책을 이달의 추천에서 빼고 싶음 | `featured_history.json`에 제목 추가 (5장 참고) |
