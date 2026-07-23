#!/usr/bin/env python3
"""Generate ASS subtitle file from input.json + style.json."""
import json, sys, re

def fmt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def main(input_path, style_path, output_path):
    with open(input_path) as f:
        data = json.load(f)
    with open(style_path) as f:
        style = json.load(f)
    with open(data['transcript_path']) as f:
        transcript = json.load(f)

    segs = transcript['segments']
    sub_style = style['subtitle']

    # Build highlight map: seg_index -> [phrase1, phrase2, ...]
    highlight_map = {}
    for card in data['cards']:
        idx = card['seg_index']
        if idx not in highlight_map:
            highlight_map[idx] = []
        highlight_map[idx].append(card['highlight'])

    # Find offset from first subtitle segment
    first_idx = data['subtitles'][0]['seg_index']
    offset = segs[first_idx]['start']

    # ASS header
    header = f"""[Script Info]
Title: Language Learning
ScriptType: v4.00+
PlayResX: {sub_style['play_res_x']}
PlayResY: {sub_style['play_res_y']}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: En,{sub_style['en_font']},{sub_style['en_size']},&H00FFFFFF,&H000000FF,&H00000000,&H{sub_style['bg_color']},-1,0,0,0,100,100,0,0,3,2,0,2,{sub_style['margin_lr']},{sub_style['margin_lr']},{sub_style['margin_v']},1
Style: Zh,{sub_style['zh_font']},{sub_style['zh_size']},&H00FFFFFF,&H000000FF,&H00000000,&H{sub_style['bg_color']},0,0,0,0,100,100,0,0,3,1.5,0,2,{sub_style['margin_lr']},{sub_style['margin_lr']},{sub_style['margin_v']},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    # Pre-pass: detect cross-segment highlights and build spillover map
    # spillover_map[next_seg_idx] = [remainder_phrase, ...]
    spillover_map = {}
    failed_highlights = []

    for idx, phrases in highlight_map.items():
        seg_text = segs[idx]['text'].strip()
        for phrase in phrases:
            pattern = re.compile(re.escape(phrase), re.IGNORECASE)
            match = pattern.search(seg_text)
            if match:
                continue  # found in this segment, no issue

            # Not found - try cross-segment match
            next_idx = idx + 1
            resolved = False
            if next_idx < len(segs):
                next_text = segs[next_idx]['text'].strip()
                combined = seg_text + " " + next_text
                cmatch = re.search(re.escape(phrase), combined, re.IGNORECASE)
                if cmatch:
                    # Find where seg_text ends in combined
                    split_pos = len(seg_text) + 1  # +1 for the space
                    if cmatch.start() < split_pos:
                        # Phrase starts in seg[idx]
                        tail_in_current = combined[cmatch.start():split_pos].strip()
                        head_in_next = combined[split_pos:cmatch.end()].strip()
                        # Validate: head_in_next must be at the start of next_text
                        if next_text.lower().startswith(head_in_next.lower()):
                            # Valid cross-segment highlight
                            # Replace the phrase in highlight_map with just the tail
                            phrases[phrases.index(phrase)] = tail_in_current
                            # Add spillover for next segment
                            if next_idx not in spillover_map:
                                spillover_map[next_idx] = []
                            spillover_map[next_idx].append(head_in_next)
                            resolved = True
                            print(f"  ↔ Cross-segment: seg {idx}→{next_idx}: \"{tail_in_current}\" + \"{head_in_next}\"")

            if not resolved:
                failed_highlights.append((idx, phrase, seg_text))

    # Print failures
    for idx, phrase, seg_text in failed_highlights:
        print(f"  ❌ Highlight not found in seg {idx}: \"{phrase}\"")
        print(f"     seg {idx} text: \"{seg_text[:80]}...\"" if len(seg_text) > 80 else f"     seg {idx} text: \"{seg_text}\"")

    lines = []
    for i, sub in enumerate(data['subtitles']):
        idx = sub['seg_index']
        seg = segs[idx]
        text = seg['text'].strip()
        zh = sub['zh']
        start = seg['start'] - offset
        end = seg['end'] - offset
        if start < 0:
            start = 0

        # Buffer: extend end by up to 0.3s without overlapping next subtitle
        if i < len(data['subtitles']) - 1:
            next_sub_idx = data['subtitles'][i + 1]['seg_index']
            next_start = segs[next_sub_idx]['start'] - offset
            buffer = min(0.3, next_start - end)
        else:
            buffer = 0.3
        end += max(0, buffer)

        # Apply highlight if this segment has one
        en_display = text
        color = sub_style['highlight_color']

        # Apply highlights from highlight_map (includes modified cross-segment tails)
        if idx in highlight_map:
            for phrase in highlight_map[idx]:
                pattern = re.compile(re.escape(phrase), re.IGNORECASE)
                match = pattern.search(en_display)
                if match:
                    orig = match.group()
                    en_display = (en_display[:match.start()] +
                                "{\\c&H" + color + "&}" + orig + "{\\c&H00FFFFFF&}" +
                                en_display[match.end():])

        # Apply spillover highlights (cross-segment head from previous segment's card)
        if idx in spillover_map:
            for phrase in spillover_map[idx]:
                # Must match at the start of the text (after stripping)
                pattern = re.compile(r'^' + re.escape(phrase), re.IGNORECASE)
                match = pattern.search(en_display)
                if match:
                    orig = match.group()
                    en_display = ("{\\c&H" + color + "&}" + orig + "{\\c&H00FFFFFF&}" +
                                en_display[match.end():])

        line = f"Dialogue: 0,{fmt_time(start)},{fmt_time(end)},En,,0,0,0,,{en_display}\\N{{\\rZh}}{zh}"
        lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header + "\n".join(lines) + "\n")

    # Verification: count highlight color tags
    highlight_count = sum(l.count("\\c&H") // 2 for l in lines)
    # Expected = cards + spillovers (cross-segment counts as 2 highlights)
    expected = len(data['cards']) + len([p for ps in spillover_map.values() for p in ps])
    missing_zh = sum(1 for sub in data['subtitles'] if not sub.get('zh'))

    print(f"Generated {len(lines)} subtitle lines")
    print(f"Missing translations: {missing_zh}")
    print(f"Highlighted lines: {highlight_count} (expected {expected})")

    if missing_zh > 0 or highlight_count != expected or failed_highlights:
        print("⚠️  VERIFICATION WARNING")
        return 1
    print("✅ ASS generation passed")
    return 0

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: gen_ass.py <input.json> <style.json> <output.ass>")
        sys.exit(1)
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3]))
