# tests/test_summary.py

import sys
from pathlib import Path
from unittest.mock import patch
import pytest

# スクリプトディレクトリを import パスに追加
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))
from fetch_and_summarize import summarize_ja

@patch("fetch_and_summarize.openai.chat.completions.create")
def test_summarize_ja_mock(mock_create):
    # モックが返すレスポンス（現在の出力仕様に合わせる）
    mock_create.return_value.choices = [
        type("Choice", (), {
            "message": type("Message", (), {
                "content": "arXiv:1234.56789v1\nこれはモックの要約です。\n[詳細はこちら](https://arxiv.org/abs/1234.56789)"
            })()
        })
    ]

    arxiv_id = "1234.56789v1"
    abstract = "This paper proposes a novel transformer-based architecture."
    url = "https://arxiv.org/abs/1234.56789"

    result = summarize_ja(arxiv_id, abstract, url)

    assert isinstance(result, str)
    assert result.startswith(f"arXiv:{arxiv_id}")
    assert "[詳細はこちら]" in result
    assert url in result
