"""네이버 도서 검색 API를 이용한 SV 관련 도서 수집"""

import requests
import time
from datetime import datetime, timedelta
import config


def fetch_all_books() -> list[dict]:
    """네이버 도서 API로 SV 키워드 검색 후 최근 3개월 신간 반환"""
    headers = {
        "X-Naver-Client-Id": config.NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": config.NAVER_CLIENT_SECRET,
    }
    cutoff = datetime.now() - timedelta(days=90)

    all_books = []
    seen = set()
    keywords = config.KEYWORDS_KO + config.KEYWORDS_EN

    print(f"\n[네이버 도서] 신간 검색 시작")
    for i, kw in enumerate(keywords, 1):
        print(f"  [{i}/{len(keywords)}] '{kw}' 검색 중...")
        try:
            params = {
                "query": kw,
                "display": 20,
                "start": 1,
                "sort": "date",
            }
            resp = requests.get(
                "https://openapi.naver.com/v1/search/book.json",
                headers=headers,
                params=params,
                timeout=8,
            )
            if resp.status_code != 200:
                continue

            items = resp.json().get("items", [])
            for item in items:
                title = item.get("title", "").replace("<b>", "").replace("</b>", "")
                if not title or title in seen:
                    continue

                pubdate = item.get("pubdate", "")
                if pubdate:
                    try:
                        pub_dt = datetime.strptime(pubdate, "%Y%m%d")
                        if pub_dt < cutoff:
                            continue
                        pub_str = pub_dt.strftime("%Y.%m.%d")
                    except ValueError:
                        pub_str = pubdate
                else:
                    continue

                seen.add(title)
                desc = item.get("description", "").replace("<b>", "").replace("</b>", "")
                author = item.get("author", "").replace("<b>", "").replace("</b>", "")
                publisher = item.get("publisher", "").replace("<b>", "").replace("</b>", "")

                all_books.append({
                    "매체명": "네이버 도서",
                    "도서명": title,
                    "저자": author,
                    "책 내용": desc[:300],
                    "출판사": publisher,
                    "출판일": pub_str,
                    "링크": item.get("link", ""),
                    "이미지": item.get("image", ""),
                    "검색 키워드": kw,
                })

        except Exception as e:
            print(f"    오류: {e}")

        time.sleep(0.15)

    print(f"\n[네이버 도서] 총 {len(all_books)}건 수집 완료")
    return all_books
