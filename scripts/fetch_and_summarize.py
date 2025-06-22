import os
import openai
import arxiv
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# ==== 初期化 ====
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ==== 設定 ====
CATEGORY = "cs.LG"
NUM_DAYS = 30
MAX_RESULTS = 5
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

# ==== 論文取得 ====
def get_paper_by_date(target_date: datetime):
    seen_ids = load_seen_ids()

    search = arxiv.Search(
        query=f"cat:{CATEGORY}",
        max_results=MAX_RESULTS * 5,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    for result in arxiv.Client().results(search):
        arxiv_id = result.get_short_id()
        published_date = result.published.date()

        if arxiv_id in seen_ids:
            continue
        if published_date != target_date.date():
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

# ==== Markdown整形 ====
def format_entry(paper, summary_en, summary_ja, tags: list[str]):
    entry = f"""## 🎓 {paper.title} ({paper.published.date()})

- 🇬🇧 {summary_en}
- 🇯🇵 {summary_ja}
- タグ：{' '.join(tags)}
- ハッシュタグ：#{' '.join(paper.categories)}
- 🔗 [{paper.entry_id}]({paper.entry_id})
---
"""
    return entry

# ==== 実行 ====
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Target date in YYYY-MM-DD format", type=str)
    args = parser.parse_args()

    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("❌ Invalid date format. Use YYYY-MM-DD.")
            return
    else:
        target_date = datetime.utcnow()

    papers = get_paper_by_date(target_date)
    if not papers:
        print(f"📬 No new papers found on {target_date.date()}.")
        return

    output_path = OUTPUT_DIR / f"{target_date.strftime('%Y-%m-%d')}.md"

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
