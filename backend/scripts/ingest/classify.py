"""
Use LLM to upgrade raw_text → QuestionDraft.proposed.

用法: python -m scripts.ingest.classify < input.normalized.jsonl > output.jsonl
用法(直接): cat data/drafts/2022.raw.jsonl | python -m scripts.ingest.normalize | python -m scripts.ingest.classify > data/drafts/2022.jsonl

In Stage 1, this is a rule-based pass. Stage 3 will integrate with LLM.
"""
from __future__ import annotations
import json
import sys
from typing import Optional

# Simple keyword-based classification rules for FAKAO subjects (Stage 1)
SUBJECT_KEYWORDS: dict[str, list[str]] = {
    "civil": ["民法", "民事", "物权", "合同", "侵权", "婚姻", "继承"],
    "criminal": ["刑法", "犯罪", "刑罚", "故意", "过失", "正当防卫"],
    "admin": ["行政法", "行政", "行政许可", "行政处罚", "行政复议"],
    "commercial": ["商法", "经济法", "公司", "合伙", "破产", "票据"],
    "intl": ["国际法", "国际私法", "国际经济法", "条约", "冲突"],
    "theory": ["理论法", "法理学", "宪法", "法制史", "法治"],
    "crim-proc": ["刑事诉讼法", "刑诉", "侦查", "起诉", "审判"],
    "civ-proc": ["民事诉讼法", "民诉", "诉讼", "管辖", "证据"],
}


def rule_based_classify(text: str) -> dict:
    """Simple keyword-matching classification for 法考 subjects."""
    subject = "unknown"
    max_score = 0

    for subj, keywords in SUBJECT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > max_score:
            max_score = score
            subject = subj

    return {
        "curriculum": "FAKAO",
        "subject": subject,
        "topic_path": [],
        "type": "single_choice",
        "difficulty": 3,
    }


def classify_draft(draft: dict) -> dict:
    """Classify a QuestionDraft, either by rules or LLM."""
    raw_text = draft.get("raw_text", draft.get("proposed", {}).get("stem", ""))
    proposed = draft.get("proposed", {})
    classification = rule_based_classify(raw_text)

    # Merge classification into proposed
    proposed.update(classification)
    draft["proposed"] = proposed
    return draft


if __name__ == "__main__":
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            draft = json.loads(line)
            classified = classify_draft(draft)
            print(json.dumps(classified, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(json.dumps({"error": str(e), "raw": line}), file=sys.stderr)