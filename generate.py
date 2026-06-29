"""SV Book - 데이터 수집 후 standalone HTML 생성"""

import sys
import os
import json
import webbrowser
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


import re as _re

def _norm_title(t):
    t = _re.split(r'[:\-—–|/]', t)[0]
    return _re.sub(r'[^가-힣a-zA-Z0-9]', '', t).lower()

def collect(sources: list[str]) -> list[dict]:
    all_books = []
    seen = set()

    SRC_LABELS = {"kyobo": "교보문고", "amazon": "Amazon", "nanet": "국회도서관", "naver": "네이버 도서"}
    steps = [s for s in ["kyobo", "amazon", "nanet", "naver"] if s in sources]
    for i, src in enumerate(steps, 1):
        print(f"[{i}/{len(steps)}] {SRC_LABELS[src]} 수집 중...")
        if src == "kyobo":
            from kyobo_scraper import fetch_all_books
        elif src == "amazon":
            from amazon_scraper import fetch_all_books
        elif src == "naver":
            from naver_scraper import fetch_all_books
        else:
            from nanet_scraper import fetch_all_books
        for b in fetch_all_books():
            key = _norm_title(b["도서명"])
            if key not in seen:
                seen.add(key)
                all_books.append(b)

    return all_books


def generate_html(books: list[dict], output_path: str, total_raw: int = 0):
    now = datetime.now().strftime("%Y.%m.%d %H:%M")
    data_json = json.dumps(books, ensure_ascii=False)
    filename_date = datetime.now().strftime("%Y%m%d")
    kw_list = json.dumps(
        list(dict.fromkeys(__import__('config').KEYWORDS_KO + __import__('config').KEYWORDS_EN)),
        ensure_ascii=False
    )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SV Book — {now}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
:root{{
  --ink:#1a1f36;
  --ink2:#2d3561;
  --ink3:#5a6282;
  --ink4:#9ba3c4;
  --bg:#f8f9ff;
  --bg2:#eef0fb;
  --border:#dde0f5;
  --accent:#4361ee;
  --accent-light:#e8ecff;
  --green:#10b981;
  --purple:#8b5cf6;
  --orange:#f59e0b;
  --red:#ef4444;
  --radius:14px;
  --serif:'Noto Sans KR',sans-serif;
  --sans:'Noto Sans KR',sans-serif;
}}
html{{scroll-behavior:smooth}}
body{{font-family:var(--sans);background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased;overflow-x:hidden}}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(24px)}}to{{opacity:1;transform:translateY(0)}}}}
@keyframes shimmer{{0%{{background-position:200% center}}100%{{background-position:-200% center}}}}

/* ── 네비게이션 ── */
.nav{{position:fixed;top:0;left:0;right:0;z-index:200;background:rgba(248,249,255,.93);backdrop-filter:blur(16px);border-bottom:1px solid rgba(221,224,245,.7);transition:box-shadow .2s}}
.nav.scrolled{{box-shadow:0 2px 24px rgba(67,97,238,.08)}}
.nav-inner{{max-width:1320px;margin:0 auto;padding:0 40px;height:60px;display:flex;align-items:center;gap:16px}}
.nav-logo{{font-size:1.15rem;font-weight:800;background:linear-gradient(135deg,#4361ee,#7c3aed);-webkit-background-clip:text;-webkit-text-fill-color:transparent;letter-spacing:-.3px;white-space:nowrap}}
.nav-meta{{font-size:.72rem;color:var(--ink4);font-weight:300;white-space:nowrap}}
.nav-actions{{display:flex;gap:8px;align-items:center;margin-left:auto}}
.nav-btn{{padding:6px 16px;border-radius:8px;font-family:var(--sans);font-size:.75rem;font-weight:600;cursor:pointer;border:1.5px solid var(--border);background:white;color:var(--ink2);transition:all .15s;white-space:nowrap}}
.nav-btn:hover{{background:var(--accent-light);border-color:var(--accent);color:var(--accent)}}
.nav-btn.primary{{background:linear-gradient(135deg,#4361ee,#7c3aed);color:white;border:none}}
.nav-btn.primary:hover{{opacity:.88}}

/* ── 히어로 ── */
.hero{{margin-top:60px;background:linear-gradient(135deg,#1a1f36 0%,#0f1d5e 40%,#1a1051 70%,#0d1117 100%);min-height:600px;position:relative;overflow:hidden}}
.hero-grid{{max-width:1320px;margin:0 auto;padding:0 40px;display:grid;grid-template-columns:1fr 1fr;min-height:600px}}
@media(max-width:860px){{.hero-grid{{grid-template-columns:1fr;min-height:auto}}}}
.hero-bg{{position:absolute;inset:0;pointer-events:none;overflow:hidden}}
.hero-bg::before{{content:'';position:absolute;top:-40%;right:-10%;width:600px;height:600px;border-radius:50%;background:radial-gradient(circle,rgba(99,102,241,.35) 0%,transparent 65%);animation:pulse 6s ease-in-out infinite}}
.hero-bg::after{{content:'';position:absolute;bottom:-30%;left:-5%;width:500px;height:500px;border-radius:50%;background:radial-gradient(circle,rgba(139,92,246,.25) 0%,transparent 65%);animation:pulse 8s ease-in-out infinite .5s}}
@keyframes pulse{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.08);opacity:.75}}}}
.hero-orb{{position:absolute;border-radius:50%;pointer-events:none}}
.hero-orb-1{{width:300px;height:300px;top:10%;right:5%;background:rgba(67,97,238,.2);filter:blur(60px);animation:float1 7s ease-in-out infinite}}
.hero-pick-btn{{display:inline-flex;align-items:center;gap:8px;margin-top:24px;padding:12px 24px;background:white;color:var(--ink);border-radius:12px;font-size:.85rem;font-weight:800;cursor:pointer;box-shadow:0 8px 28px rgba(0,0,0,.2);transition:all .25s;letter-spacing:-.2px}}
.hero-pick-btn:hover{{transform:translateY(-3px);box-shadow:0 14px 40px rgba(67,97,238,.3)}}
.hero-pick-arrow{{color:var(--accent);font-weight:700}}
@keyframes float1{{0%,100%{{transform:translateY(0) translateX(0)}}50%{{transform:translateY(-20px) translateX(10px)}}}}
@keyframes float2{{0%,100%{{transform:translateY(0)}}50%{{transform:translateY(15px)}}}}
.hero-content{{position:relative;z-index:1;padding:72px 0 80px 0;display:flex;flex-direction:column;justify-content:center;animation:fadeUp .6s ease both}}
@media(max-width:860px){{.hero-content{{padding:48px 0}}}}
.hero-eyebrow{{font-size:.67rem;font-weight:700;letter-spacing:3.5px;text-transform:uppercase;background:linear-gradient(90deg,#7dd3fc,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:18px;display:flex;align-items:center;gap:10px}}
.hero-eyebrow::before{{content:'';width:28px;height:2px;background:linear-gradient(90deg,#7dd3fc,#a78bfa);border-radius:2px;flex-shrink:0}}
.hero-title{{font-size:2.7rem;font-weight:800;color:white;line-height:1.2;letter-spacing:-.6px;margin-bottom:18px;text-shadow:0 2px 20px rgba(0,0,0,.3)}}
@media(max-width:1100px){{.hero-title{{font-size:2.1rem}}}}
.hero-desc{{font-size:.88rem;color:rgba(255,255,255,.58);line-height:1.9;font-weight:300;max-width:400px;margin-bottom:32px}}
.hero-cats{{display:flex;flex-wrap:wrap;gap:8px}}
.hero-cat{{padding:6px 14px;border-radius:20px;font-size:.73rem;font-weight:600;border:1px solid rgba(255,255,255,.15);color:rgba(255,255,255,.75);cursor:pointer;transition:all .2s;background:rgba(255,255,255,.05)}}
.hero-cat:hover,.hero-cat.active{{color:white;border-color:rgba(255,255,255,.45);background:rgba(255,255,255,.12)}}
.hero-cat[data-cat="Tech & Future"].active{{background:rgba(139,92,246,.35);border-color:#a78bfa}}
.hero-cat[data-cat="ESG & Sustainability"].active{{background:rgba(16,185,129,.3);border-color:#6ee7b7}}
.hero-cat[data-cat="Social & Human"].active{{background:rgba(239,68,68,.3);border-color:#fca5a5}}
.hero-cat[data-cat="Geopolitics & Strategy"].active{{background:rgba(245,158,11,.3);border-color:#fcd34d}}
.hero-visual{{position:relative;z-index:1;display:flex;align-items:center;justify-content:center;padding:40px 0 60px 0;animation:fadeUp .7s .15s ease both}}
@media(max-width:860px){{.hero-visual{{display:none}}}}
/* ── 캐러셀 ── */
.carousel{{position:relative;width:480px;height:420px}}
.carousel-track{{position:relative;width:100%;height:100%}}
.c-slide{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:22px;opacity:0;transition:opacity .45s,transform .45s;pointer-events:none;transform:translateX(30px)}}
.c-slide.active{{opacity:1;transform:translateX(0);pointer-events:auto}}
.c-slide.exit{{opacity:0;transform:translateX(-30px)}}
.c-book-main{{flex-shrink:0;filter:drop-shadow(0 28px 40px rgba(0,0,0,.55))}}
.c-book-main img{{width:200px;height:300px;border-radius:10px;display:block;object-fit:cover;transition:transform .35s;border:1px solid rgba(255,255,255,.1)}}
.c-book-main:hover img{{transform:translateY(-8px) rotate(-1.5deg)}}
.c-info{{flex:1;min-width:0}}
.c-rank{{font-size:.6rem;font-weight:800;letter-spacing:2.5px;text-transform:uppercase;background:linear-gradient(90deg,#7dd3fc,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px}}
.c-title{{font-size:1rem;font-weight:800;color:white;line-height:1.38;margin-bottom:6px}}
.c-author{{font-size:.74rem;color:rgba(255,255,255,.65);margin-bottom:10px;font-weight:400}}
.c-desc{{font-size:.76rem;color:rgba(255,255,255,.82);line-height:1.72;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;font-weight:400}}
.c-bio{{font-size:.72rem;color:#c4b5fd;line-height:1.65;margin-top:10px;font-weight:500;padding:8px 12px;background:rgba(139,92,246,.15);border-left:3px solid #a78bfa;border-radius:0 8px 8px 0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}}
.c-link{{display:inline-flex;align-items:center;gap:4px;margin-top:14px;font-size:.71rem;font-weight:700;color:white;text-decoration:none;background:linear-gradient(135deg,rgba(67,97,238,.5),rgba(124,58,237,.5));border:1px solid rgba(255,255,255,.2);padding:5px 14px;border-radius:20px;transition:all .22s;backdrop-filter:blur(4px)}}
.c-link:hover{{background:linear-gradient(135deg,rgba(67,97,238,.75),rgba(124,58,237,.75));border-color:rgba(255,255,255,.4)}}
/* 화살표 + 인디케이터 */
.carousel-nav{{position:absolute;bottom:-44px;left:0;right:0;display:flex;align-items:center;justify-content:center;gap:16px}}
.c-arrow{{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:white;width:34px;height:34px;border-radius:50%;cursor:pointer;font-size:1rem;display:flex;align-items:center;justify-content:center;transition:all .2s;flex-shrink:0;backdrop-filter:blur(6px)}}
.c-arrow:hover{{background:rgba(255,255,255,.18);border-color:rgba(255,255,255,.4)}}
.c-dots{{display:flex;gap:6px;align-items:center}}
.c-dot{{width:6px;height:6px;border-radius:50%;background:rgba(255,255,255,.28);cursor:pointer;transition:all .22s}}
.c-dot.active{{background:white;width:20px;border-radius:3px}}

/* ── 소개 배너 ── */
.intro{{background:linear-gradient(180deg,#f0f2ff 0%,#f8f9ff 100%);border-bottom:1px solid var(--border);padding:0}}
.intro-inner{{max-width:1320px;margin:0 auto;padding:48px 40px;display:grid;grid-template-columns:auto 1fr;gap:60px;align-items:start}}
@media(max-width:900px){{.intro-inner{{grid-template-columns:1fr;gap:32px}}}}
.intro-label{{font-size:.67rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--accent);margin-bottom:12px}}
.intro-heading{{font-size:1.6rem;font-weight:800;color:var(--ink);line-height:1.35;letter-spacing:-.4px;margin-bottom:12px;white-space:nowrap}}
.intro-sub{{font-size:.83rem;color:var(--ink3);line-height:1.8;font-weight:300;max-width:340px}}
.intro-cats{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}
.icat{{display:flex;align-items:flex-start;gap:12px;padding:16px 18px;border-radius:12px;border:1.5px solid var(--border);transition:all .2s;cursor:pointer;background:white}}
.icat:hover{{transform:translateY(-3px);box-shadow:0 8px 24px rgba(67,97,238,.1)}}
.icat-tech{{--c:#8b5cf6}}.icat-esg{{--c:#10b981}}.icat-social{{--c:#ef4444}}.icat-geo{{--c:#f59e0b}}
.icat:hover{{border-color:var(--c)}}
.icat-icon{{font-size:1.4rem;flex-shrink:0}}
.icat-name{{font-size:.8rem;font-weight:700;color:var(--ink);margin-bottom:3px}}
.icat-desc{{font-size:.71rem;color:var(--ink4);line-height:1.55;font-weight:300}}

/* ── 툴바 (sticky) ── */
.toolbar-sticky{{position:sticky;top:60px;z-index:100;background:rgba(248,249,255,.96);backdrop-filter:blur(12px);border-bottom:1px solid var(--border)}}
.toolbar-inner{{max-width:1320px;margin:0 auto;padding:0 40px;display:flex;align-items:center;gap:0;overflow-x:auto}}
.cat-tab{{padding:14px 20px;font-size:.8rem;font-weight:500;color:var(--ink4);border:none;background:none;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-1px;transition:all .18s;font-family:var(--sans);white-space:nowrap;flex-shrink:0}}
.cat-tab:hover{{color:var(--ink2)}}
.cat-tab.active{{color:var(--ink);font-weight:700;border-bottom-color:var(--accent)}}
.cat-tab[data-cat="Tech & Future"].active{{color:var(--purple);border-bottom-color:var(--purple)}}
.cat-tab[data-cat="ESG & Sustainability"].active{{color:var(--green);border-bottom-color:var(--green)}}
.cat-tab[data-cat="Social & Human"].active{{color:var(--red);border-bottom-color:var(--red)}}
.cat-tab[data-cat="Geopolitics & Strategy"].active{{color:var(--orange);border-bottom-color:var(--orange)}}
.toolbar-sep{{width:1px;height:20px;background:var(--border);flex-shrink:0;margin:0 8px}}
.search-wrap{{flex:1;min-width:180px;max-width:280px;position:relative;margin-left:auto}}
.search-wrap input{{width:100%;padding:7px 12px 7px 34px;border:1.5px solid var(--border);border-radius:8px;font-size:.8rem;font-family:var(--sans);outline:none;color:var(--ink);transition:all .15s;background:white}}
.search-wrap input:focus{{border-color:var(--accent);box-shadow:0 0 0 3px rgba(67,97,238,.1)}}
.search-wrap svg{{position:absolute;left:10px;top:50%;transform:translateY(-50%);color:var(--ink4);pointer-events:none}}
.fsel{{padding:7px 12px;border:1.5px solid var(--border);border-radius:8px;font-size:.78rem;font-family:var(--sans);background:white;color:var(--ink);cursor:pointer;outline:none;flex-shrink:0}}

/* ── 통계 + 정렬 바 ── */
.meta-bar{{max-width:1320px;margin:0 auto;padding:16px 40px 0;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px}}
.meta-count{{font-size:.78rem;color:var(--ink3)}}
.meta-count b{{color:var(--accent);font-weight:700}}
.sort-group{{display:flex;gap:6px;align-items:center}}
.sort-lbl{{font-size:.72rem;color:var(--ink4)}}
.sort-btn{{padding:4px 14px;border-radius:20px;border:1.5px solid var(--border);background:white;font-size:.72rem;font-family:var(--sans);color:var(--ink3);cursor:pointer;transition:all .15s}}
.sort-btn:hover{{border-color:var(--accent);color:var(--accent)}}
.sort-btn.active{{background:var(--accent);color:white;border-color:var(--accent)}}

/* ── 카드 그리드 ── */
.grid-wrap{{max-width:1320px;margin:0 auto;padding:20px 40px 40px}}
.book-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:28px}}
@media(max-width:900px){{.book-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:500px){{.book-grid{{grid-template-columns:1fr}}}}
/* ── 페이지네이션 ── */
.pagination{{display:flex;align-items:center;justify-content:center;gap:6px;padding:32px 0 64px}}
.pg-btn{{min-width:36px;height:36px;padding:0 10px;border-radius:8px;border:1.5px solid var(--border);background:white;color:var(--ink3);font-size:.82rem;font-family:var(--sans);cursor:pointer;transition:all .18s;display:flex;align-items:center;justify-content:center}}
.pg-btn:hover{{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}}
.pg-btn.active{{background:linear-gradient(135deg,#4361ee,#7c3aed);color:white;border-color:transparent;font-weight:700;box-shadow:0 4px 14px rgba(67,97,238,.35)}}
.pg-btn:disabled{{opacity:.3;cursor:default}}
.pg-ellipsis{{color:var(--ink4);font-size:.82rem;padding:0 4px}}

/* 카드 — 가로 레이아웃 (표지 왼쪽, 텍스트 오른쪽) */
.book-card{{background:white;border-radius:var(--radius);border:1px solid var(--border);display:flex;flex-direction:row;opacity:0;transform:translateY(24px);transition:opacity .45s,transform .45s,box-shadow .25s,border-color .25s;overflow:hidden}}
.book-card.visible{{opacity:1;transform:translateY(0)}}
.book-card:hover{{box-shadow:0 16px 48px rgba(67,97,238,.13);border-color:rgba(67,97,238,.25);transform:translateY(-3px)}}
.cover-wrap{{position:relative;overflow:hidden;flex-shrink:0;width:100px;background:#eef0fb}}
.cover-wrap img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .45s ease}}
.book-card:hover .cover-wrap img{{transform:scale(1.07)}}
.cover-overlay{{position:absolute;inset:0;background:linear-gradient(to right,transparent 40%,rgba(26,31,54,.5));opacity:0;transition:opacity .3s}}
.book-card:hover .cover-overlay{{opacity:1}}
.overlay-link{{position:absolute;bottom:8px;left:50%;transform:translateX(-50%) translateY(4px);opacity:0;transition:all .22s;white-space:nowrap;background:white;color:var(--accent);font-size:.66rem;font-weight:700;padding:4px 12px;border-radius:20px;text-decoration:none}}
.book-card:hover .overlay-link{{opacity:1;transform:translateX(-50%) translateY(0)}}
.badge-new{{position:absolute;top:6px;left:4px;background:linear-gradient(135deg,#ef4444,#f97316);color:white;font-size:.55rem;font-weight:700;padding:2px 6px;border-radius:4px;letter-spacing:.6px}}
.cat-pill{{position:absolute;bottom:6px;left:4px;font-size:.56rem;font-weight:700;padding:2px 7px;border-radius:20px;letter-spacing:.2px}}
.cp-tech{{background:linear-gradient(135deg,rgba(139,92,246,.92),rgba(99,102,241,.92));color:white}}
.cp-esg{{background:linear-gradient(135deg,rgba(16,185,129,.9),rgba(5,150,105,.9));color:white}}
.cp-social{{background:linear-gradient(135deg,rgba(239,68,68,.88),rgba(220,38,38,.88));color:white}}
.cp-geo{{background:linear-gradient(135deg,rgba(245,158,11,.9),rgba(217,119,6,.9));color:white}}
.src-dot{{position:absolute;top:6px;right:4px;font-size:.54rem;font-weight:600;padding:2px 6px;border-radius:4px;background:rgba(255,255,255,.9);color:var(--ink3)}}

.book-body{{padding:14px 14px 14px 12px;flex:1;min-width:0;display:flex;flex-direction:column;gap:6px}}
.book-title{{font-size:.84rem;font-weight:700;color:var(--ink);line-height:1.4;letter-spacing:-.1px}}
.book-title a{{color:inherit;text-decoration:none}}
.book-title a:hover{{color:var(--accent)}}
.book-meta{{font-size:.66rem;color:var(--ink4);display:flex;gap:4px;flex-wrap:wrap;align-items:center;font-weight:300}}
.meta-sep{{opacity:.3}}
.book-desc{{font-size:.72rem;color:var(--ink3);line-height:1.7;flex:1;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;font-weight:300}}
.book-desc.expanded{{display:block}}
.book-footer{{display:flex;align-items:center;justify-content:space-between;padding-top:8px;border-top:1px solid var(--border);margin-top:auto}}
.score-badge{{font-size:.63rem;font-weight:700;color:var(--accent);background:var(--accent-light);padding:2px 8px;border-radius:20px}}
.toggle-btn{{font-size:.67rem;color:var(--accent);cursor:pointer;font-weight:600;background:none;border:none;font-family:var(--sans);padding:0}}
.toggle-btn:hover{{text-decoration:underline}}

/* ── 빈 상태 ── */
.empty{{grid-column:1/-1;text-align:center;padding:100px 20px}}
.empty-icon{{font-size:3rem;opacity:.25;margin-bottom:16px}}
.empty p{{font-size:.88rem;color:var(--ink4);font-weight:300}}

/* ── 모달 ── */
.modal-bg{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:500;align-items:center;justify-content:center;backdrop-filter:blur(4px)}}
.modal-bg.show{{display:flex}}
.modal{{background:white;border-radius:16px;padding:32px 36px;max-width:460px;width:90%;box-shadow:0 24px 80px rgba(0,0,0,.18);animation:modalIn .2s ease}}
@keyframes modalIn{{from{{opacity:0;transform:translateY(12px)}}to{{opacity:1;transform:translateY(0)}}}}
.modal h2{{font-family:var(--serif);font-size:1.1rem;font-weight:700;color:var(--ink);margin-bottom:8px}}
.modal p{{font-size:.82rem;color:var(--ink3);line-height:1.7;margin-bottom:20px;font-weight:300}}
.token-label{{font-size:.74rem;font-weight:600;color:var(--ink2);display:block;margin-bottom:6px}}
.token-input{{width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:6px;font-size:.82rem;font-family:var(--sans);outline:none;margin-bottom:16px;transition:border .15s}}
.token-input:focus{{border-color:var(--accent)}}
.modal-status{{font-size:.79rem;padding:10px 14px;border-radius:8px;margin-bottom:16px;display:none;line-height:1.5}}
.modal-status.ok{{background:#dafbe1;color:#1a7f37}}
.modal-status.err{{background:#ffebe9;color:#cf222e}}
.modal-btns{{display:flex;gap:10px;justify-content:flex-end}}
.mbtn{{padding:8px 20px;border-radius:6px;font-family:var(--sans);font-size:.8rem;font-weight:600;cursor:pointer;border:1px solid var(--border);transition:all .15s}}
.mbtn-primary{{background:var(--ink);color:white;border-color:var(--ink)}}
.mbtn-primary:hover{{background:var(--ink2)}}
.mbtn-secondary{{background:white;color:var(--ink2)}}
.mbtn-secondary:hover{{background:var(--bg2)}}

/* ── 원장님 Pick 모달 ── */
.pick-modal{{background:white;border-radius:20px;max-width:600px;width:92%;max-height:88vh;overflow-y:auto;box-shadow:0 24px 80px rgba(0,0,0,.2);animation:modalIn .25s ease both;position:relative}}
.pick-modal-close{{position:absolute;top:14px;right:14px;z-index:10;background:rgba(0,0,0,.3);color:white;border:none;width:32px;height:32px;border-radius:50%;font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:background .15s}}
.pick-modal-close:hover{{background:rgba(0,0,0,.5)}}
.pick-banner{{height:180px;background:linear-gradient(135deg,#fef3c7 0%,#a7f3d0 50%,#bfdbfe 100%);display:flex;align-items:flex-end;position:relative;border-radius:20px 20px 0 0;overflow:hidden}}
.pick-banner-img{{position:absolute;inset:0;object-fit:cover;width:100%;height:100%}}
.pick-banner-ov{{padding:20px 28px;width:100%;background:linear-gradient(to top,rgba(0,0,0,.55) 0%,rgba(0,0,0,.2) 60%,transparent 100%);position:relative;z-index:2}}
.pick-banner-t{{font-size:1.3rem;font-weight:800;color:white;text-shadow:0 2px 8px rgba(0,0,0,.3)}}
.pick-banner-s{{font-size:.78rem;color:rgba(255,255,255,.85);font-weight:300;margin-top:4px}}
/* 캐러셀 1권씩 */
.pick-carousel{{display:flex;align-items:center;gap:12px;padding:20px 20px 8px}}
.pick-ca-arr{{width:36px;height:36px;border-radius:50%;border:1.5px solid var(--border);background:white;color:var(--ink3);font-size:1rem;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:all .15s}}
.pick-ca-arr:hover{{border-color:var(--accent);color:var(--accent);background:var(--accent-light)}}
.pick-ca-card{{flex:1;display:flex;gap:16px;align-items:flex-start;padding:16px;border-radius:14px;background:var(--bg2);border:1px solid var(--border);min-height:140px}}
.pick-ca-img{{width:80px;height:115px;border-radius:8px;object-fit:cover;flex-shrink:0;box-shadow:0 4px 12px rgba(0,0,0,.1)}}
.pick-ca-info{{flex:1;min-width:0}}
.pick-ca-title{{font-size:.92rem;font-weight:800;color:var(--ink);margin-bottom:4px}}
.pick-ca-meta{{font-size:.7rem;color:var(--ink4);margin-bottom:6px;font-weight:300}}
.pick-ca-bio{{font-size:.68rem;color:var(--purple);font-weight:500;margin-bottom:6px}}
.pick-ca-desc{{font-size:.72rem;color:var(--ink3);line-height:1.6;font-weight:300;margin-bottom:8px}}
.pick-ca-link{{font-size:.68rem;font-weight:700;color:var(--accent);text-decoration:none}}
.pick-ca-link:hover{{text-decoration:underline}}
.pick-ca-dots{{display:flex;gap:5px;justify-content:center;padding:8px 0 16px}}
.pick-ca-dot{{width:6px;height:6px;border-radius:50%;background:var(--border);cursor:pointer;transition:all .2s}}
.pick-ca-dot.active{{background:var(--accent);width:16px;border-radius:3px}}
/* 전체 리스트 */
.pick-list-hdr{{font-size:.78rem;font-weight:700;color:var(--ink3);padding:0 24px 8px;border-top:1px solid var(--border);margin-top:4px;padding-top:16px}}
.pick-item{{display:flex;gap:10px;align-items:center;padding:10px 24px;border-bottom:1px solid var(--bg2);transition:background .12s}}
.pick-item:hover{{background:var(--bg2)}}
.pick-num{{width:20px;height:20px;border-radius:50%;background:linear-gradient(135deg,#4361ee,#7c3aed);color:white;font-size:.6rem;font-weight:800;display:flex;align-items:center;justify-content:center;flex-shrink:0}}
.pick-sm-img{{width:32px;height:46px;border-radius:4px;object-fit:cover;flex-shrink:0}}
.pick-sm-info{{flex:1;min-width:0}}
.pick-sm-title{{font-size:.78rem;font-weight:700;color:var(--ink)}}
.pick-sm-meta{{font-size:.64rem;color:var(--ink4);font-weight:300}}
.pick-sm-link{{font-size:.62rem;font-weight:700;color:var(--accent);text-decoration:none;flex-shrink:0}}
.pick-list-pg{{display:flex;gap:5px;justify-content:center;padding:14px 0 20px}}
.pick-pg-btn{{min-width:28px;height:28px;padding:0 8px;border-radius:6px;border:1px solid var(--border);background:white;font-size:.75rem;font-family:var(--sans);color:var(--ink3);cursor:pointer;display:flex;align-items:center;justify-content:center;transition:all .15s}}
.pick-pg-btn:hover{{border-color:var(--accent);color:var(--accent)}}
.pick-pg-btn.active{{background:var(--accent);color:white;border-color:var(--accent)}}

/* ── 사이트 가이드 ── */
.guide-section{{background:linear-gradient(180deg,var(--bg) 0%,#eef0fb 100%);padding:0;border-top:1px solid var(--border)}}
.guide-inner{{max-width:1320px;margin:0 auto;padding:56px 40px 64px}}
.guide-header{{text-align:center;margin-bottom:36px}}
.guide-label{{font-size:.65rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--accent);margin-bottom:10px}}
.guide-title{{font-size:1.35rem;font-weight:800;color:var(--ink)}}
.guide-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}}
@media(max-width:900px){{.guide-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:560px){{.guide-grid{{grid-template-columns:1fr}}}}
.guide-card{{background:white;border-radius:14px;border:1px solid var(--border);padding:22px 20px;transition:all .2s}}
.guide-card:hover{{border-color:var(--accent);box-shadow:0 8px 24px rgba(67,97,238,.08);transform:translateY(-2px)}}
.guide-card-icon{{font-size:1.5rem;margin-bottom:10px}}
.guide-card-title{{font-size:.82rem;font-weight:700;color:var(--ink);margin-bottom:8px}}
.guide-card-desc{{font-size:.73rem;color:var(--ink3);line-height:1.75;font-weight:300}}
.guide-card-desc b{{color:var(--ink2);font-weight:600}}

/* ── 미니 테스트 (플로팅) ── */
.quiz-fab{{position:fixed;bottom:28px;right:28px;z-index:400;border-radius:28px;border:none;background:linear-gradient(135deg,#4361ee,#7c3aed);color:white;font-size:.82rem;font-weight:700;cursor:pointer;box-shadow:0 6px 24px rgba(67,97,238,.4);display:flex;align-items:center;gap:8px;padding:0 20px;height:52px;transition:all .25s;font-family:var(--sans);animation:fabBounce 2s ease-in-out infinite 3s}}
.quiz-fab:hover{{transform:scale(1.04);box-shadow:0 10px 32px rgba(67,97,238,.5)}}
.quiz-fab.hide{{display:none}}
@keyframes fabBounce{{0%,100%{{transform:translateY(0)}}15%{{transform:translateY(-6px)}}30%{{transform:translateY(0)}}}}
.quiz-fab-tip{{position:fixed;bottom:92px;right:28px;z-index:400;background:white;border-radius:10px;padding:10px 16px;box-shadow:0 4px 20px rgba(0,0,0,.12);font-size:.78rem;font-weight:600;color:var(--ink);white-space:nowrap;animation:fadeUp .3s ease both;pointer-events:none}}
.quiz-fab-tip::after{{content:'';position:absolute;bottom:-6px;right:22px;width:12px;height:12px;background:white;transform:rotate(45deg);box-shadow:2px 2px 4px rgba(0,0,0,.05)}}

.quiz-popup{{position:fixed;bottom:28px;right:28px;z-index:450;width:400px;max-height:520px;background:white;border-radius:20px;box-shadow:0 20px 60px rgba(26,31,54,.2);display:none;flex-direction:column;overflow:hidden;animation:quizIn .25s ease both}}
.quiz-popup.show{{display:flex}}
@keyframes quizIn{{from{{opacity:0;transform:translateY(16px) scale(.96)}}to{{opacity:1;transform:translateY(0) scale(1)}}}}
@media(max-width:460px){{.quiz-popup{{width:calc(100vw - 24px);right:12px;bottom:12px}}}}
.quiz-popup-header{{display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid var(--border);flex-shrink:0}}
.quiz-popup-title{{font-size:.85rem;font-weight:800;color:var(--ink)}}
.quiz-popup-close{{background:none;border:none;font-size:1.1rem;color:var(--ink4);cursor:pointer;padding:4px;transition:color .15s}}
.quiz-popup-close:hover{{color:var(--ink)}}
.quiz-popup-body{{flex:1;overflow-y:auto;padding:24px 20px;text-align:center}}
.quiz-label{{font-size:.65rem;font-weight:700;letter-spacing:2.5px;text-transform:uppercase;color:var(--purple);margin-bottom:10px}}
.quiz-heading{{font-size:1.1rem;font-weight:800;color:var(--ink);margin-bottom:6px}}
.quiz-sub{{font-size:.78rem;color:var(--ink3);margin-bottom:22px;font-weight:300}}
.quiz-start-btn{{padding:10px 28px;border-radius:24px;border:none;background:linear-gradient(135deg,#4361ee,#7c3aed);color:white;font-size:.82rem;font-weight:700;cursor:pointer;font-family:var(--sans);transition:all .2s;box-shadow:0 4px 16px rgba(67,97,238,.3)}}
.quiz-start-btn:hover{{transform:translateY(-2px);box-shadow:0 8px 24px rgba(67,97,238,.35)}}
/* 진행 바 */
.quiz-progress{{display:flex;gap:6px;justify-content:center;margin-bottom:28px}}
.qp-dot{{width:32px;height:4px;border-radius:2px;background:var(--border);transition:background .25s}}
.qp-dot.done{{background:var(--accent)}}
.qp-dot.current{{background:var(--purple)}}
/* 질문 */
.quiz-q{{font-size:1.05rem;font-weight:700;color:var(--ink);margin-bottom:22px;line-height:1.5}}
.quiz-options{{display:grid;grid-template-columns:1fr 1fr;gap:10px;max-width:480px;margin:0 auto}}
.quiz-opt{{padding:14px 16px;border-radius:12px;border:1.5px solid var(--border);background:white;cursor:pointer;text-align:left;transition:all .18s;font-family:var(--sans)}}
.quiz-opt:hover{{border-color:var(--accent);background:var(--accent-light);transform:translateY(-2px);box-shadow:0 4px 12px rgba(67,97,238,.1)}}
.quiz-opt-emoji{{font-size:1.2rem;margin-bottom:6px;display:block}}
.quiz-opt-text{{font-size:.8rem;font-weight:600;color:var(--ink);line-height:1.45}}
/* 결과 */
.quiz-result{{animation:fadeUp .4s ease both}}
.quiz-result-tag{{display:inline-block;padding:4px 14px;border-radius:20px;font-size:.7rem;font-weight:700;color:white;margin-bottom:14px}}
.quiz-result-title{{font-size:1.15rem;font-weight:800;color:var(--ink);margin-bottom:18px}}
.quiz-recs{{display:flex;gap:14px;justify-content:center;flex-wrap:wrap;margin-bottom:20px}}
.quiz-rec{{display:flex;gap:10px;align-items:flex-start;background:white;border-radius:12px;border:1px solid var(--border);padding:12px;width:210px;text-align:left;transition:all .18s}}
.quiz-rec:hover{{border-color:var(--accent);box-shadow:0 4px 16px rgba(67,97,238,.1)}}
.quiz-rec img{{width:48px;height:68px;border-radius:6px;object-fit:cover;flex-shrink:0}}
.quiz-rec-info{{min-width:0}}
.quiz-rec-title{{font-size:.76rem;font-weight:700;color:var(--ink);margin-bottom:3px;line-height:1.35}}
.quiz-rec-author{{font-size:.66rem;color:var(--ink4);font-weight:300}}
.quiz-retry{{padding:8px 22px;border-radius:20px;border:1.5px solid var(--border);background:white;font-size:.78rem;font-weight:600;color:var(--ink2);cursor:pointer;font-family:var(--sans);transition:all .15s}}
.quiz-retry:hover{{border-color:var(--accent);color:var(--accent)}}

/* ── 스크롤 진행 바 ── */
.progress-bar{{position:fixed;top:60px;left:0;height:2px;background:var(--accent);z-index:300;transition:width .1s linear;width:0%}}
</style>
</head>
<body>

<!-- 네비게이션 -->
<nav class="nav" id="mainNav">
  <div class="nav-inner">
    <div class="nav-logo">SV<span>.</span>Book</div>
    <span class="nav-meta">{now} 기준 · {len(books)}권</span>
    <div class="nav-actions">
      <button class="nav-btn" onclick="document.getElementById('guideSection').scrollIntoView({{behavior:'smooth'}})">📖 가이드</button>
      <button class="nav-btn" onclick="openRefreshModal()">🔄 재수집</button>
      <button class="nav-btn" onclick="downloadCSV()">CSV</button>
    </div>
  </div>
</nav>

<!-- 스크롤 진행 바 -->
<div class="progress-bar" id="progressBar"></div>

<!-- 히어로 -->
<section class="hero" id="heroSection">
  <div class="hero-bg">
    <div class="hero-orb hero-orb-1"></div>
  </div>
  <div class="hero-grid">
  <div class="hero-content">
    <div class="hero-eyebrow">CSES SV Book</div>
    <h1 class="hero-title">매주 사회적가치를<br>담은 책을 선별합니다</h1>
    <p class="hero-desc">사회적가치, ESG, 기후·환경, 지정학 등<br>우리 연구와 연결된 신간을 매주 자동 수집·분류합니다.</p>
    <div class="hero-cats">
      <button class="hero-cat active" data-cat="" onclick="heroSetCat(this)">전체</button>
      <button class="hero-cat" data-cat="Tech & Future" onclick="heroSetCat(this)">🤖 Tech &amp; Future</button>
      <button class="hero-cat" data-cat="ESG & Sustainability" onclick="heroSetCat(this)">🌱 ESG &amp; Sustainability</button>
      <button class="hero-cat" data-cat="Social & Human" onclick="heroSetCat(this)">🤝 Social &amp; Human</button>
      <button class="hero-cat" data-cat="Geopolitics & Strategy" onclick="heroSetCat(this)">🌍 Global</button>
    </div>
    <div class="hero-pick-btn" onclick="openPickModal()"><span>⭐</span> 원장님 Pick! <span class="hero-pick-arrow">→</span></div>
  </div>
  <div class="hero-visual">
    <div class="carousel" id="heroCarousel">
      <div class="carousel-track" id="carouselTrack"></div>
      <div class="carousel-nav">
        <button class="c-arrow" onclick="carouselPrev()">&#8592;</button>
        <div class="c-dots" id="cDots"></div>
        <button class="c-arrow" onclick="carouselNext()">&#8594;</button>
      </div>
    </div>
  </div>
  </div>
</section>

<!-- 소개 배너 -->
<section class="intro">
  <div class="intro-inner">
    <div>
      <div class="intro-label">About</div>
      <h2 class="intro-heading">4가지 주제로<br>탐색하세요</h2>
      <p class="intro-sub">교보문고, 국회도서관, 네이버 도서에서 자동 수집한 책들을 관련도 순으로 정리했어요.</p>
    </div>
    <div class="intro-cats">
      <div class="icat icat-tech" onclick="filterCat('Tech & Future')">
        <span class="icat-icon">🤖</span>
        <div><div class="icat-name">Tech &amp; Future</div><div class="icat-desc">AI, 로봇, 디지털 전환과 사회 변화</div></div>
      </div>
      <div class="icat icat-esg" onclick="filterCat('ESG & Sustainability')">
        <span class="icat-icon">🌱</span>
        <div><div class="icat-name">ESG &amp; Sustainability</div><div class="icat-desc">기후위기, 탄소중립, 기업의 사회적 책임</div></div>
      </div>
      <div class="icat icat-social" onclick="filterCat('Social & Human')">
        <span class="icat-icon">🤝</span>
        <div><div class="icat-name">Social &amp; Human</div><div class="icat-desc">불평등, 인구변화, 일의 미래, 다양성</div></div>
      </div>
      <div class="icat icat-geo" onclick="filterCat('Geopolitics & Strategy')">
        <span class="icat-icon">🌍</span>
        <div><div class="icat-name">Global &amp; Strategy</div><div class="icat-desc">글로벌 질서 재편, 공급망, 국제 전략</div></div>
      </div>
    </div>
  </div>
</section>

<!-- 미니 테스트 (플로팅) -->
<button class="quiz-fab" id="quizFab" onclick="openQuiz()">📚 나에게 맞는 책 찾기</button>
<div class="quiz-popup" id="quizPopup">
  <div class="quiz-popup-header">
    <span class="quiz-popup-title">📚 Book Match Test</span>
    <button class="quiz-popup-close" onclick="closeQuiz()">✕</button>
  </div>
  <div class="quiz-popup-body" id="quizBox">
    <div class="quiz-label">Book Match Test</div>
    <h2 class="quiz-heading">나에게 맞는 SV 도서는?</h2>
    <p class="quiz-sub">4개 질문에 답하면 딱 맞는 책 3권을 추천해드려요</p>
    <button class="quiz-start-btn" onclick="quizStart()">테스트 시작하기</button>
  </div>
</div>

<!-- 카테고리 탭 (sticky) -->
<div class="toolbar-sticky">
  <div class="toolbar-inner">
    <button class="cat-tab active" data-cat="" onclick="setCat(this)">전체</button>
    <button class="cat-tab" data-cat="Tech & Future" onclick="setCat(this)">🤖 Tech</button>
    <button class="cat-tab" data-cat="ESG & Sustainability" onclick="setCat(this)">🌱 ESG</button>
    <button class="cat-tab" data-cat="Social & Human" onclick="setCat(this)">🤝 Social</button>
    <button class="cat-tab" data-cat="Geopolitics & Strategy" onclick="setCat(this)">🌍 Global</button>
    <div class="toolbar-sep"></div>
    <select class="fsel" id="srcFilter" onchange="render()">
      <option value="">전체 출처</option>
      <option value="교보문고">교보문고</option>
      <option value="국회도서관">국회도서관</option>
      <option value="네이버 도서">네이버 도서</option>
    </select>
    <select class="fsel" id="kwFilter" onchange="render()">
      <option value="">전체 키워드</option>
    </select>
    <div class="search-wrap">
      <svg width="14" height="14" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
      <input type="text" id="q" placeholder="검색..." oninput="render()">
    </div>
  </div>
</div>

<!-- 통계 + 정렬 -->
<div class="meta-bar">
  <span class="meta-count" id="stats"></span>
  <div class="sort-group">
    <span class="sort-lbl">정렬</span>
    <button class="sort-btn active" id="btnDate" onclick="setSort('date')">최신순</button>
    <button class="sort-btn" id="btnScore" onclick="setSort('score')">관련도순</button>
  </div>
</div>

<!-- 카드 그리드 -->
<div class="grid-wrap">
  <div class="book-grid" id="bookGrid"></div>
  <div class="pagination" id="pagination"></div>
</div>

<!-- 사이트 가이드 -->
<section class="guide-section" id="guideSection">
  <div class="guide-inner">
    <div class="guide-header">
      <div class="guide-label">Site Guide</div>
      <h2 class="guide-title">SV Book은 이렇게 운영됩니다</h2>
    </div>
    <div class="guide-grid">
      <div class="guide-card">
        <div class="guide-card-icon">📡</div>
        <h3 class="guide-card-title">데이터 수집</h3>
        <p class="guide-card-desc">매주 월요일 오전 10시(KST), <b>교보문고</b> · <b>국회도서관</b> · <b>네이버 도서</b>에서 SV 관련 키워드로 신간을 자동 수집합니다. 수집된 데이터는 누적되어 계속 쌓입니다.</p>
      </div>
      <div class="guide-card">
        <div class="guide-card-icon">🎯</div>
        <h3 class="guide-card-title">관련도 점수</h3>
        <p class="guide-card-desc">제목과 내용에서 <b>SV 핵심 키워드</b>(AI×사회가치, ESG, 기후변화, 불평등, 거버넌스 등)의 출현 빈도와 조합을 분석해 <b>1~5점</b>으로 채점합니다. 5점은 AI×사회가치 등 복합 주제를 깊이 다루는 도서입니다.</p>
      </div>
      <div class="guide-card">
        <div class="guide-card-icon">🏷️</div>
        <h3 class="guide-card-title">자동 분류</h3>
        <p class="guide-card-desc">제목+내용 키워드 매칭으로 <b>Tech & Future</b>, <b>ESG & Sustainability</b>, <b>Social & Human</b>, <b>Global & Strategy</b> 4개 카테고리에 자동 배정됩니다.</p>
      </div>
      <div class="guide-card">
        <div class="guide-card-icon">🚫</div>
        <h3 class="guide-card-title">필터링 기준</h3>
        <p class="guide-card-desc">수험서, 소설/잡지, 아동·청소년 도서, ETF/투자서, 순수 기술서, 특정 정치인 저술, 안전보건 실무서, 기초 개론서 등은 자동 제외됩니다.</p>
      </div>
      <div class="guide-card">
        <div class="guide-card-icon">🔄</div>
        <h3 class="guide-card-title">수동 재수집</h3>
        <p class="guide-card-desc">우측 상단 <b>🔄 재수집</b> 버튼으로 GitHub Actions를 수동 실행할 수 있습니다. GitHub 토큰을 한 번 입력하면 브라우저에 자동 저장됩니다.</p>
      </div>
      <div class="guide-card">
        <div class="guide-card-icon">📚</div>
        <h3 class="guide-card-title">이달의 추천</h3>
        <p class="guide-card-desc">매월 CSES 연구진이 직접 선정한 <b>TOP 5 도서</b>를 상단 캐러셀에 게시합니다. 사회적가치 연구와 가장 밀접한 도서 위주로 선별합니다.</p>
      </div>
    </div>
  </div>
</section>

<!-- 재수집 모달 -->
<div class="modal-bg" id="refreshModal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <h2>🔄 재수집 실행</h2>
    <p>교보문고 · 국회도서관 최근 3개월 신간을 다시 수집하고 사이트를 업데이트합니다.<br>약 10~15분 후 페이지를 새로고침하면 반영돼요.</p>
    <label class="token-label">GitHub 토큰 (최초 1회 입력, 자동 저장)</label>
    <input class="token-input" id="tokenInput" type="password" placeholder="ghp_...">
    <div class="modal-status" id="modalStatus"></div>
    <div class="modal-btns">
      <button class="mbtn mbtn-secondary" onclick="closeModal()">닫기</button>
      <button class="mbtn mbtn-primary" id="runBtn" onclick="triggerWorkflow()">지금 실행</button>
    </div>
  </div>
</div>

<!-- 원장님 Pick 모달 -->
<div class="modal-bg" id="pickModal" onclick="if(event.target===this)closePickModal()">
  <div class="pick-modal">
    <button class="pick-modal-close" onclick="closePickModal()">✕</button>
    <div class="pick-banner" id="pickBanner">
      <div class="pick-banner-ov">
        <h2 class="pick-banner-t">⭐ 원장님 Pick!</h2>
        <p class="pick-banner-s">CSES 원장님께서 직접 선정한 도서 (2025-2026)</p>
      </div>
    </div>
    <div class="pick-carousel">
      <button class="pick-ca-arr" onclick="pickCarPrev()">&#8592;</button>
      <div class="pick-ca-card" id="pickCaCard"></div>
      <button class="pick-ca-arr" onclick="pickCarNext()">&#8594;</button>
    </div>
    <div class="pick-ca-dots" id="pickCaDots"></div>
    <div class="pick-list-hdr">전체 목록</div>
    <div id="pickList"></div>
    <div class="pick-list-pg" id="pickPg"></div>
  </div>
</div>

<script>
const ALL = {data_json};
const TODAY = new Date().toISOString().slice(0,7);
let sortKey='date', activeCat='';

const CP = {{'Tech & Future':'cp-tech','ESG & Sustainability':'cp-esg','Social & Human':'cp-social','Geopolitics & Strategy':'cp-geo'}};
const CAT_COLOR = {{'Tech & Future':'#a78bfa','ESG & Sustainability':'#6ee7b7','Social & Human':'#fca5a5','Geopolitics & Strategy':'#fcd34d'}};

// 키워드 드롭다운
(function(){{
  const order={kw_list};
  const present=new Set(ALL.map(b=>b['검색 키워드']));
  const sel=document.getElementById('kwFilter');
  order.filter(k=>present.has(k)).forEach(k=>{{
    const o=document.createElement('option');o.value=k;o.textContent=k;sel.appendChild(o);
  }});
}})();

// ── 이달의 추천 도서 캐러셀 (26년 6월 SV Book 편집 선정) ──
const FEATURED = [
  {{
    rank:'이달의 추천 1위',
    title:'이토록 인간적인 능력',
    author:'그레이엄 리 · 길벗 · 2026.02',
    bio:'디지털 기술 교육 전문가. 리디언스톤(Lydian Stone) 창립자 겸 CEO. AI 시대에 지켜야 할 인간다움과 핵심 능력을 연구.',
    desc:'"쓰지 않는 능력은 잃는다" — AI 시대, 우리를 인간답게 만드는 12가지 핵심 능력을 조명하며 인간다움의 본질을 되묻는다.',
    image:'https://shopping-phinf.pstatic.net/main_5886504/58865048657.20260331112437.jpg',
    link:'https://search.shopping.naver.com/book/catalog/58865048657',
  }},
  {{
    rank:'이달의 추천 2위',
    title:'경계 없음',
    author:'이중학 · 클라우드나인 · 2026.03',
    bio:'AI 에이전트 시대의 신인류론을 제시하는 연구자. 수직·수평 모든 경계가 사라지는 시대의 새로운 성장 전략을 탐구.',
    desc:'수직·수평 경계가 사라지고 AI 에이전트를 거느린 신인류가 온다. 기존 일자리 구조를 넘어 스스로 길을 만드는 시대의 생존 전략.',
    image:'https://shopping-phinf.pstatic.net/main_5941656/59416563400.20260331094626.jpg',
    link:'https://search.shopping.naver.com/book/catalog/59416563400',
  }},
  {{
    rank:'이달의 추천 3위',
    title:'호모 카르보(Homo Carbo)',
    author:'신익수 · 틈새책방 · 2026.03',
    bio:'탄소 문명과 기후위기의 교차점을 연구하는 과학 인문 저술가. 이산화탄소가 새로운 질병원이 되는 현실을 경고.',
    desc:'탄소를 먹고 자란 문명의 미래 — 이산화탄소가 기후 위기뿐 아니라 인류의 새로운 질병원이 되고 있다는 충격적 보고서.',
    image:'https://shopping-phinf.pstatic.net/main_5927712/59277129968.20260331114642.jpg',
    link:'https://search.shopping.naver.com/book/catalog/59277129968',
  }},
  {{
    rank:'이달의 추천 4위',
    title:'AI 이후의 미래 어떻게 될 것인가',
    author:'제이슨 솅커 · 더페이지 · 2026.05',
    bio:'세계적 미래학자. 금융·기술·일자리 전반에 걸친 AI의 파급력을 분석하며 부와 권력의 재편을 전망.',
    desc:'"AI는 도구가 아니라 새로운 지배 운영체제다" — 세계 산업을 뒤흔드는 AI가 부와 권력을 어디로 향하게 하는지 날카롭게 전망.',
    image:'https://shopping-phinf.pstatic.net/main_5976274/59762742786.20260428082502.jpg',
    link:'https://search.shopping.naver.com/book/catalog/59762742786',
  }},
  {{
    rank:'이달의 추천 5위',
    title:'인간을 인간답게 만드는 불완전함에 대하여',
    author:'팀 하포드 · 윌마 · 2026.05',
    bio:'세계적 이코노미스트이자 《경제학 콘서트》 저자. 알고리즘 시대, 인간의 유연함과 창의성이 사회 변혁의 핵심임을 역설.',
    desc:'알고리즘이 모든 마찰을 제거하는 완벽한 질서의 시대 — 그런데 왜 세상은 더 나아지지 않을까? 불완전함이 인간의 진짜 힘이다.',
    image:'https://shopping-phinf.pstatic.net/main_5978923/59789235607.20260425072246.jpg',
    link:'https://search.shopping.naver.com/book/catalog/59789235607',
  }},
];

let curSlide=0;
(function initCarousel(){{
  const track=document.getElementById('carouselTrack');
  const dots=document.getElementById('cDots');
  if(!track) return;
  track.innerHTML=FEATURED.map((b,i)=>`
    <div class="c-slide${{i===0?' active':''}}" data-idx="${{i}}">
      <div class="c-book-main">
        <a href="${{b.link}}" target="_blank"><img src="${{b.image}}" alt="${{b.title}}"></a>
      </div>
      <div class="c-info">
        <div class="c-rank">${{b.rank}}</div>
        <div class="c-title">${{b.title}}</div>
        <div class="c-author">${{b.author}}</div>
        <div class="c-desc">${{b.desc}}</div>
        <div class="c-bio">✍️ ${{b.bio}}</div>
        <a class="c-link" href="${{b.link}}" target="_blank">자세히 보기 →</a>
      </div>
    </div>`).join('');
  dots.innerHTML=FEATURED.map((_,i)=>`<div class="c-dot${{i===0?' active':''}}" onclick="goSlide(${{i}})"></div>`).join('');
}})();

function goSlide(n){{
  const slides=document.querySelectorAll('.c-slide');
  const dots=document.querySelectorAll('.c-dot');
  slides[curSlide].classList.remove('active');
  slides[curSlide].classList.add('exit');
  setTimeout(()=>slides[curSlide]&&slides[curSlide].classList.remove('exit'),400);
  dots[curSlide].classList.remove('active');
  curSlide=(n+FEATURED.length)%FEATURED.length;
  slides[curSlide].classList.add('active');
  dots[curSlide].classList.add('active');
}}
function carouselNext(){{goSlide(curSlide+1);}}
function carouselPrev(){{goSlide(curSlide-1);}}

function esc(s){{return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}

// 네비 스크롤 효과
window.addEventListener('scroll',()=>{{
  document.getElementById('mainNav').classList.toggle('scrolled',window.scrollY>10);
  const h=document.documentElement;
  const pct=(window.scrollY/(h.scrollHeight-h.clientHeight))*100;
  document.getElementById('progressBar').style.width=pct+'%';
}},{{passive:true}});

// 카테고리 필터
function setCat(btn){{
  activeCat=btn.dataset.cat;
  document.querySelectorAll('.cat-tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  render();
}}
function heroSetCat(btn){{
  activeCat=btn.dataset.cat;
  document.querySelectorAll('.hero-cat').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.cat-tab').forEach(b=>{{
    if(b.dataset.cat===activeCat) b.classList.add('active');
    else b.classList.remove('active');
  }});
  render();
  document.querySelector('.toolbar-sticky').scrollIntoView({{behavior:'smooth'}});
}}
function filterCat(cat){{
  activeCat=cat;
  document.querySelectorAll('.cat-tab,.hero-cat').forEach(b=>{{
    b.classList.toggle('active', b.dataset.cat===cat);
  }});
  render();
  document.querySelector('.toolbar-sticky').scrollIntoView({{behavior:'smooth'}});
}}

function setSort(key){{
  sortKey=key;
  document.getElementById('btnDate').classList.toggle('active',key==='date');
  document.getElementById('btnScore').classList.toggle('active',key==='score');
  render();
}}

function parseDate(s){{
  if(!s) return '';
  const m=s.match(/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\\s+(\\d{{1,2}}),?\\s+(\\d{{4}})/i);
  if(m){{const mo={{'jan':'01','feb':'02','mar':'03','apr':'04','may':'05','jun':'06','jul':'07','aug':'08','sep':'09','oct':'10','nov':'11','dec':'12'}};return m[3]+'-'+mo[m[1].slice(0,3).toLowerCase()]+'-'+m[2].padStart(2,'0');}}
  return s.replace(/\\./g,'-');
}}

function filtered(){{
  const q=document.getElementById('q').value.trim().toLowerCase();
  const src=document.getElementById('srcFilter').value;
  const kw=document.getElementById('kwFilter').value;
  return ALL.filter(b=>{{
    if(activeCat&&b['_category']!==activeCat) return false;
    if(src&&b['매체명']!==src) return false;
    if(kw&&b['검색 키워드']!==kw) return false;
    if(q&&!(b['도서명']||'').concat(b['저자']||'',b['책 내용']||'').toLowerCase().includes(q)) return false;
    return true;
  }});
}}

function getSorted(){{
  return filtered().sort((a,b)=>{{
    if(sortKey==='score') return (b['_score']||0)-(a['_score']||0);
    return (parseDate(b['출판일'])||'0').localeCompare(parseDate(a['출판일'])||'0');
  }});
}}

function toggleDesc(uid,btn){{
  document.getElementById(uid).classList.toggle('expanded');
  btn.textContent=document.getElementById(uid).classList.contains('expanded')?'접기':'더 보기';
}}

// IntersectionObserver for card animations
const io=new IntersectionObserver(entries=>{{
  entries.forEach(e=>{{if(e.isIntersecting){{e.target.classList.add('visible');io.unobserve(e.target);}}}}  );
}},{{threshold:0.08}});

const PAGE_SIZE=9;
let curPage=1;

function renderPage(books, page){{
  const total=Math.ceil(books.length/PAGE_SIZE)||1;
  curPage=Math.max(1,Math.min(page,total));
  const slice=books.slice((curPage-1)*PAGE_SIZE, curPage*PAGE_SIZE);
  const grid=document.getElementById('bookGrid');
  grid.innerHTML=slice.map((b,i)=>{{
    const ds=parseDate(b['출판일']);
    const isNew=ds&&ds.slice(0,7)>=TODAY;
    const href=b['링크']||'';
    const cat=b['_category']||'';
    const cp=CP[cat]||'';
    const uid='p'+curPage+'i'+i;
    const srcLbl=b['매체명']==='교보문고'?'교보':'국회';
    const metaParts=[b['저자'],b['출판사'],b['출판일']].filter(Boolean).map(esc);
    return `<div class="book-card" style="transition-delay:${{(i%3)*60}}ms">
  <div class="cover-wrap">
    <img src="${{esc(b['이미지']||'')}}" alt="${{esc(b['도서명'])}}" loading="lazy" onerror="this.parentNode.style.minHeight='180px';this.remove()">
    <div class="cover-overlay"></div>
    ${{href?`<a class="overlay-link" href="${{esc(href)}}" target="_blank">자세히 보기 →</a>`:''}}
    ${{isNew?'<span class="badge-new">NEW</span>':''}}
    ${{cat?`<span class="cat-pill ${{cp}}">${{esc(cat)}}</span>`:''}}
    <span class="src-dot">${{srcLbl}}</span>
  </div>
  <div class="book-body">
    <div class="book-title">${{href?`<a href="${{esc(href)}}" target="_blank">${{esc(b['도서명'])}}</a>`:esc(b['도서명'])}}</div>
    <div class="book-meta">${{metaParts.join('<span class="meta-sep"> · </span>')}}</div>
    ${{b['책 내용']?`<div class="book-desc" id="${{uid}}">${{esc(b['책 내용'])}}</div>
    <button class="toggle-btn" onclick="toggleDesc('${{uid}}',this)">더 보기</button>`:''}}
    <div class="book-footer">
      <span class="score-badge">관련도 ${{b['_score']||0}}점</span>
    </div>
  </div>
</div>`;
  }}).join('');
  grid.querySelectorAll('.book-card').forEach(c=>io.observe(c));

  // 페이지네이션 렌더
  const pg=document.getElementById('pagination');
  if(total<=1){{pg.innerHTML='';return;}}
  const pages=[];
  // 항상 1 표시
  pages.push(1);
  if(curPage>3) pages.push('…');
  for(let p=Math.max(2,curPage-1);p<=Math.min(total-1,curPage+1);p++) pages.push(p);
  if(curPage<total-2) pages.push('…');
  if(total>1) pages.push(total);

  pg.innerHTML=
    `<button class="pg-btn" onclick="goPage(${{curPage-1}})" ${{curPage===1?'disabled':''}}>&#8592;</button>`+
    pages.map(p=>p==='…'
      ? `<span class="pg-ellipsis">…</span>`
      : `<button class="pg-btn${{p===curPage?' active':''}}" onclick="goPage(${{p}})">${{p}}</button>`
    ).join('')+
    `<button class="pg-btn" onclick="goPage(${{curPage+1}})" ${{curPage===total?'disabled':''}}>&#8594;</button>`;
}}

function goPage(p){{
  const books=getSorted();
  renderPage(books,p);
  document.querySelector('.toolbar-sticky').scrollIntoView({{behavior:'smooth'}});
}}

function render(){{
  const books=getSorted();
  document.getElementById('stats').innerHTML=`<b>${{books.length}}</b>권 표시 중`;
  const grid=document.getElementById('bookGrid');
  if(!books.length){{
    grid.innerHTML='<div class="empty"><div class="empty-icon">🔍</div><p>검색 결과가 없습니다</p></div>';
    document.getElementById('pagination').innerHTML='';
    return;
  }}
  renderPage(books,1);
}}

function downloadCSV(){{
  const books=getSorted();
  const rows=[['#','카테고리','매체명','도서명','저자','책 내용','출판사','출판일','링크']];
  books.forEach((b,i)=>rows.push([i+1,b['_category']||'',b['매체명']||'',b['도서명']||'',b['저자']||'',b['책 내용']||'',b['출판사']||'',b['출판일']||'',b['링크']||'']));
  const csv='\\uFEFF'+rows.map(r=>r.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\\n');
  const a=document.createElement('a');a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='SV_Book_{filename_date}.csv';a.click();
}}

// 모달
// 원장님 Pick
const DIRECTOR_PICKS = [
  {{title:'최후의 인구론',author:'폴 몰런드',pub:'미래의창',date:'2025.01',bio:'영국 런던대 버크벡 칼리지 연구원, 인구통계학자',desc:'인구 감소가 가져올 인류의 미래를 전망하는 마지막 경고',img:'https://shopping-phinf.pstatic.net/main_5232754/52327541626.20260331100527.jpg',link:'https://search.shopping.naver.com/book/catalog/52327541626'}},
  {{title:'기부의 과학적 관리',author:'육근효',pub:'한국학술정보',date:'2025.01',bio:'경영학 박사, 기부·사회적 가치 경영 연구자',desc:'기부를 조직적·과학적으로 관리하는 실천적 프레임워크',img:'https://shopping-phinf.pstatic.net/main_5250622/52506223029.20260331102913.jpg',link:'https://search.shopping.naver.com/book/catalog/52506223029'}},
  {{title:'인센티브 이코노미',author:'유리 그니지',pub:'김영사',date:'2024.09',bio:'UC 샌디에이고 경제학 교수, 행동경제학 세계적 권위자',desc:'사람을 행동하게 하는 시그널 — 인센티브가 세상을 돌아가게 한다',img:'https://shopping-phinf.pstatic.net/main_5029985/50299858625.20260331121939.jpg',link:'https://search.shopping.naver.com/book/catalog/50299858625'}},
  {{title:'기업가정신',author:'나석권 외 7',pub:'현암사',date:'2025.04',bio:'기업가정신 연구자 7인 공저',desc:'경제 성장과 일자리 창출의 핵심, 기업가정신의 본질을 탐구',img:'https://shopping-phinf.pstatic.net/main_5425142/54251423391.20260331120842.jpg',link:'https://search.shopping.naver.com/book/catalog/54251423391'}},
  {{title:'적응하라 기후위기는 멈추지 않는다',author:'로버트 핀다이크',pub:'시크릿하우스',date:'2025.06',bio:'MIT 슬론경영대학원 석좌교수, 환경경제학 권위자',desc:'기후 대응을 넘어 적응의 시대로 — 경제학으로 본 생존 전략',img:'https://shopping-phinf.pstatic.net/main_5534095/55340956229.20260331122048.jpg',link:'https://search.shopping.naver.com/book/catalog/55340956229'}},
  {{title:'무엇이 대전환을 만들었는가',author:'바츨라프 스밀',pub:'처음북스',date:'2025.08',bio:'캐나다 매니토바대 석좌교수, 빌 게이츠 추천 저자',desc:'인구·식량·에너지·경제·환경으로 본 세계의 작동 원리',img:'https://shopping-phinf.pstatic.net/main_5586133/55861339745.20260331103152.jpg',link:'https://search.shopping.naver.com/book/catalog/55861339745'}},
  {{title:'빅벳',author:'라지브 샤',pub:'초록우산',date:'2025.05',bio:'록펠러재단 전 대표, USAID 전 청장',desc:'인류적 과제에 대담하게 베팅하는 빅벳 전략의 실체',img:'',link:'https://search.kyobobook.co.kr/search?keyword=%EB%B9%85%EB%B2%B3'}},
  {{title:'불확실성에 맞서는 기술',author:'데이비드 스피겔할터',pub:'생각의힘',date:'2025.05',bio:'케임브리지대 통계학 교수, 영국 왕립통계학회 전 회장',desc:'실업률·주식·전쟁·기후위기·AI — 예측의 대가가 가르치는 미래 생존 전략',img:'https://shopping-phinf.pstatic.net/main_5487363/54873634406.20260331104823.jpg',link:'https://search.shopping.naver.com/book/catalog/54873634406'}},
  {{title:'트렌드코리아 2026',author:'김난도 외 11',pub:'미래의창',date:'2025.09',bio:'서울대 소비자학과 교수, 소비트렌드분석센터장',desc:'AI 대전환의 시대, 2026 대한민국 소비트렌드 전망',img:'https://shopping-phinf.pstatic.net/main_5658975/56589756898.20260331121048.jpg',link:'https://search.shopping.naver.com/book/catalog/56589756898'}},
  {{title:'질서없음',author:'헬렌 톰슨',pub:'월북',date:'2025.10',bio:'케임브리지대 정치경제학 교수',desc:'격동의 세계를 이해하는 세 가지 프레임 — 에너지·지정학·금융',img:'https://shopping-phinf.pstatic.net/main_5692681/56926813115.20260331110635.jpg',link:'https://search.shopping.naver.com/book/catalog/56926813115'}},
  {{title:'직관과 객관',author:'키코 아네라스',pub:'오픈도어북스',date:'2026.01',bio:'데이터 사이언티스트, 의사결정 연구자',desc:'데이터와 직관 사이에서 더 나은 판단을 내리는 방법',img:'',link:'https://search.kyobobook.co.kr/search?keyword=%EC%A7%81%EA%B4%80%EA%B3%BC+%EA%B0%9D%EA%B4%80'}},
  {{title:'통합 성장 이론',author:'오데드 갤로어',pub:'RHK',date:'2025.11',bio:'브라운대 경제학과 교수, 통합성장이론 창시자',desc:'인류가 산업혁명 이후 폭발적 성장 단계로 전환한 이유를 규명',img:'',link:'https://search.kyobobook.co.kr/search?keyword=%ED%86%B5%ED%95%A9%EC%84%B1%EC%9E%A5%EC%9D%B4%EB%A1%A0'}},
  {{title:'휴먼 코드',author:'성소라',pub:'더스퀘어',date:'2025.12',bio:'AI·디지털 전환 전략가, 글로벌 기업 자문',desc:'AI가 질주하는 시대, 인간만의 차별적 무기를 재설계하라',img:'https://shopping-phinf.pstatic.net/main_5781108/57811080449.20260331102917.jpg',link:'https://search.shopping.naver.com/book/catalog/57811080449'}},
  {{title:'필연적 혼자의 시대',author:'김수영',pub:'다산북스',date:'2025.04',bio:'서울대 사회복지학과 교수, 1인가구 연구자',desc:'1000만 1인가구 시대 — 한국이 가족 대신 혼자를 선택한 이유',img:'https://shopping-phinf.pstatic.net/main_5861307/58613071998.20260331095059.jpg',link:'https://search.shopping.naver.com/book/catalog/58613071998'}},
  {{title:'낯선 사람과 부근을 만들기',author:'상바오',pub:'글항아리',date:'2026.02',bio:'사회학 연구자, 관계와 공동체 탐구',desc:'관계 끊기 시대, 친밀한 낯선 사람들 속에서 부근을 만들어내는 시도',img:'https://shopping-phinf.pstatic.net/main_5858327/58583270623.20260331095228.jpg',link:'https://search.shopping.naver.com/book/catalog/58583270623'}},
  {{title:'주의! 거짓이 포함되어 있을 수 있음',author:'앨릭스 에드먼스',pub:'위즈덤하우스',date:'2026.01',bio:'런던경영대학원 재무학 교수',desc:'가짜 정보와 허위 선동에 넘어가지 않는 팩트 체크의 기술',img:'https://shopping-phinf.pstatic.net/main_5868313/58683132378.20260331100947.jpg',link:'https://search.shopping.naver.com/book/catalog/58683132378'}},
  {{title:'사회연대경제',author:'로베르 부아예',pub:'경인문화사',date:'2025.05',bio:'프랑스 국립과학연구센터(CNRS) 연구교수, 조절이론 대가',desc:'인간 중심의 대안 경제질서로서 사회연대경제(SSE)의 가능성을 탐색',img:'https://shopping-phinf.pstatic.net/main_5557318/55573183670.20260331114002.jpg',link:'https://search.shopping.naver.com/book/catalog/55573183670'}},
  {{title:'슈퍼 모멘텀',author:'이인숙 외 5',pub:'플랫폼9와3/4',date:'2026.01',bio:'SK하이닉스 전·현직 임원 취재 기반',desc:'SK하이닉스의 언더독 스토리 — AI 메모리 기술 리더십의 비밀',img:'https://shopping-phinf.pstatic.net/main_5857039/58570391535.20260331122007.jpg',link:'https://search.shopping.naver.com/book/catalog/58570391535'}},
];
let pickCaIdx=0, pickPgIdx=0;
const PICK_PG_SIZE=5;

function openPickModal(){{
  pickCaIdx=0; pickPgIdx=0;
  renderPickCar();
  renderPickList();
  // 배너 이미지 (있으면 적용)
  const bannerEl=document.getElementById('pickBanner');
  const imgTest=new Image();
  imgTest.onload=function(){{
    const imgEl=document.createElement('img');
    imgEl.src='director_banner.jpg';
    imgEl.className='pick-banner-img';
    bannerEl.insertBefore(imgEl,bannerEl.firstChild);
  }};
  imgTest.onerror=function(){{}};
  imgTest.src='director_banner.jpg';
  document.getElementById('pickModal').classList.add('show');
}}
function renderPickCar(){{
  const b=DIRECTOR_PICKS[pickCaIdx];
  document.getElementById('pickCaCard').innerHTML=`
    ${{b.img?`<img class="pick-ca-img" src="${{b.img}}" onerror="this.style.display='none'">`:''}}
    <div class="pick-ca-info">
      <div class="pick-ca-title">${{b.title}}</div>
      <div class="pick-ca-meta">${{b.author}} · ${{b.pub}} · ${{b.date}}</div>
      <div class="pick-ca-bio">✍️ ${{b.bio}}</div>
      <div class="pick-ca-desc">${{b.desc}}</div>
      <a class="pick-ca-link" href="${{b.link}}" target="_blank">구매하기 →</a>
    </div>`;
  document.getElementById('pickCaDots').innerHTML=DIRECTOR_PICKS.map((_,i)=>
    `<div class="pick-ca-dot${{i===pickCaIdx?' active':''}}" onclick="pickCaGo(${{i}})"></div>`
  ).join('');
}}
function pickCaGo(n){{pickCaIdx=(n+DIRECTOR_PICKS.length)%DIRECTOR_PICKS.length;renderPickCar();}}
function pickCarNext(){{pickCaGo(pickCaIdx+1);}}
function pickCarPrev(){{pickCaGo(pickCaIdx-1);}}

function renderPickList(){{
  const total=Math.ceil(DIRECTOR_PICKS.length/PICK_PG_SIZE);
  const start=pickPgIdx*PICK_PG_SIZE;
  const slice=DIRECTOR_PICKS.slice(start,start+PICK_PG_SIZE);
  document.getElementById('pickList').innerHTML=slice.map((b,i)=>`
    <div class="pick-item" onclick="pickCaGo(${{start+i}});document.querySelector('.pick-carousel').scrollIntoView({{behavior:'smooth'}})">
      <div class="pick-num">${{start+i+1}}</div>
      ${{b.img?`<img class="pick-sm-img" src="${{b.img}}" onerror="this.style.display='none'">`:''}}
      <div class="pick-sm-info">
        <div class="pick-sm-title">${{b.title}}</div>
        <div class="pick-sm-meta">${{b.author}} · ${{b.pub}}</div>
      </div>
      <a class="pick-sm-link" href="${{b.link}}" target="_blank" onclick="event.stopPropagation()">구매 →</a>
    </div>`).join('');
  document.getElementById('pickPg').innerHTML=Array.from({{length:total}},(_,i)=>
    `<button class="pick-pg-btn${{i===pickPgIdx?' active':''}}" onclick="pickPgIdx=${{i}};renderPickList()">${{i+1}}</button>`
  ).join('');
}}
function closePickModal(){{
  document.getElementById('pickModal').classList.remove('show');
}}

function openRefreshModal(){{
  document.getElementById('refreshModal').classList.add('show');
  const saved=localStorage.getItem('sv_gh_token');
  if(saved) document.getElementById('tokenInput').value=saved;
}}
function closeModal(){{
  document.getElementById('refreshModal').classList.remove('show');
  setStatus('','');
  document.getElementById('runBtn').textContent='지금 실행';
  document.getElementById('runBtn').disabled=false;
}}
function setStatus(msg,type){{
  const el=document.getElementById('modalStatus');
  el.textContent=msg;el.className='modal-status'+(type?' '+type:'');
  el.style.display=msg?'block':'none';
}}
async function triggerWorkflow(){{
  const token=document.getElementById('tokenInput').value.trim();
  if(!token){{setStatus('❌ GitHub 토큰을 입력해주세요.','err');return;}}
  localStorage.setItem('sv_gh_token',token);
  const btn=document.getElementById('runBtn');
  btn.textContent='실행 중...';btn.disabled=true;setStatus('','');
  try{{
    const res=await fetch('https://api.github.com/repos/csessocial/sv-book/actions/workflows/update.yml/dispatches',{{
      method:'POST',
      headers:{{'Authorization':'token '+token,'Accept':'application/vnd.github+json','Content-Type':'application/json'}},
      body:JSON.stringify({{'ref':'main'}})
    }});
    if(res.status===204){{
      setStatus('✅ 수집 시작됐어요! 약 10~15분 후 새로고침하세요.','ok');
      btn.textContent='실행됨';
    }} else {{
      const j=await res.json().catch(()=>({{}}));
      setStatus('❌ '+(j.message||'오류 '+res.status),'err');
      btn.textContent='지금 실행';btn.disabled=false;
    }}
  }} catch(e){{
    setStatus('❌ '+e.message,'err');btn.textContent='지금 실행';btn.disabled=false;
  }}
}}

render();

// ── 미니 테스트 ──
const QUIZ_QS = [
  {{
    q: '요즘 가장 관심 가는 키워드는?',
    opts: [
      {{emoji:'🤖',text:'AI·기술이 바꾸는 미래',w:{{t:3,e:0,s:1,g:1}}}},
      {{emoji:'🌱',text:'기후·환경·지속가능성',w:{{t:0,e:3,s:1,g:1}}}},
      {{emoji:'🤝',text:'불평등·다양성·인구변화',w:{{t:0,e:1,s:3,g:1}}}},
      {{emoji:'🌍',text:'글로벌 질서·국제 전략',w:{{t:1,e:0,s:0,g:3}}}},
    ]
  }},
  {{
    q: '오늘 하루를 한마디로 표현하면?',
    opts: [
      {{emoji:'💡',text:'새로운 걸 배우고 싶다',w:{{t:2,e:1,s:1,g:1}}}},
      {{emoji:'😤',text:'세상이 왜 이런가 싶다',w:{{t:0,e:1,s:2,g:2}}}},
      {{emoji:'🌿',text:'조용히 생각을 정리하고 싶다',w:{{t:0,e:2,s:2,g:0}}}},
      {{emoji:'🔥',text:'뭔가 해내고 싶은 에너지가!',w:{{t:2,e:0,s:0,g:2}}}},
    ]
  }},
  {{
    q: '독서할 때 선호하는 스타일은?',
    opts: [
      {{emoji:'📊',text:'데이터·사례 중심 분석서',w:{{t:2,e:2,s:0,g:1}}}},
      {{emoji:'💬',text:'사람 이야기·인터뷰',w:{{t:0,e:0,s:3,g:1}}}},
      {{emoji:'🔮',text:'미래 전망·예측서',w:{{t:2,e:1,s:0,g:2}}}},
      {{emoji:'📖',text:'깊이 있는 교양·인문서',w:{{t:1,e:1,s:2,g:1}}}},
    ]
  }},
  {{
    q: '연구원으로서 요즘 고민되는 주제는?',
    opts: [
      {{emoji:'⚙️',text:'AI가 일자리·사회를 어떻게 바꿀까',w:{{t:3,e:0,s:2,g:0}}}},
      {{emoji:'🏭',text:'ESG·탄소중립 실현 방안',w:{{t:0,e:3,s:0,g:1}}}},
      {{emoji:'👥',text:'저출생·고령화·사회안전망',w:{{t:0,e:0,s:3,g:1}}}},
      {{emoji:'🌐',text:'공급망·패권 경쟁·에너지 전환',w:{{t:0,e:1,s:0,g:3}}}},
    ]
  }},
];
const CAT_KEYS = ['Tech & Future','ESG & Sustainability','Social & Human','Geopolitics & Strategy'];
const CAT_LABELS = {{'Tech & Future':'Tech & Future 🤖','ESG & Sustainability':'ESG & Sustainability 🌱','Social & Human':'Social & Human 🤝','Geopolitics & Strategy':'Global & Strategy 🌍'}};
const CAT_COLORS = {{'Tech & Future':'linear-gradient(135deg,#8b5cf6,#6366f1)','ESG & Sustainability':'linear-gradient(135deg,#10b981,#059669)','Social & Human':'linear-gradient(135deg,#ef4444,#dc2626)','Geopolitics & Strategy':'linear-gradient(135deg,#f59e0b,#d97706)'}};
let quizStep=-1, quizScores={{t:0,e:0,s:0,g:0}};

// 플로팅 테스트 open/close
function openQuiz(){{
  document.getElementById('quizPopup').classList.add('show');
  document.getElementById('quizFab').classList.add('hide');
}}
function closeQuiz(){{
  document.getElementById('quizPopup').classList.remove('show');
  document.getElementById('quizFab').classList.remove('hide');
}}

function quizStart(){{
  quizStep=0; quizScores={{t:0,e:0,s:0,g:0}};
  quizRender();
}}
function quizRender(){{
  const box=document.getElementById('quizBox');
  if(quizStep<QUIZ_QS.length){{
    const qd=QUIZ_QS[quizStep];
    box.innerHTML=`
      <div class="quiz-progress">${{QUIZ_QS.map((_,i)=>`<div class="qp-dot${{i<quizStep?' done':i===quizStep?' current':''}}"></div>`).join('')}}</div>
      <div class="quiz-q">${{qd.q}}</div>
      <div class="quiz-options">${{qd.opts.map((o,i)=>`
        <div class="quiz-opt" onclick="quizAnswer(${{i}})">
          <span class="quiz-opt-emoji">${{o.emoji}}</span>
          <span class="quiz-opt-text">${{o.text}}</span>
        </div>`).join('')}}</div>`;
  }} else {{
    quizShowResult();
  }}
}}
function quizAnswer(idx){{
  const w=QUIZ_QS[quizStep].opts[idx].w;
  quizScores.t+=w.t; quizScores.e+=w.e; quizScores.s+=w.s; quizScores.g+=w.g;
  quizStep++;
  quizRender();
}}
function quizShowResult(){{
  const scores=[quizScores.t,quizScores.e,quizScores.s,quizScores.g];
  const maxIdx=scores.indexOf(Math.max(...scores));
  const cat=CAT_KEYS[maxIdx];
  const pool=ALL.filter(b=>b['_category']===cat&&(b['_score']||0)>=4);
  const matched=(pool.length>=3?pool:ALL.filter(b=>(b['_score']||0)>=4)).sort((a,b)=>(b['_score']||0)-(a['_score']||0)).slice(0,3);
  const box=document.getElementById('quizBox');
  box.innerHTML=`<div class="quiz-result">
    <div class="quiz-result-tag" style="background:${{CAT_COLORS[cat]}}">${{CAT_LABELS[cat]}}</div>
    <div class="quiz-result-title">당신에게 추천하는 도서 3권</div>
    <div class="quiz-recs">${{matched.map(b=>`
      <a class="quiz-rec" href="${{esc(b['링크']||'#')}}" target="_blank" style="text-decoration:none;color:inherit">
        <img src="${{esc(b['이미지']||'')}}" onerror="this.style.display='none'">
        <div class="quiz-rec-info">
          <div class="quiz-rec-title">${{esc(b['도서명'])}}</div>
          <div class="quiz-rec-author">${{esc(b['저자']||'')}}</div>
        </div>
      </a>`).join('')}}</div>
    <button class="quiz-retry" onclick="quizStart()">다시 해보기</button>
    <button class="quiz-retry" style="margin-left:8px" onclick="filterCat('${{cat}}')">이 카테고리 전체 보기 →</button>
  </div>`;
}}
</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

    print("=" * 45)
    print("  SV Book 수집 시작")
    print("=" * 45)

    sources = ["kyobo", "nanet", "naver"]
    raw_books = collect(sources)
    print(f"\n총 {len(raw_books)}건 수집. 필터링 중...")

    from sv_filter import filter_and_score
    books = filter_and_score(raw_books, min_score=1)

    # 이미지 없는 책 제거
    before_img = len(books)
    books = [b for b in books if b.get("이미지", "").strip()]
    removed_img = before_img - len(books)
    if removed_img:
        print(f"  → 이미지 없는 책 {removed_img}건 제거")

    # 기존 데이터와 병합 (누적)
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sv_books_data.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        existing_titles = {_norm_title(b["도서명"]) for b in existing}
        new_count = 0
        for b in books:
            key = _norm_title(b["도서명"])
            if key not in existing_titles:
                existing.append(b)
                existing_titles.add(key)
                new_count += 1
        books = existing
        print(f"  → 기존 {len(existing) - new_count}권 + 신규 {new_count}권 = 총 {len(books)}권 누적")
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=1)

    # AI 요약 (ANTHROPIC_API_KEY가 있을 때만 실행)
    if os.environ.get("ANTHROPIC_API_KEY"):
        from summarizer import summarize_books
        books = summarize_books(books)
    else:
        print("\n[AI 요약 건너뜀] ANTHROPIC_API_KEY 환경변수가 없습니다.")

    print(f"\nHTML 생성 중...")
    output = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SV_Book.html")
    generate_html(books, output, total_raw=len(raw_books))

    print(f"저장 완료: {output}")
    print("브라우저로 열기...")
    webbrowser.open(output)
