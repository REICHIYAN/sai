import os
import openai
import arxiv
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ==== 設定 ====
CATEGORY = "cs.LG"
NUM_DAYS = 30
MAX_RESULTS = 1
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)

def get_recent_papers():
    today = datetime.utcnow()
    start_date = today - timedelta(days=NUM_DAYS)
    search = arxiv.Search(
        query=f"cat:{CATEGORY}",
        max_results=MAX_RESULTS,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )
    papers = []
    for result in arxiv.Client().results(search):
        if result.published.date() >= start_date.date():
            papers.append(result)
    return papers

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

def format_entry(paper, summary_en, summary_ja):
    entry = f"""## 🎓 {paper.title} ({paper.published.date()})

- 🇬🇧 {summary_en}
- 🇯🇵 {summary_ja}
- ハッシュタグ：#{' '.join(paper.categories)}
- 🔗 [{paper.entry_id}]({paper.entry_id})
---
"""
    return entry

def main():
    papers = get_recent_papers()
    if not papers:
        print("📬 No new papers found in the last 3 days.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"{today_str}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        for paper in papers:
            summary_en = summarize(paper.summary, lang="en")
            summary_ja = summarize(paper.summary, lang="ja")
            entry = format_entry(paper, summary_en, summary_ja)
            f.write(entry + "\n")

    print(f"✅ Summary written to {output_path}")

if __name__ == "__main__":
    main()
