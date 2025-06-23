import os
import openai
import arxiv
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from dotenv import load_dotenv

# ==== 初期化 ====
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ==== 定数 ====
CATEGORIES = ["cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.NE"]
MAX_RESULTS = 1
DAYS_BACK = 365
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
def get_first_unseen_paper():
    seen_ids = load_seen_ids()
    start_time = datetime.now(timezone.utc) - timedelta(days=DAYS_BACK)

    query = " OR ".join([f"cat:{cat}" for cat in CATEGORIES])
    search = arxiv.Search(
        query=query,
        max_results=MAX_RESULTS * 10,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    )

    client = arxiv.Client()
    for result in client.results(search):
        if result.published < start_time:
            continue
        arxiv_id = result.get_short_id()
        if arxiv_id in seen_ids:
            continue
        save_seen_id(arxiv_id)
        return [result]

    return []

# ==== 要約処理 ====
def summarize_ja(arxiv_id: str, abstract: str, url: str) -> str:
    prompt = f"次の英文要約を、日本語で105文字以内に簡潔に要約してください：\n{abstract}"

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "あなたは日本語で簡潔に書く技術ライターです。出力は全角105文字以内にしてください。"
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=110,
    )

    summary = response.choices[0].message.content.strip()
    if not summary:
        summary = "（要約取得失敗）"
    else:
        summary = summary.replace("\n", " ").strip()[:105]  # 改行削除＋文字数制限

    return summary + "\n" + f"[Link]({url})"

# ==== メイン処理 ====
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="※未使用：互換性のために存在", type=str)
    parser.parse_args()

    papers = get_first_unseen_paper()
    if not papers:
        print("📬 No new papers found.")
        return

    today_str = datetime.now().strftime("%Y-%m-%d")
    output_path = OUTPUT_DIR / f"{today_str}.md"

    with open(output_path, "w", encoding="utf-8") as f:
        for paper in papers:
            print(f"🧾 Summarizing: {paper.title}")
            summary = summarize_ja(
                arxiv_id=paper.get_short_id(),
                abstract=paper.summary,
                url=paper.entry_id
            )
            f.write(summary + "\n\n")

    print(f"✅ Summary written to {output_path}")

if __name__ == "__main__":
    main()
