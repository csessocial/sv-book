"""국회도서관 금주의 신간 스크래퍼 — 최근 3개월치"""

import re
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

SOURCE_NANET = "국회도서관"

LIST_URL   = "https://www.nanet.go.kr/datasearch/weeknewbook/selectWeekNewBookList.do"
DETAIL_URL = "https://www.nanet.go.kr/datasearch/weeknewbook/selectWeekNewBookDetail.do"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def _fetch_detail(search_seq: str) -> dict:
    """상세 페이지에서 서지정보 + 도서요약 반환"""
    resp = requests.post(DETAIL_URL, data={"searchSeq": search_seq}, headers=HEADERS, timeout=10)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    # 서지사항 (.book 텍스트 파싱)
    book_el = soup.select_one(".book")
    raw = book_el.get_text(" ", strip=True) if book_el else ""

    title  = _extract(r"^(.+?)\s*-\s*저자", raw) or ""
    author = _extract(r"저자\s*:\s*(.+?)\s*-", raw) or ""
    trans  = _extract(r"역자\s*:\s*(.+?)\s*-", raw) or ""
    pub    = _extract(r"발행사항\s*:\s*(.+?)\s*-", raw) or ""
    call   = _extract(r"청구기호\s*:\s*(.+?)(?:자세히보기|$)", raw) or ""

    # 출판사 / 출판연도 분리 ("리더스북 : 웅진씽크빅(2026)")
    publisher, pub_date = "", ""
    m = re.search(r"(.+?)\((\d{4})\)", pub)
    if m:
        publisher = m.group(1).strip().rstrip(":")
        pub_date  = m.group(2)

    # 도서요약: 첫 번째 .para 텍스트
    paras = soup.select(".para")
    summary = paras[0].get_text(strip=True) if paras else ""

    # 저자 + 역자 합치기
    author_full = author
    if trans:
        author_full = f"{author} (역: {trans})"

    return {
        "도서명": _clean_title(title),
        "저자": author_full,
        "책 내용": summary,
        "출판사": publisher,
        "출판일": pub_date,
        "청구기호": call.strip(),
    }


def _extract(pattern: str, text: str) -> str | None:
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


def _clean_title(title: str) -> str:
    """'(팀 버너스리,) 이것은 모두를 위한 것입니다' → '이것은 모두를 위한 것입니다'"""
    return re.sub(r"^\(.*?\)\s*", "", title).strip()


def _get_week_dates(months: int = 3) -> list[str]:
    """드롭다운에서 최근 N개월 이내 주차 날짜 목록 반환"""
    resp = requests.get(LIST_URL, headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")

    cutoff = datetime.today() - timedelta(days=months * 30)
    dates = []
    for opt in soup.select("select option"):
        val = opt.get("value", "").strip()
        if not val:
            continue
        try:
            dt = datetime.strptime(val, "%Y-%m-%d")
            if dt >= cutoff:
                dates.append(val)
        except ValueError:
            continue
    return dates


def _fetch_week(search_date: str) -> list[dict]:
    """특정 주차 신간 목록 + 상세 수집"""
    resp = requests.get(LIST_URL, params={"searchWeeks": search_date},
                        headers=HEADERS, timeout=15)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    return soup.select(".item")


def fetch_all_books() -> list[dict]:
    """금주의 신간 최근 3개월치 수집"""
    print(f"\n[국회도서관] 금주의 신간 수집 시작 (최근 3개월)")

    week_dates = _get_week_dates(months=3)
    print(f"  수집 대상 주차: {len(week_dates)}주")

    seen_seqs = set()
    all_items_by_week = []
    for date in week_dates:
        items = _fetch_week(date)
        for item in items:
            link_el = item.select_one(".detailLink")
            seq = link_el.get("data-search-seq", "") if link_el else ""
            if seq and seq not in seen_seqs:
                seen_seqs.add(seq)
                all_items_by_week.append(item)
        time.sleep(0.3)

    print(f"  총 {len(all_items_by_week)}건 (중복 제거 후)")

    books = []
    total = len(all_items_by_week)
    for i, item in enumerate(all_items_by_week, 1):
        link_el = item.select_one(".detailLink")
        if not link_el:
            continue

        seq   = link_el.get("data-search-seq", "")
        title_preview = item.select_one(".tit")
        title_text = title_preview.get_text(strip=True) if title_preview else seq
        img_el = item.select_one(".thum img")
        image_url = img_el.get("src", "") if img_el else ""

        print(f"  [{i}/{total}] {title_text[:30]}...")

        detail = _fetch_detail(seq)
        if not detail.get("도서명"):
            continue

        books.append({
            "매체명": SOURCE_NANET,
            "도서명": detail["도서명"],
            "저자": detail["저자"],
            "책 내용": detail["책 내용"],
            "출판사": detail["출판사"],
            "출판일": detail["출판일"],
            "카테고리": "",
            "비고 (저자 설명)": detail["청구기호"],
            "검색 키워드": "금주의신간",
            "링크": f"https://www.nanet.go.kr/datasearch/weeknewbook/selectWeekNewBookDetail.do?searchSeq={seq}",
            "이미지": image_url,
        })

        time.sleep(0.5)

    print(f"\n[국회도서관] 총 {len(books)}건 수집 완료 ({len(week_dates)}주치)")
    return books


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    books = fetch_all_books()
    for b in books[:5]:
        print(f"\n📚 {b['도서명']} / {b['저자']} ({b['출판일']})")
        print(f"   {b['책 내용'][:100]}...")
