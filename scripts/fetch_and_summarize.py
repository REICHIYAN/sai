import os
import openai
import arxiv
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# ==== 初期化 ====
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ==== 設定 ====
CATEGORY = "cs.*"
MAX_RESULTS = 1
OUTPUT_DIR = Path("outputs")
SEEN_IDS_FILE = Path("seen/seen_ids.txt")

OUTPUT_DIR.mkdir(exist_ok=True)
SEEN_IDS_FILE.parent.mkdir(exist_ok=True)
if not SEEN_IDS_FILE.exists():
    SEEN_IDS_FILE.touch()

# ==== 重複チェック ====
def load_seen_ids() -> set:
    with open(SEEN_IDS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def save_seen_id(arxiv_id: str) -> None:
    with open(SEEN_IDS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{arxiv_id}\n")

# ==== 論文取得（強制取得）====
def get_first_unseen_paper():
    seen_ids = load_seen_ids()

    search = arxiv.Search(
        query=f"cat:{CATEGORY}",
        max_results=MAX_RESULTS * 10,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    for result in arxiv.Client().results(search):
        arxiv_id = result.get_short_id()
        if arxiv_id in seen_ids:
            continue

        save_seen_id(arxiv_id)
        return [result]

    return []

# ==== 要約処理 ====
def summarize(text: str, lang: str) -> str:
    if lang == "en":
        prompt = f"Summarize the following abstract in English in 200 to 280 characters:\n{text}"
    else:
        prompt = f"次の英文要約を、日本語で140〜200文字に要約してください：\n{text}"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a concise academic assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()

# ==== タグ補完 ====
def generate_tags(title: str, summary: str) -> list[str]:
    prompt = f"""以下は論文のタイトルと要約です。
この論文の主な技術・研究分野を、英語のハッシュタグ形式で最大3つ出力してください（例：#LLM #ReinforcementLearning）。

タイトル：
{title}

要約：
{summary}
"""
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in machine learning research topics."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    tags_text = response.choices[0].message.content.strip()
    tags = [tag.strip() for tag in tags_text.split() if tag.startswith("#")]
    return tags[:3]

# ==== Markdown出力 ====
def format_entry(paper, summary_en, summary_ja, tags: list[str]) -> str:
    return f"""## 🎓 {paper.title} ({paper.published.date()})

- 🇬🇧 {summary_en}
- 🇯🇵 {summary_ja}
- タグ：{' '.join(tags)}
- ハッシュタグ：#{' '.join(paper.categories)}
- 🔗 [{paper.entry_id}]({paper.entry_id})
---
"""

# ==== 実行 ====
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="(無視されます) 互換性のための引数", type=str)
    args = parser.parse_args()

    papers = get_first_unseen_paper()
    if not papers:
        print("📬 No new papers found.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"{today_str}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        for paper in papers:
            summary_en = summarize(paper.summary, lang="en")
            summary_ja = summarize(paper.summary, lang="ja")
            tags = generate_tags(paper.title, paper.summary)
            entry = format_entry(paper, summary_en, summary_ja, tags)
            f.write(entry + "\n")

    print(f"✅ Summary written to {output_path}")

if __name__ == "__main__":
    main()
