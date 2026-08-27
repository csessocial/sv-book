"""Claude API를 이용한 SV Book 요약 생성"""

import os
import anthropic

_client = None

SYSTEM_PROMPT = """\
당신은 사회적 가치(Social Value) 전문 도서 큐레이터입니다.
주어진 도서 정보를 바탕으로 (1) 요약과 (2) 저자 한 줄 소개를 작성하세요.

[요약] 원칙:
- 첫 문장: 책의 핵심 주장이나 분석 대상을 명확히 제시
- 두 번째 문장: 분석 방법, 근거, 접근법을 설명
- 세 번째 문장(필요 시): 주요 시사점이나 정책적 함의 제시
- 학술적·저널리즘 문체, 마케팅 표현 지양
- 문장 부호 외 줄바꿈 없이 한 단락으로 작성

[저자 소개] 원칙:
- 저자를 소개하는 한국어 한 문장(소속·전문분야·대표 이력 중심, 40자 내외)
- **확실히 아는 정보가 없으면 빈칸으로 두세요(추측·창작 금지).** 내용 설명에 저자 소개가 있으면 그것을 근거로 요약해도 됩니다.

반드시 아래 형식으로만 출력(다른 말 금지):
###요약###
<요약문 한 단락>
###저자###
<저자 한 줄 소개 또는 빈칸>

요약 예시:
인류가 산업혁명 이후 폭발적 성장 단계로 전환한 이유를 기술 진보, 인구 변화, 교육 축적의 내생적 역동성에서 설명한다. 국가 간 불평등 또한 지리·문화·인구 다양성 같은 장기적 초기 조건에서 비롯됨을 밝히며, 저성장 시대에 국가가 지속 성장 단계로 진입하기 위한 핵심 조건과 정책적 시사점을 제시한다.
저자 소개 예시:
브라운대 경제학 교수로 통합성장이론을 정립한 세계적 경제사학자.\
"""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.\n"
                "배치 파일에 set ANTHROPIC_API_KEY=your_key_here 를 추가하세요."
            )
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def _parse_output(text: str, fallback: str) -> tuple[str, str]:
    """모델 출력에서 (요약, 저자소개) 분리. 형식 어긋나면 최대한 복원."""
    text = (text or "").strip()
    summary, bio = text, ""
    if "###저자###" in text:
        head, _, tail = text.partition("###저자###")
        summary = head.replace("###요약###", "").strip()
        bio = tail.strip()
    else:
        summary = text.replace("###요약###", "").strip()
    if not summary:
        summary = fallback
    # 저자 정보가 없다고 판단되는 응답은 빈칸 처리
    if bio and any(x in bio for x in ("빈칸", "정보가 없", "알 수 없", "확실하지", "미상", "N/A", "없음")):
        bio = ""
    return summary, bio


def summarize_book(book: dict) -> tuple[str, str]:
    """
    단일 도서 → (요약, 저자 한 줄 소개) 반환.
    API 호출 실패 시 (원본 '책 내용', "") 반환.
    """
    title = book.get("도서명", "")
    author = book.get("저자", "")
    description = book.get("책 내용", "").strip()

    if not description and not title:
        return "", ""

    user_message = f"도서명: {title}\n저자: {author}\n내용 설명: {description}"

    try:
        client = _get_client()
        response = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=600,
            thinking={"type": "adaptive"},
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        text = "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()
        return _parse_output(text, description)
    except Exception as e:
        print(f"  [요약 오류] '{title}': {e}")
        return description, ""


def summarize_books(books: list[dict], verbose: bool = True) -> list[dict]:
    """
    도서 목록 전체에 AI 요약을 추가하여 반환.
    원본 '책 내용'은 '_원본_내용' 키에 보존.
    """
    total = len(books)
    if total == 0:
        return books

    print(f"\n[AI 요약] {total}건 요약 시작 (claude-opus-4-8)...")
    result = []
    for i, book in enumerate(books, 1):
        if verbose:
            print(f"  [{i}/{total}] {book.get('도서명', '')[:30]}...", end="\r")
        summary, bio = summarize_book(book)
        b = dict(book)
        b["_원본_내용"] = b.get("책 내용", "")
        b["책 내용"] = summary
        b["_저자소개"] = bio
        result.append(b)

    if verbose:
        print(f"  AI 요약 완료: {total}건{' ' * 30}")
    return result
