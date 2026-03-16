# 🗒️ Weekly Report Generator

Notion DB에 쌓인 주간 작업 기록을 자동으로 읽어,
LLM이 회고 리포트를 생성하고 Notion 페이지로 업로드하는 자동화 도구입니다.

## ✨ Features

- 📥 Notion DB에서 이번 주 작업 기록 자동 수집
- 🤖 LLM 기반 회고 리포트 생성 (성과 요약 / 배운 점 / 아쉬운 점 / 다음 주 목표)
- 📄 Markdown 리포트 로컬 저장
- 📤 생성된 리포트를 Notion 페이지로 자동 업로드
- 🗓️ 주차 자동 계산 + 스케줄러 지원
- 🔍 dry-run 모드 (LLM 호출 없이 작업 기록 미리보기)

## 🛠️ Tech Stack

- Python 3.11+
- [notion-client](https://github.com/ramnes/notion-sdk-py)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Click](https://click.palletsprojects.com/) (CLI)
- [schedule](https://schedule.readthedocs.io/) (스케줄러)

## 📁 Project Structure

```text
weekly-report-gen/
├── src/
│   ├── config.py          # 환경 변수 설정
│   ├── pipeline.py        # 전체 파이프라인 통합
│   ├── scheduler.py       # 자동 실행 스케줄러
│   ├── notion/
│   │   ├── client.py      # Notion API 클라이언트
│   │   ├── parser.py      # 페이지 파싱
│   │   └── uploader.py    # Markdown → Notion 블록 변환 + 업로드
│   ├── llm/
│   │   └── generator.py   # LLM 회고 리포트 생성
│   └── report/
│       ├── preprocessor.py # 작업 기록 전처리 + 정규화
│       └── renderer.py     # Markdown 파일 저장
├── tests/
│   ├── test_preprocessor.py
│   └── test_uploader.py
├── output/                 # 생성된 Markdown 리포트 저장
├── main.py                 # CLI 진입점
├── .env.example
└── requirements.txt
```

## 🚀 Getting Started

### 1. 레포지토리 클론 + 가상환경 세팅

```cmd
git clone https://github.com/Dev-2A/weekly-report-gen.git
cd weekly-report-gen
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Notion 인테그레이션 생성

1. [notion.so/my-integrations](https://www.notion.so/my-integrations) 접속
2. **New integration** 생성 (Internal 타입)
3. **Internal Integration Secret** 복사 → `NOTION_TOKEN`

### 3. Notion DB 준비

작업 기록 DB에 아래 컬럼이 필요:

| 컬럼명 | 타입 | 설명 |
| -------- | ------ | ------ |
| `Name` | 제목 | 작업 이름 |
| `Date` | 날짜 | 작업 날짜 |
| `Status` | 셀렉트 | 완료 / 진행 중 등 |
| `Tags` | 멀티셀렉트 | 개발 / 회의 등 |
| `Memo` | 텍스트 | 메모 (선택) |

DB 및 리포트 업로드 페이지에 인테그레이션 연결 필수:
`•••` → Connections → 인테그레이션 선택

### 4. 환경 변수 설정

```cmd
copy .env.example .env
```

`.env` 파일에 값 입력:

```env
NOTION_TOKEN=secret_xxxx
NOTION_DATABASE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_REPORT_PARENT_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxx
```

> **DB ID 찾는 법**: Notion DB를 새 탭으로 열고 URL에서
> `notion.so/` 뒤 `?v=` 앞의 32자리

## 💻 Usage

```cmd
# 지난주 회고 리포트 생성 (기본)
python main.py generate

# 이번 주 리포트 생성
python main.py generate --week 0

# Notion 업로드 없이 로컬 저장만
python main.py generate --no-upload

# LLM 호출 없이 작업 기록만 확인 (무료)
python main.py preview

# 저장된 리포트 목록 확인
python main.py list

# 설정 상태 확인
python main.py info

# 매주 월요일 오전 9시 자동 실행
python main.py scheduler

# 매주 금요일 오후 6시 자동 실행
python main.py scheduler --weekday friday --hour 18
```

## ⏰ Windows 작업 스케줄러 등록

터미널을 열어두지 않아도 자동 실행하려면 Windows 작업 스케줄러에 등록.

### 1. 배치 파일 생성

프로젝트 루트에 `run_report.bat` 파일 생성:

```bat
@echo off
cd /d C:\Users\ontheit\Desktop\dev2a\self\SelfStudy\vscode\weekly-report-gen
call .venv\Scripts\activate
python main.py generate --week 1
```

### 2. 작업 스케줄러 등록

```text
1. Win + S → "작업 스케줄러" 검색 후 실행
2. 오른쪽 패널 → "기본 작업 만들기" 클릭
3. 이름: "Weekly Report Generator"
4. 트리거: "매주" → 요일/시각 선택 (예: 월요일 09:00)
5. 동작: "프로그램 시작"
   - 프로그램: C:\Users\ontheit\Desktop\dev2a\self\SelfStudy\vscode\weekly-report-gen\run_report.bat
6. 마침 클릭
```

이후 매주 지정한 시각에 컴퓨터가 켜져 있으면 자동으로 리포트가 생성돼!

## 🧪 Tests

```cmd
pytest tests/ -v
```

## 📄 License

MIT
