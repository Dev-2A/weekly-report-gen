import anthropic
from src.config import Config


SYSTEM_PROMPT =  """당신은 개발자의 주간 회고 리포트를 작성하는 전문 어시스턴트입니다.
주어진 작업 기록을 분석하여 아래 형식에 맞는 회골 리포트를 한국어로 작성해주세요.

작성 원칙:
- 구체적인 작업명과 수치를 활용해 내용을 풍부하게 작성
- 긍정적인 성과는 충분히 인정하되, 개선점도 솔직하게 기술
- 다음 주 액션 아이템은 실천 가능하고 구체적으로 작성
- 전체 분량은 500~800자 내외로 작성"""


REPORT_TEMPLATE = """아래는 이번 주({week_label}) 작업 기록입니다.

{summary_text}

---

위 작업 기록을 바탕으로 다음 형식에 맞춰 주간 회고 리포트를 작성해주세요.

# 📋 주간 회고 리포트 — {week_label}

## ✅ 이번 주 성과
(완료된 작업 중 주요 성과를 3~5개 항목으로 정리)

## 📚 배운 점
(이번 주 작업을 통해 새롭게 알게 된 것, 기술적으로 성장한 부분)

## 🔍 아쉬운 점 / 개선할 점
(완료하지 못한 작업, 비효율적이었던 부분, 다음에 개선할 사항)

## 🎯 다음 주 목표
(다음 주에 집중할 작업과 구체적인 액션 아이템 3~5개)

## 💬 한 줄 회고
(이번 주를 한 문장으로 표현)
"""


class ReportGenerator:
    """Anthropic Claude API를 이용한 회고 리포트 생성기"""
    
    def __init__(self, config: Config):
        self.clilent = anthropic.Anthropic(api_key=config.anthropic_api_key)
        self.model = config.llm_model
        self.max_tokens = config.max_tokens
    
    def generate(self, week_label: str, summary_text: str) -> str:
        """
        작업 요약 텍스트를 바탕으로 주간 회고 리포트를 생성합니다.
        
        Args:
            week_label: 주차 레이블 (예: '2026년 10주차 (03/02 ~ 03/08)')
            summary_text: 전처리된 작업 요약 텍스트
        
        Returns:
            생성된 회고 리포트 Markdown 문자열
        """
        prompt = REPORT_TEMPLATE.format(
            week_label=week_label,
            summary_text=summary_text,
        )
        
        print(f"🤖 LLM 회고 리포트 생성 중... (모델: {self.model})")
        
        message = self.clilent.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )
        
        report_text = message.content[0].text
        print(f"✅ 리포트 생성 완료 (사용 토큰: {message.usage.input_tokens} in / {message.usage.output_tokens} out)")
        
        return report_text
    
    def generate_with_retry(
        self, week_label: str, summary_text: str, max_retries: int = 3
    ) -> str:
        """
        실패 시 재시도 로직이 포함된 리포트 생성 메서드.
        
        Args:
            week_label: 주차 레이블
            summary_text: 전처리된 작업 요약 텍스트
            max_retries: 최대 재시도 횟수
        
        Returns:
            생성된 회고 리포트 Markdown 문자열
        """
        last_error = None
        
        for attempt in range(1, max_retries + 1):
            try:
                return self.generate(week_label, summary_text)
            except anthropic.RateLimitError as e:
                print(f"⚠️  Rate limit 초과 ({attempt}/{max_retries}), 잠시 후 재시도...")
                last_error = e
                import time
                time.sleep(10 * attempt)
            except anthropic.APIError as e:
                print(f"⚠️  API 오류 ({attempt}/{max_retries}): {e}")
                last_error = e
                import time
                time.sleep(3 * attempt)
        
        raise RuntimeError(
            f"리포트 생성 실패: {max_retries}회 재시도 후에도 오류가 발생했습니다.\n"
            f"마지막 오류: {last_error}"
        )