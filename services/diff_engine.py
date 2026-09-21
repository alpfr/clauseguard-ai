"""
ClauseGuard AI - Visual Redline & Diff Engine
Word-level and token-level legal clause comparison with Side-by-Side and Unified views.
"""

import difflib
import html
import re
from typing import Dict, Any, List, Tuple


def tokenize(text: str) -> List[str]:
    """
    Split text into words and non-word tokens (punctuation, whitespace)
    so that whitespace and formatting are preserved across diff reconstructions.
    """
    if not text:
        return []
    # Match contiguous word characters, contiguous whitespace, or single punctuation symbols
    return re.findall(r"\w+|\s+|[^\w\s]", text, re.UNICODE)


def compute_word_diff(original: str, proposed: str) -> Dict[str, Any]:
    """
    Compute tokenized word-level diff between original clause and proposed counter-language.
    Returns structured operations, statistics, and HTML representations:
    - left_html: Original clause with deleted/altered terms marked as <del class="diff-del">
    - right_html: Proposed clause with added/altered terms marked as <ins class="diff-ins">
    - unified_html: Standard legal redline showing both deletions and insertions inline
    """
    orig_clean = (original or "").strip()
    prop_clean = (proposed or "").strip()

    orig_tokens = tokenize(orig_clean)
    prop_tokens = tokenize(prop_clean)

    matcher = difflib.SequenceMatcher(None, orig_tokens, prop_tokens, autojunk=False)
    opcodes = matcher.get_opcodes()

    left_parts: List[str] = []
    right_parts: List[str] = []
    unified_parts: List[str] = []

    words_removed = 0
    words_added = 0
    words_unchanged = 0

    for tag, i1, i2, j1, j2 in opcodes:
        orig_chunk = "".join(orig_tokens[i1:i2])
        prop_chunk = "".join(prop_tokens[j1:j2])

        escaped_orig = html.escape(orig_chunk)
        escaped_prop = html.escape(prop_chunk)

        if tag == "equal":
            left_parts.append(escaped_orig)
            right_parts.append(escaped_prop)
            unified_parts.append(escaped_orig)
            # Count words (excluding purely whitespace)
            words_unchanged += len(re.findall(r"\w+", orig_chunk))

        elif tag == "replace":
            # In Left: show as deletion/struck-through
            left_parts.append(f'<del class="diff-del" title="Removed / Replaced">{escaped_orig}</del>')
            # In Right: show as addition/new protection
            right_parts.append(f'<ins class="diff-ins" title="Protective Counter-Proposal">{escaped_prop}</ins>')
            # In Unified: show deletion then insertion
            unified_parts.append(f'<del class="diff-del">{escaped_orig}</del><ins class="diff-ins">{escaped_prop}</ins>')

            words_removed += len(re.findall(r"\w+", orig_chunk))
            words_added += len(re.findall(r"\w+", prop_chunk))

        elif tag == "delete":
            left_parts.append(f'<del class="diff-del" title="Removed">{escaped_orig}</del>')
            unified_parts.append(f'<del class="diff-del">{escaped_orig}</del>')
            words_removed += len(re.findall(r"\w+", orig_chunk))

        elif tag == "insert":
            right_parts.append(f'<ins class="diff-ins" title="Added Protection">{escaped_prop}</ins>')
            unified_parts.append(f'<ins class="diff-ins">{escaped_prop}</ins>')
            words_added += len(re.findall(r"\w+", prop_chunk))

    total_orig_words = words_unchanged + words_removed
    change_ratio = (words_removed + words_added) / max(1, (total_orig_words + words_added))

    return {
        "original_raw": orig_clean,
        "proposed_raw": prop_clean,
        "left_html": "".join(left_parts),
        "right_html": "".join(right_parts),
        "unified_html": "".join(unified_parts),
        "stats": {
            "words_removed": words_removed,
            "words_added": words_added,
            "words_unchanged": words_unchanged,
            "change_percentage": round(change_ratio * 100, 1),
        }
    }
