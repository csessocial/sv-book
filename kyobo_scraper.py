"""교보문고 신간 검색 스크래퍼"""

import re
import time
import requests
from bs4 import BeautifulSoup
from config import KEYWORDS_KO, KEYWORDS_EN, RESULTS_PER_KEYWORD, SOURCE_NL, NAVER_CLIENT_ID, NAVER_CLIENT_SECRET

SOURCE_KYOBO = "교보문고"

NAVER_BOOK_URL = "https://openapi.naver.com/v1/search/book.json"
_NAVER_HEADERS = {
    "X-Naver-Client-Id": NAVER_CLIENT_ID,
    "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
}

def _fetch_naver_info(title: str, author: str = "") -> dict:
    """네이버 책 API로 책 소개 + 이미지 URL 반환. 실패 시 빈 dict."""
    try:
        query = f"{title} {author}".strip()
        resp = requests.get(NAVER_BOOK_URL, headers=_NAVER_HEADERS,
                            params={"query": query, "display": 1}, timeout=5)
        if resp.status_code != 200:
            return {}
        items = resp.json().get("items", [])
        if not items:
            return {}
        item = items[0]
        desc = re.sub(r"<[^>]+>", "", item.get("description", "")).strip()
        image = item.get("image", "")
        return {"description": desc, "image": image}
    except Exception:
        return {}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}

SEARCH_URL = "https://search.kyobobook.co.kr/search"


def search_books(keyword: str, max_results: int = RESULTS_PER_KEYWORD) -> list[dict]:
    """단일 키워드로 교보문고 검색"""
    params = {
        "keyword": keyword,
        "gbCode": "KOR",   # 국내도서
        "target": "total",
    }

    try:
        resp = requests.get(SEARCH_URL, params=params, headers=HEADERS, timeout=10)
        resp.encoding = "utf-8"
        resp.raise_for_status()
    except Exception as e:
        print(f"  [오류] '{keyword}' 검색 실패: {e}")
        return []

    soup = BeautifulSoup(resp.text, "lxml")
    items = soup.select("li.prod_item")[:max_results]

    books = []
    for item in items:
        title_el   = item.select_one(".prod_info")
        author_el  = item.select_one(".author.rep")
        pub_el     = item.select_one(".prod_publish .text")
        date_el    = item.select_one(".prod_publish .date")
        desc_el    = item.select_one(".prod_desc_info") or item.select_one(".prod_desc")
        link_el    = item.select_one("a.prod_info")
        cat_el     = item.select_one(".prod_category")

        # 카테고리 추출 (제목 파싱 전에)
        category = cat_el.get_text(strip=True).strip("[]") if cat_el else ""

        title = ""
        if title_el:
            for span in title_el.select(".prod_category, .prod_label"):
                span.decompose()
            title = title_el.get_text(strip=True)

        if not title:
            continue

        author      = author_el.get_text(strip=True) if author_el else ""
        publisher   = pub_el.get_text(strip=True) if pub_el else ""
        pub_date    = _clean_date(date_el.get_text(strip=True)) if date_el else ""
        description = desc_el.get_text(strip=True) if desc_el else ""
        link        = link_el.get("href", "") if link_el else ""

        # 네이버 API로 책 소개 + 이미지 보완
        image_url = ""
        if len(description) < 50:
            naver = _fetch_naver_info(title, author)
            if naver.get("description"):
                description = naver["description"]
            image_url = naver.get("image", "")
        else:
            naver = _fetch_naver_info(title, author)
            image_url = naver.get("image", "")

        books.append({
            "매체명": SOURCE_KYOBO,
            "도서명": title,
            "저자": author,
            "책 내용": description,
            "출판사": publisher,
            "출판일": pub_date,
            "카테고리": category,
            "비고 (저자 설명)": "",
            "검색 키워드": keyword,
            "링크": link,
            "이미지": image_url,
        })

    return books


def _clean_date(raw: str) -> str:
    """'2026년 03월 25일' → '2026.03.25'"""
    raw = raw.strip()
    m = re.match(r"(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일", raw)
    if m:
        return f"{m.group(1)}.{int(m.group(2)):02d}.{int(m.group(3)):02d}"
    return raw


def fetch_all_books() -> list[dict]:
    """전체 키워드 검색 후 중복 제거하여 반환"""
    print(f"\n[교보문고] 신간 검색 시작")

    all_books = []
    seen_titles = set()

    all_keywords = KEYWORDS_KO + KEYWORDS_EN
    for i, kw in enumerate(all_keywords, 1):
        print(f"  [{i}/{len(all_keywords)}] '{kw}' 검색 중...")
        books = search_books(kw)

        for book in books:
            title = book["도서명"]
            if title and title not in seen_titles:
                seen_titles.add(title)
                all_books.append(book)

        time.sleep(0.8)  # 서버 부하 방지

    print(f"\n[교보문고] 총 {len(all_books)}건 수집 완료")
    return all_books


if __name__ == "__main__":
    books = fetch_all_books()
    print("\n[미리보기 - 상위 10건]")
    for b in books[:10]:
        print(f"  {b['도서명']} / {b['저자']} / {b['출판사']} ({b['출판일']})")
        if b['책 내용']:
            print(f"    → {b['책 내용'][:60]}...")
