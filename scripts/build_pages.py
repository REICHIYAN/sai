from pathlib import Path
from datetime import datetime

OUTPUTS_DIR = Path("outputs")
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

def convert_md_to_html(md_path: Path) -> str:
    content = md_path.read_text(encoding="utf-8")
    body = "\n".join(
        f"<p>{line}</p>" if not line.startswith("## ") else f"<h2>{line[3:]}</h2>"
        for line in content.splitlines()
    )
    return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{md_path.stem}</title>
</head>
<body>
<h1>{md_path.stem}</h1>
{body}
</body>
</html>
"""

def main():
    md_files = sorted(OUTPUTS_DIR.glob("*.md"), reverse=True)

    entries = []
    latest_file = None

    for md_file in md_files:
        html_file = DOCS_DIR / f"{md_file.stem}.html"
        html_content = convert_md_to_html(md_file)
        html_file.write_text(html_content, encoding="utf-8")

        link = f'<li><a href="{html_file.name}">{md_file.stem}</a></li>'
        entries.append(link)

        if latest_file is None:
            latest_file = html_file.name  # 最初の（最新の）ファイルを取得

    index_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Paper Summaries</title>
</head>
<body>
  <h1>📚 Paper Summaries</h1>

  <!-- ✅ 最新リンクをトップに表示 -->
  <p>🆕 最新はこちら → <a href="{latest_file}">{latest_file.replace('.html', '')}</a></p>

  <ul>
    {''.join(entries)}
  </ul>
</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print("✅ GitHub Pages index updated with latest link.")

if __name__ == "__main__":
    main()
