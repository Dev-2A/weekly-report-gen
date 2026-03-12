import os
from datetime import datetime
from pathlib import Path


class MarkdownRenderer:
    """
    생성된 회고 리포트를 Markdown 파일로 저장하는 렌더러
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, report_text: str, week_label: str, start_date: str) -> Path:
        """
        리포트 텍스트를 Markdown 파일로 저장합니다.
        
        Args:
            report_text: LLM이 생성한 회고 리포트 텍스트
            week_label: 주차 레이블 (예: '2026년 10주차 (03/02 ~ 03/08)')
            start_date: 주 시작일 (YYYY-MM-DD), 파일명에 사용
        
        Returns:
            저장된 파일 경로 (Path 객체)
        """
        filename = self._build_filename(start_date)
        filepath = self.output_dir / filename
        
        content = self._build_content(report_text, week_label)
        
        filepath.write_text(content, encoding="utf-8")
        print(f"📄 Markdown 리포트 저장 완료: {filepath}")
        
        return filepath
    
    def _build_filename(self, start_date: str) -> str:
        """
        파일명을 생성합니다.
        예: weekly-report-2026-03-02.md
        """
        return f"weekly-report-{start_date}.md"
    
    def _build_content(self, report_text: str, week_label: str) -> str:
        """
        파일에 저장할 최종 Markdown 문자열을 조립합니다.
        생성 메타데이터를 상단 주석으로 포함합니다.
        """
        generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        header = "\n".join([
            "<!--",
            f"  Weekly Report Generator",
            f"  주차: {week_label}",
            f"  생성일시: {generated_at}",
            "-->",
            "",
        ])
        
        return header + report_text


class ReportSummary:
    """
    저장된 리포트 목록을 조회하고 요약하는 유틸리티
    """
    
    def __init__(self, output_dir: str = "output"):
        self.output_dir = Path(output_dir)
    
    def list_reports(self) -> list[dict]:
        """
        output 디렉토리의 모든 리포트 파일 목록을 반환합니다.
        
        Returns:
            [{"filename": str, "path": Path, "created_at": str}, ...]
        """
        if not self.output_dir.exists():
            return []
        
        reports = []
        for filepath in sorted(self.output_dir.glob("weekly-report-*.md"), reverse=True):
            stat = filepath.stat()
            reports.append({
                "filename": filepath.name,
                "path": filepath,
                "created_at": datetime.fromtimestamp(stat.at_mtime).strftime(
                    "%Y-%m-%d %H:%M"
                ),
                "size_kb": round(stat.st_size / 1024, 1),
            })
        
        return reports
    
    def print_list(self) -> None:
        """저장된 리포트 목록을 터미널에 출력합니다."""
        reports = self.list_reports()
        
        if not reports:
            print("📭 저장된 리포트가 없습니다.")
            return

        print(f"\n📂 저장된 리포트 목록 ({len(reports)}개)\n")
        print(f"{'파일명':<40} {'생성일시':<20} {'크기':>8}")
        print("-" * 72)
        for r in reports:
            print(f"{r['filename']:<40} {r['created_at']:<20} {r['size_kb']:>6.1f} KB")
        print()
    
    def read(self, start_date: str) -> str | None:
        """
        특정 날짜의 리포트 파일 내용을 읽어 반환합니다.

        Args:
            start_date: 주 시작일 (YYYY-MM-DD)

        Returns:
            파일 내용 문자열, 파일이 없으면 None
        """
        filepath = self.output_dir / f"weekly-report-{start_date}.md"

        if not filepath.exists():
            print(f"⚠️  리포트 파일을 찾을 수 없습니다: {filepath}")
            return None

        return filepath.read_text(encoding="utf-8")