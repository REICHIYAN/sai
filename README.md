# 📚 sai - arXiv Daily Summarizer

`sai` は、最新の arXiv 論文（特に Machine Learning 分野）を毎日 1 件要約し、
英語・日本語の両方で Markdown に出力する自動化ツールです。

---

## 🚀 機能概要

* arXiv から `cs.LG` カテゴリの最新論文を1件取得（過去365日以内）
* 英語（200〜280文字）と日本語（140〜200文字）で要約
* `outputs/YYYY-MM-DD.md` に Markdown 出力
* `.env` に保存された OpenAI API キーを使用
* GitHub Actions を用いて定期実行 & 自動コミットも可能

---

## 🛠 セットアップ手順

```bash
# 1. クローン
$ git clone https://github.com/your-username/sai.git
$ cd sai

# 2. 仮想環境（任意）
$ python3 -m venv venv
$ source venv/bin/activate

# 3. 依存関係インストール
$ pip install -r requirements.txt

# 4. .env 作成
$ echo 'OPENAI_API_KEY="your-api-key-here"' > .env
```

---

## 📄 実行方法

```bash
$ python3 scripts/fetch_and_summarize.py
```

出力先: `outputs/YYYY-MM-DD.md`

---

## 📅 GitHub Actions 自動化

`.github/workflows/daily.yml` により毎朝 JST 8:00 に要約を自動生成＆コミット。

```yaml
on:
  schedule:
    - cron: '0 23 * * *'  # JST 8:00
  workflow_dispatch:
```

---

## 🧠 出力例

```markdown
## 🎓 Paper Title (2025-06-22)

- 🇬🇧 Summary（200〜280文字）
- 🇯🇵 要約（140〜200文字）
- ハッシュタグ：#cs.LG #cs.AI
- 🔗 [arXivリンク](https://arxiv.org/abs/2506.12345)
---
```

---

## 🔒 注意事項

* `.env` は `.gitignore` により push されません。
* OpenAI API 使用には課金が発生する可能性があります。

---

## 🧩 TODO / 今後の展望

* [ ] `seen_ids.txt` による重複回避（実装中）
* [ ] タグ自動分類（LLM分類器）
* [ ] GitHub Pages による公開日報化

---

## ©️ License

MIT License
