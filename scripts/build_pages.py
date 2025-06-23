from pathlib import Path
import html
import re

OUTPUTS_DIR = Path("outputs")
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

def convert_md_to_html(md_path: Path) -> str:
    """2行構成（要約 + URL）MarkdownファイルをHTMLに変換"""
    content = md_path.read_text(encoding="utf-8").strip()
    lines = content.splitlines()

    html_parts = []
    block = []

    for line in lines:
        line = line.strip()
        if not line:
            if block:
                # 2行目がURLならリンク付きで出力
                summary = html.escape(block[0])
                if len(block) > 1 and block[1].startswith("http"):
                    url = html.escape(block[1])
                    html_parts.append(f"<p>{summary}<br>\n<a href=\"{url}\">{url}</a></p>")
                else:
                    html_parts.append(f"<p>{summary}</p>")
                block = []
            continue
        block.append(line)

    # 最後のブロック処理
    if block:
        summary = html.escape(block[0])
        if len(block) > 1 and block[1].startswith("http"):
            url = html.escape(block[1])
            html_parts.append(f"<p>{summary}<br>\n<a href=\"{url}\">{url}</a></p>")
        else:
            html_parts.append(f"<p>{summary}</p>")

    title = html.escape(md_path.stem)
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"ja\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"  <title>{title}</title>\n"
        "</head>\n"
        "<body>\n"
        f"<h1>{title}</h1>\n"
        + "\n".join(html_parts) +
        "\n</body>\n</html>\n"
    )

def build_index():
    """すべてのMarkdown→HTMLに変換し、indexページを作成"""
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

    entries_html = "\n".join(entries)
    latest_link = latest_file.replace(".html", "") if latest_file else ""

    index_html = (
        "<!DOCTYPE html>\n"
        "<html lang=\"ja\">\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "  <title>Paper Summaries</title>\n"
        "</head>\n"
        "<body>\n"
        "  <h1>📚 Paper Summaries</h1>\n"
        f"  <p>🆕 最新はこちら → <a href=\"{latest_file}\">{latest_link}</a></p>\n"
        "  <section>\n"
        f"    <ul>\n{entries_html}\n    </ul>\n"
        "  </section>\n"
        "</body>\n"
        "</html>\n"
    )

    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")
    print("✅ HTML変換・index構築完了。")

if __name__ == "__main__":
    build_index()
