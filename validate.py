#!/usr/bin/env python3
"""Validate input.json for learning video generation."""
import json, sys

def validate(path):
    with open(path) as f:
        data = json.load(f)

    errors = []

    # Required top-level keys
    for key in ['transcript_path', 'seg_range', 'video_path', 'output_path', 'hook', 'subtitles', 'cards']:
        if key not in data:
            errors.append(f"Missing top-level key: '{key}'")

    if errors:
        return errors

    # seg_range
    sr = data['seg_range']
    if not isinstance(sr, list) or len(sr) != 2:
        errors.append("seg_range must be [start_index, end_index]")
    elif sr[0] >= sr[1]:
        errors.append(f"seg_range[0] ({sr[0]}) must be < seg_range[1] ({sr[1]})")

    # hook
    hook = data['hook']
    for key in ['en', 'zh', 'accent']:
        if key not in hook:
            errors.append(f"hook missing '{key}'")
    if 'accent' in hook and 'en' in hook:
        if hook['accent'] not in hook['en']:
            errors.append(f"hook.accent '{hook['accent']}' not found in hook.en '{hook['en']}'")

    # subtitles
    seg_indices = set()
    for i, sub in enumerate(data['subtitles']):
        if 'seg_index' not in sub:
            errors.append(f"subtitles[{i}] missing 'seg_index'")
        elif not isinstance(sub['seg_index'], int):
            errors.append(f"subtitles[{i}].seg_index must be int")
        else:
            seg_indices.add(sub['seg_index'])
        if 'zh' not in sub:
            errors.append(f"subtitles[{i}] missing 'zh'")
        elif not sub['zh']:
            errors.append(f"subtitles[{i}].zh is empty")

    # cards
    for i, card in enumerate(data['cards']):
        for key in ['seg_index', 'highlight', 'zh', 'usage', 'example', 'type']:
            if key not in card:
                errors.append(f"cards[{i}] missing '{key}'")
        if 'type' in card:
            if card['type'] not in ('word', 'phrase', 'pattern'):
                errors.append(f"cards[{i}].type must be 'word', 'phrase' or 'pattern', got '{card['type']}'")
            if card['type'] == 'pattern' and 'title' not in card:
                errors.append(f"cards[{i}] type=pattern requires 'title' field")
        if 'seg_index' in card and card['seg_index'] not in seg_indices:
            errors.append(f"cards[{i}].seg_index {card['seg_index']} not in subtitles")

    return errors

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: validate.py <input.json>")
        sys.exit(1)

    errors = validate(sys.argv[1])
    if errors:
        print(f"VALIDATION FAILED ({len(errors)} errors):")
        for e in errors:
            print(f"  ❌ {e}")
        sys.exit(1)
    else:
        print("✅ Validation passed")
        sys.exit(0)
