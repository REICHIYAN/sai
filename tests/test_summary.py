import sys
import os
from pathlib import Path
import pytest

# ✅ scripts/ ディレクトリをインポート可能にする
sys.path.append(str(Path(__file__).resolve().parent.parent / "scripts"))

from fetch_and_summarize import summarize, generate_tags

@pytest.mark.parametrize("lang", ["en", "ja"])
def test_summarize_returns_text(lang):
    text = (
        "This paper proposes a novel transformer-based architecture "
        "for few-shot learning with enhanced memory retrieval."
    )
    result = summarize(text, lang=lang)
    assert isinstance(result, str)
    assert len(result) > 0
    assert len(result) < 300

def test_generate_tags_returns_hashtags():
    title = "Scaling Laws for Neural Language Models"
    summary = "This study examines the impact of model size on performance in various NLP tasks."
    tags = generate_tags(title, summary)
    assert isinstance(tags, list)
    assert all(tag.startswith("#") for tag in tags)
    assert 1 <= len(tags) <= 3
