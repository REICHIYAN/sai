from pathlib import Path
import html
import re

OUTPUTS_DIR = Path("outputs")
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

def convert_md_to_html(md_path: Path) -> str:
    """Markdownファイルを簡易HTMLに変換（リンク対応済）"""
    content = md_path.read_text(encoding="utf-8")

    def convert_line(line: str) -> str:
        if not line.strip():
            return ""
        # タイトル
        if line.startswith("## "):
            return f"<h2>{html.escape(line[3:])}</h2>"
        # MarkdownリンクをHTMLリンクに変換
        line = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda m: f'<a href="{html.escape(m.group(2))}">{html.escape(m.group(1))}</a>',
            line
        )
        return f"<p>{html.escape(line)}</p>"

    body = "\n".join(convert_line(line) for line in content.splitlines())

    title = html.escape(md_path.stem)
    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
</head>
<body>
  <h1>{title}</h1>
  {body}
</body>
</html>
"""

def build_index():
    """全HTML出力＋indexページ作成"""
    md_files = sorted(OUTPUTS_DIR.glob("*.md"), reverse=True)
    if not md_files:
        print("⚠️ Markdownファイルが見つかりません。")
        return

    entries = []
    latest_file = None

    for i, md_file in enumerate(md_files):
        html_file = DOCS_DIR / f"{md_file.stem}.html"
        html_content = convert_md_to_html(md_file)
        html_file.write_text(html_content, encoding="utf-8")

        display = html.escape(md_file.stem)
        entries.append(f'<li><a href="{html_file.name}">{display}</a></li>')

        if i == 0:
            latest_file = html_file.name

    index_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Paper Summaries</title>
</head>
<body>
  <h1>📚 Paper Summaries</h1>
  <p>🆕 最新はこちら → <a href="{latest_file}">{latest_file.replace('.html', '')}</a></p>

  <section>
    <ul>
      {'\n'.join(entries)}
    </ul>
  </section>
</body>
</html>
"""
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print("✅ HTML変換・index構築完了。")

if __name__ == "__main__":
    build_index()
