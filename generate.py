"""SV Book - 데이터 수집 후 standalone HTML 생성"""

import sys
import os
import json
import webbrowser
from datetime import datetime

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def collect(sources: list[str]) -> list[dict]:
    all_books = []
    seen = set()

    SRC_LABELS = {"kyobo": "교보문고", "amazon": "Amazon", "nanet": "국회도서관"}
    steps = [s for s in ["kyobo", "amazon", "nanet"] if s in sources]
    for i, src in enumerate(steps, 1):
        print(f"[{i}/{len(steps)}] {SRC_LABELS[src]} 수집 중...")
        if src == "kyobo":
            from kyobo_scraper import fetch_all_books
        elif src == "amazon":
            from amazon_scraper import fetch_all_books
        else:
            from nanet_scraper import fetch_all_books
        for b in fetch_all_books():
            if b["도서명"] not in seen:
                seen.add(b["도서명"])
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
  --navy:#0a1628;
  --navy2:#1a2e4a;
  --accent:#1d6fa4;
  --accent2:#e8f4fb;
  --text:#1a1a2e;
  --text2:#4a5568;
  --text3:#8a9ab5;
  --bg:#f7f8fc;
  --white:#ffffff;
  --border:#e8ecf3;
  --radius:12px;
}}
body{{font-family:'Noto Sans KR',sans-serif;background:var(--bg);color:var(--text);min-height:100vh;font-weight:400;-webkit-font-smoothing:antialiased}}

/* ── 헤더 ── */
.site-header{{background:var(--navy);color:white}}
.header-inner{{max-width:1400px;margin:0 auto;padding:0 48px;display:flex;align-items:center;justify-content:space-between;height:64px}}
.logo{{font-size:1.05rem;font-weight:700;letter-spacing:-.3px;display:flex;align-items:center;gap:10px}}
.logo-dot{{width:8px;height:8px;border-radius:50%;background:#4fc3f7;flex-shrink:0}}
.header-meta{{font-size:.73rem;color:rgba(255,255,255,.4);font-weight:300}}
.btn-csv{{background:transparent;border:1px solid rgba(255,255,255,.28);color:rgba(255,255,255,.85);padding:7px 18px;border-radius:20px;font-family:'Noto Sans KR',sans-serif;font-size:.76rem;font-weight:500;cursor:pointer;transition:all .2s;letter-spacing:-.1px;white-space:nowrap}}
.btn-csv:hover{{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.55)}}
.btn-refresh{{background:transparent;border:1px solid rgba(255,255,255,.28);color:rgba(255,255,255,.85);padding:7px 18px;border-radius:20px;font-family:'Noto Sans KR',sans-serif;font-size:.76rem;font-weight:500;cursor:pointer;transition:all .2s;letter-spacing:-.1px;white-space:nowrap;display:flex;align-items:center;gap:6px}}
.btn-refresh:hover{{background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.55)}}
.btn-refresh.loading{{opacity:.6;pointer-events:none}}
/* 재수집 모달 */
.modal-bg{{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:1000;align-items:center;justify-content:center}}
.modal-bg.show{{display:flex}}
.modal{{background:white;border-radius:16px;padding:32px 36px;max-width:460px;width:90%;box-shadow:0 24px 60px rgba(0,0,0,.2)}}
.modal h2{{font-size:1.05rem;font-weight:700;color:var(--navy);margin-bottom:8px;letter-spacing:-.3px}}
.modal p{{font-size:.82rem;color:var(--text2);line-height:1.7;margin-bottom:20px;font-weight:300}}
.modal-status{{font-size:.8rem;padding:12px 16px;border-radius:8px;margin-bottom:20px;display:none}}
.modal-status.ok{{background:#d1fae5;color:#065f46}}
.modal-status.err{{background:#fee2e2;color:#991b1b}}
.modal-btns{{display:flex;gap:10px;justify-content:flex-end}}
.mbtn{{padding:9px 20px;border-radius:8px;font-family:'Noto Sans KR',sans-serif;font-size:.8rem;font-weight:600;cursor:pointer;border:none;transition:all .15s}}
.mbtn-primary{{background:var(--navy);color:white}}
.mbtn-primary:hover{{background:#1a2e4a}}
.mbtn-secondary{{background:#f3f4f6;color:var(--text2)}}
.mbtn-secondary:hover{{background:#e5e7eb}}

/* ── 히어로 TOP5 ── */
.hero{{background:var(--navy2);padding:44px 48px 36px}}
.hero-inner{{max-width:1400px;margin:0 auto}}
.hero-label{{font-size:.68rem;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;color:#4fc3f7;margin-bottom:12px}}
.hero-title{{font-size:1.45rem;font-weight:700;color:white;margin-bottom:30px;letter-spacing:-.5px}}
.rec-grid{{display:grid;grid-template-columns:repeat(5,1fr);gap:18px}}
@media(max-width:960px){{.rec-grid{{grid-template-columns:repeat(3,1fr)}}}}
@media(max-width:580px){{.rec-grid{{grid-template-columns:repeat(2,1fr)}}}}
.rec-card{{background:rgba(255,255,255,.07);border-radius:10px;overflow:hidden;transition:all .22s;text-decoration:none;color:white;border:1px solid rgba(255,255,255,.1);display:block}}
.rec-card:hover{{background:rgba(255,255,255,.13);transform:translateY(-5px);box-shadow:0 16px 40px rgba(0,0,0,.4)}}
.rec-card-img{{width:100%;aspect-ratio:2/3;object-fit:cover;display:block;background:#243550}}
.rec-card-body{{padding:13px 14px 16px}}
.rec-card-cat{{font-size:.6rem;font-weight:600;letter-spacing:1.2px;text-transform:uppercase;margin-bottom:7px;opacity:.75}}
.rec-card-title{{font-size:.81rem;font-weight:600;line-height:1.45;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:5px;letter-spacing:-.2px}}
.rec-card-author{{font-size:.69rem;opacity:.45;font-weight:300}}

/* ── 카테고리 탭 ── */
.cat-nav{{background:var(--white);border-bottom:2px solid var(--border);position:sticky;top:0;z-index:100}}
.cat-nav-inner{{max-width:1400px;margin:0 auto;padding:0 48px;display:flex;gap:0;overflow-x:auto}}
.cat-tab{{padding:15px 22px;font-size:.81rem;font-weight:500;color:var(--text3);border:none;background:none;cursor:pointer;border-bottom:2px solid transparent;margin-bottom:-2px;transition:all .18s;font-family:'Noto Sans KR',sans-serif;white-space:nowrap;letter-spacing:-.2px}}
.cat-tab:hover{{color:var(--text2)}}
.cat-tab.active{{color:var(--navy);font-weight:700;border-bottom-color:var(--navy)}}
.cat-tab[data-cat="Tech & Future"].active{{border-bottom-color:#7c3aed;color:#7c3aed}}
.cat-tab[data-cat="ESG & Sustainability"].active{{border-bottom-color:#059669;color:#059669}}
.cat-tab[data-cat="Social & Human"].active{{border-bottom-color:#dc2626;color:#dc2626}}
.cat-tab[data-cat="Geopolitics & Strategy"].active{{border-bottom-color:#d97706;color:#d97706}}

/* ── 툴바 ── */
.controls{{max-width:1400px;margin:0 auto;padding:24px 48px 0;display:flex;gap:12px;flex-wrap:wrap;align-items:center}}
.search-wrap{{flex:1;min-width:220px;position:relative}}
.search-wrap svg{{position:absolute;left:13px;top:50%;transform:translateY(-50%);color:var(--text3);pointer-events:none;flex-shrink:0}}
.search-wrap input{{width:100%;padding:10px 14px 10px 40px;border:1.5px solid var(--border);border-radius:8px;font-size:.84rem;font-family:'Noto Sans KR',sans-serif;outline:none;color:var(--text);background:var(--white);transition:border .15s}}
.search-wrap input:focus{{border-color:var(--accent)}}
.search-wrap input::placeholder{{color:var(--text3)}}
.fsel{{padding:10px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:.81rem;font-family:'Noto Sans KR',sans-serif;background:var(--white);color:var(--text);cursor:pointer;outline:none}}
.sort-row{{max-width:1400px;margin:0 auto;padding:14px 48px 6px;display:flex;gap:8px;align-items:center}}
.sort-lbl{{font-size:.72rem;color:var(--text3);margin-right:2px}}
.sort-btn{{padding:5px 14px;border-radius:20px;border:1.5px solid var(--border);background:var(--white);font-size:.72rem;font-family:'Noto Sans KR',sans-serif;color:var(--text2);cursor:pointer;transition:all .15s;font-weight:500}}
.sort-btn.active{{background:var(--navy);color:white;border-color:var(--navy)}}
.stats-row{{max-width:1400px;margin:0 auto;padding:8px 48px 18px;font-size:.76rem;color:var(--text3)}}
.stats-row b{{color:var(--navy);font-weight:600}}

/* ── 카드 그리드 ── */
.grid-outer{{max-width:1400px;margin:0 auto;padding:0 48px 72px}}
.book-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:26px}}
@media(max-width:1200px){{.book-grid{{grid-template-columns:repeat(3,1fr)}}}}
@media(max-width:820px){{.book-grid{{grid-template-columns:repeat(2,1fr)}}}}
@media(max-width:500px){{.book-grid{{grid-template-columns:1fr}}}}

.book-card{{background:var(--white);border-radius:var(--radius);overflow:hidden;border:1px solid var(--border);transition:all .22s;display:flex;flex-direction:column}}
.book-card:hover{{box-shadow:0 10px 36px rgba(10,22,40,.11);transform:translateY(-4px);border-color:transparent}}
.cover-wrap{{position:relative;background:#e9eef5;overflow:hidden}}
.cover-wrap img{{width:100%;aspect-ratio:2/3;object-fit:cover;display:block;transition:transform .32s}}
.book-card:hover .cover-wrap img{{transform:scale(1.04)}}
.badge-new{{position:absolute;top:10px;left:10px;background:#ef4444;color:white;font-size:.6rem;font-weight:700;padding:3px 8px;border-radius:4px;letter-spacing:.5px;font-family:'Noto Sans KR',sans-serif}}
.cat-badge{{position:absolute;bottom:10px;left:10px;font-size:.6rem;font-weight:700;padding:3px 10px;border-radius:20px;letter-spacing:.3px;backdrop-filter:blur(6px);font-family:'Noto Sans KR',sans-serif}}
.cat-tech{{background:rgba(124,58,237,.82);color:white}}
.cat-esg{{background:rgba(5,150,105,.82);color:white}}
.cat-social{{background:rgba(220,38,38,.82);color:white}}
.cat-geo{{background:rgba(217,119,6,.82);color:white}}
.src-pill{{position:absolute;top:10px;right:10px;font-size:.59rem;font-weight:600;padding:3px 8px;border-radius:4px;font-family:'Noto Sans KR',sans-serif}}
.src-kyobo{{background:rgba(255,255,255,.92);color:#856404}}
.src-nl{{background:rgba(255,255,255,.92);color:#155724}}

.book-body{{padding:16px 17px 15px;flex:1;display:flex;flex-direction:column;gap:9px}}
.book-title{{font-size:.88rem;font-weight:700;color:var(--navy);line-height:1.42;letter-spacing:-.3px}}
.book-title a{{color:inherit;text-decoration:none}}
.book-title a:hover{{color:var(--accent)}}
.book-meta{{font-size:.72rem;color:var(--text3);font-weight:300;display:flex;gap:5px;flex-wrap:wrap;align-items:center;line-height:1.5}}
.meta-sep{{opacity:.35}}
.book-desc{{font-size:.77rem;color:var(--text2);line-height:1.75;flex:1;display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden;font-weight:300;letter-spacing:-.1px}}
.book-desc.expanded{{display:block}}
.book-footer{{display:flex;align-items:center;justify-content:space-between;margin-top:2px;padding-top:10px;border-top:1px solid var(--border)}}
.score-pill{{font-size:.7rem;font-weight:600;color:var(--accent);background:var(--accent2);padding:3px 10px;border-radius:20px;letter-spacing:-.1px}}
.toggle-btn{{font-size:.72rem;color:var(--accent);cursor:pointer;font-weight:500;user-select:none;background:none;border:none;font-family:'Noto Sans KR',sans-serif;padding:0;letter-spacing:-.1px}}
.toggle-btn:hover{{text-decoration:underline}}

.empty{{text-align:center;padding:90px 20px;color:var(--text3);grid-column:1/-1}}
.empty-ico{{font-size:2.8rem;margin-bottom:14px;opacity:.35}}
.empty p{{font-size:.88rem;font-weight:300}}
</style>
</head>
<body>

<header class="site-header">
  <div class="header-inner">
    <div class="logo"><span class="logo-dot"></span>SV Book</div>
    <span class="header-meta">{now} 기준 &nbsp;·&nbsp; {len(books)}권 큐레이션</span>
    <div style="display:flex;gap:8px">
      <button class="btn-refresh" onclick="openRefreshModal()">🔄 재수집</button>
      <button class="btn-csv" onclick="downloadCSV()">CSV 다운로드</button>
    </div>
  </div>
</header>

<!-- 재수집 모달 -->
<div class="modal-bg" id="refreshModal" onclick="if(event.target===this)closeModal()">
  <div class="modal">
    <h2>🔄 재수집 실행</h2>
    <p>교보문고 · 국회도서관에서 최근 3개월 신간을 다시 수집하고 사이트를 업데이트합니다.<br>약 10~15분 후 페이지를 새로고침하면 반영돼요.</p>
    <div style="margin-bottom:16px">
      <label style="font-size:.76rem;font-weight:600;color:var(--text2);display:block;margin-bottom:6px">GitHub 토큰 (최초 1회만 입력, 자동 저장)</label>
      <input id="tokenInput" type="password" placeholder="ghp_..." style="width:100%;padding:9px 12px;border:1.5px solid var(--border);border-radius:8px;font-size:.82rem;font-family:'Noto Sans KR',sans-serif;outline:none">
    </div>
    <div class="modal-status" id="modalStatus"></div>
    <div class="modal-btns">
      <button class="mbtn mbtn-secondary" onclick="closeModal()">닫기</button>
      <button class="mbtn mbtn-primary" id="runBtn" onclick="triggerWorkflow()">지금 실행</button>
    </div>
  </div>
</div>

<section class="hero">
  <div class="hero-inner">
    <div class="hero-label">Editor's Pick</div>
    <div class="hero-title">이번 주 추천 도서 TOP 5</div>
    <div class="rec-grid" id="recGrid"></div>
  </div>
</section>

<nav class="cat-nav">
  <div class="cat-nav-inner">
    <button class="cat-tab active" data-cat="" onclick="setCat(this)">전체</button>
    <button class="cat-tab" data-cat="Tech & Future" onclick="setCat(this)">🤖 Tech &amp; Future</button>
    <button class="cat-tab" data-cat="ESG & Sustainability" onclick="setCat(this)">🌱 ESG &amp; Sustainability</button>
    <button class="cat-tab" data-cat="Social & Human" onclick="setCat(this)">🤝 Social &amp; Human</button>
    <button class="cat-tab" data-cat="Geopolitics & Strategy" onclick="setCat(this)">🌍 Geopolitics &amp; Strategy</button>
  </div>
</nav>

<div class="controls">
  <div class="search-wrap">
    <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
    <input type="text" id="q" placeholder="도서명, 저자, 내용 검색..." oninput="render()">
  </div>
  <select class="fsel" id="srcFilter" onchange="render()">
    <option value="">전체 출처</option>
    <option value="교보문고">교보문고</option>
    <option value="국회도서관">국회도서관</option>
  </select>
  <select class="fsel" id="kwFilter" onchange="render()">
    <option value="">전체 키워드</option>
  </select>
</div>

<div class="sort-row">
  <span class="sort-lbl">정렬</span>
  <button class="sort-btn active" id="btnDate" onclick="setSort('date')">최신순</button>
  <button class="sort-btn" id="btnScore" onclick="setSort('score')">관련도순</button>
</div>
<div class="stats-row"><span id="stats"></span></div>

<div class="grid-outer">
  <div class="book-grid" id="bookGrid"></div>
</div>

<script>
const ALL = {data_json};
const TODAY = new Date().toISOString().slice(0,7);
let sortKey = 'date', activeCat = '';

const CC = {{
  'Tech & Future':'cat-tech',
  'ESG & Sustainability':'cat-esg',
  'Social & Human':'cat-social',
  'Geopolitics & Strategy':'cat-geo'
}};
const CAT_COLOR = {{
  'Tech & Future':'#a78bfa',
  'ESG & Sustainability':'#6ee7b7',
  'Social & Human':'#fca5a5',
  'Geopolitics & Strategy':'#fcd34d'
}};

(function(){{
  const order = {kw_list};
  const present = new Set(ALL.map(b=>b['검색 키워드']));
  const sel = document.getElementById('kwFilter');
  order.filter(k=>present.has(k)).forEach(k=>{{
    const o=document.createElement('option');o.value=k;o.textContent=k;sel.appendChild(o);
  }});
}})();

(function(){{
  const top5=[...ALL].sort((a,b)=>(b['_score']||0)-(a['_score']||0)).slice(0,5);
  document.getElementById('recGrid').innerHTML=top5.map(b=>{{
    const href=b['링크']||'#';
    return `<a class="rec-card" href="${{esc(href)}}" target="_blank">
      <img class="rec-card-img" src="${{esc(b['이미지']||'')}}" alt="${{esc(b['도서명'])}}" loading="lazy" onerror="this.style.background='#243550';this.removeAttribute('src')">
      <div class="rec-card-body">
        <div class="rec-card-cat" style="color:${{CAT_COLOR[b['_category']]||'#93c5fd'}}">${{esc(b['_category']||'')}}</div>
        <div class="rec-card-title">${{esc(b['도서명'])}}</div>
        <div class="rec-card-author">${{esc(b['저자']||'')}}</div>
      </div>
    </a>`;
  }}).join('');
}})();

function esc(s){{return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');}}

function setCat(btn){{
  activeCat=btn.dataset.cat;
  document.querySelectorAll('.cat-tab').forEach(b=>b.classList.remove('active'));
  btn.classList.add('active');
  render();
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
  if(m){{
    const mo={{'jan':'01','feb':'02','mar':'03','apr':'04','may':'05','jun':'06','jul':'07','aug':'08','sep':'09','oct':'10','nov':'11','dec':'12'}};
    return m[3]+'-'+mo[m[1].slice(0,3).toLowerCase()]+'-'+m[2].padStart(2,'0');
  }}
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
  const list=filtered();
  return list.sort((a,b)=>{{
    if(sortKey==='score') return (b['_score']||0)-(a['_score']||0);
    return (parseDate(b['출판일'])||'0000').localeCompare(parseDate(a['출판일'])||'0000');
  }});
}}

function toggleDesc(uid,btn){{
  const el=document.getElementById(uid);
  const exp=el.classList.toggle('expanded');
  btn.textContent=exp?'접기':'더 보기';
}}

function render(){{
  const books=getSorted();
  document.getElementById('stats').innerHTML=`<b>${{books.length}}</b>권 표시 중`;
  const grid=document.getElementById('bookGrid');
  if(!books.length){{
    grid.innerHTML='<div class="empty"><div class="empty-ico">🔍</div><p>검색 결과가 없습니다</p></div>';
    return;
  }}
  grid.innerHTML=books.map((b,i)=>{{
    const ds=parseDate(b['출판일']);
    const isNew=ds&&ds.slice(0,7)>=TODAY;
    const href=b['링크']||'';
    const titleEl=href?`<a href="${{esc(href)}}" target="_blank">${{esc(b['도서명'])}}</a>`:esc(b['도서명']);
    const cat=b['_category']||'';
    const uid='d'+i;
    const srcLbl=b['매체명']==='교보문고'?'교보':'국회';
    const srcCls=b['매체명']==='교보문고'?'src-kyobo':'src-nl';
    const metaParts=[b['저자'],b['출판사'],b['출판일']].filter(Boolean).map(esc);
    return `<div class="book-card">
  <div class="cover-wrap">
    <img src="${{esc(b['이미지']||'')}}" alt="${{esc(b['도서명'])}}" loading="lazy" onerror="this.parentNode.style.minHeight='160px';this.remove()">
    ${{isNew?'<span class="badge-new">NEW</span>':''}}
    ${{cat?`<span class="cat-badge ${{CC[cat]||''}}">${{esc(cat)}}</span>`:''}}
    <span class="src-pill ${{srcCls}}">${{srcLbl}}</span>
  </div>
  <div class="book-body">
    <div class="book-title">${{titleEl}}</div>
    <div class="book-meta">${{metaParts.join('<span class="meta-sep"> · </span>')}}</div>
    ${{b['책 내용']?`<div class="book-desc" id="${{uid}}">${{esc(b['책 내용'])}}</div>
    <button class="toggle-btn" onclick="toggleDesc('${{uid}}',this)">더 보기</button>`:''}}
    <div class="book-footer">
      <span class="score-pill">관련도 ${{b['_score']||0}}점</span>
    </div>
  </div>
</div>`;
  }}).join('');
}}

function downloadCSV(){{
  const books=getSorted();
  const rows=[['#','카테고리','매체명','도서명','저자','책 내용','출판사','출판일','링크']];
  books.forEach((b,i)=>rows.push([i+1,b['_category']||'',b['매체명']||'',b['도서명']||'',b['저자']||'',b['책 내용']||'',b['출판사']||'',b['출판일']||'',b['링크']||'']));
  const csv='\\uFEFF'+rows.map(r=>r.map(c=>'"'+String(c).replace(/"/g,'""')+'"').join(',')).join('\\n');
  const a=document.createElement('a');a.href='data:text/csv;charset=utf-8,'+encodeURIComponent(csv);
  a.download='SV_Book_{filename_date}.csv';a.click();
}}

render();

// ── 재수집 모달 ──
function openRefreshModal(){{
  document.getElementById('refreshModal').classList.add('show');
  const saved = localStorage.getItem('sv_gh_token');
  if(saved) document.getElementById('tokenInput').value = saved;
}}
function closeModal(){{
  document.getElementById('refreshModal').classList.remove('show');
  setStatus('','');
  document.getElementById('runBtn').textContent='지금 실행';
  document.getElementById('runBtn').disabled=false;
}}
function setStatus(msg, type){{
  const el=document.getElementById('modalStatus');
  el.textContent=msg; el.className='modal-status'+(type?' '+type:'');
  el.style.display=msg?'block':'none';
}}

async function triggerWorkflow(){{
  const token = document.getElementById('tokenInput').value.trim();
  if(!token){{ setStatus('❌ GitHub 토큰을 입력해주세요.','err'); return; }}
  localStorage.setItem('sv_gh_token', token);

  const btn=document.getElementById('runBtn');
  btn.textContent='실행 중...'; btn.disabled=true;
  setStatus('','');
  try{{
    const res = await fetch(
      'https://api.github.com/repos/csessocial/sv-book/actions/workflows/update.yml/dispatches',
      {{
        method:'POST',
        headers:{{
          'Authorization':'token '+token,
          'Accept':'application/vnd.github+json',
          'Content-Type':'application/json'
        }},
        body:JSON.stringify({{'ref':'main'}})
      }}
    );
    if(res.status===204){{
      setStatus('✅ 수집 시작됐어요! 약 10~15분 후 페이지를 새로고침하세요.','ok');
      btn.textContent='실행됨';
    }} else {{
      const j=await res.json().catch(()=>({{}}));
      setStatus('❌ '+(j.message||'오류 '+res.status),'err');
      btn.textContent='지금 실행'; btn.disabled=false;
    }}
  }} catch(e){{
    setStatus('❌ 네트워크 오류: '+e.message,'err');
    btn.textContent='지금 실행'; btn.disabled=false;
  }}
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

    sources = ["kyobo", "nanet"]
    raw_books = collect(sources)
    print(f"\n총 {len(raw_books)}건 수집. 필터링 중...")

    from sv_filter import filter_and_score
    books = filter_and_score(raw_books, min_score=2)

    # 이미지 없는 책 제거
    before_img = len(books)
    books = [b for b in books if b.get("이미지", "").strip()]
    removed_img = before_img - len(books)
    if removed_img:
        print(f"  → 이미지 없는 책 {removed_img}건 제거")

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
