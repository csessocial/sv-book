"""카카오 책 검색 API를 이용한 SV 관련 신간 수집 (네이버 책 API 종료 대체).

카카오 REST 키가 필요합니다. GitHub Actions Secrets 또는 환경변수 KAKAO_REST_KEY 로 주입.
키가 없으면 조용히 건너뜁니다(빈 리스트 반환).
"""

import time
from datetime import datetime, timedelta

import requests
import config

SOURCE_KAKAO = "카카오 책"
SEARCH_URL = "https://dapi.kakao.com/v3/search/book"


def _parse_date(dt: str) -> tuple[str, datetime | None]:
    """카카오 datetime(ISO8601, 예 '2026-05-01T00:00:00.000+09:00') → ('YYYY.MM.DD', dt)"""
    if not dt or len(dt) < 10:
        return "", None
    try:
        d = datetime.strptime(dt[:10], "%Y-%m-%d")
        return d.strftime("%Y.%m.%d"), d
    except ValueError:
        return "", None


def fetch_all_books() -> list[dict]:
    """SV 키워드로 카카오 책 검색 후 최근 3개월 신간 반환. 키 없으면 [] 반환."""
    key = getattr(config, "KAKAO_REST_KEY", "") or ""
    if not key:
        print("\n[카카오 책] KAKAO_REST_KEY 미설정 → 건너뜀")
        return []

    headers = {"Authorization": f"KakaoAK {key}"}
    cutoff = datetime.now() - timedelta(days=90)
    keywords = config.KEYWORDS_KO + config.KEYWORDS_EN

    all_books = []
    seen = set()
    print(f"\n[카카오 책] 신간 검색 시작")
    for i, kw in enumerate(keywords, 1):
        print(f"  [{i}/{len(keywords)}] '{kw}' 검색 중...")
        try:
            resp = requests.get(
                SEARCH_URL,
                headers=headers,
                params={"query": kw, "sort": "recency", "size": 30},
                timeout=8,
            )
            if resp.status_code != 200:
                print(f"    HTTP {resp.status_code}: {resp.text[:120]}")
                continue

            for item in resp.json().get("documents", []):
                title = (item.get("title") or "").strip()
                if not title or title in seen:
                    continue

                pub_str, pub_dt = _parse_date(item.get("datetime", ""))
                if pub_dt is None or pub_dt < cutoff:
                    continue

                seen.add(title)
                authors = item.get("authors") or []
                all_books.append({
                    "매체명": SOURCE_KAKAO,
                    "도서명": title,
                    "저자": ", ".join(authors),
                    "책 내용": (item.get("contents") or "")[:300],
                    "출판사": item.get("publisher", ""),
                    "출판일": pub_str,
                    "링크": item.get("url", ""),
                    "이미지": item.get("thumbnail", ""),
                    "검색 키워드": kw,
                })
        except Exception as e:
            print(f"    오류: {e}")

        time.sleep(0.15)

    print(f"\n[카카오 책] 총 {len(all_books)}건 수집 완료")
    return all_books


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    for b in fetch_all_books()[:10]:
        print(f"[{b['출판일']}] {b['도서명']} / {b['저자']}")
