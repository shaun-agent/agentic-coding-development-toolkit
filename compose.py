#!/usr/bin/env python3
"""
Compose learning video: validate → gen ASS → gen cards → gen hook → ffmpeg.
Usage: python3 compose.py <input.json> [style.json]
"""
import json, sys, os, subprocess, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STYLE = os.path.join(SCRIPT_DIR, 'style.json')
NODE_PATH = os.environ.get('NODE_PATH', os.path.join(SCRIPT_DIR, 'node_modules'))

def run(cmd, check=True):
    print(f"  → {cmd[:80]}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ❌ FAILED: {result.stderr[:200]}")
        sys.exit(1)
    if result.stdout.strip():
        print(f"    {result.stdout.strip()}")
    return result

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compose.py <input.json> [style.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    style_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STYLE

    with open(input_path) as f:
        data = json.load(f)
    with open(style_path) as f:
        style = json.load(f)

    # Unique work dir based on output filename
    output_name = os.path.splitext(os.path.basename(data['output_path']))[0]
    tmp_dir = f'/tmp/learning_video_work_{output_name}'
    os.makedirs(tmp_dir, exist_ok=True)
    cards_dir = os.path.join(tmp_dir, 'cards')
    os.makedirs(cards_dir, exist_ok=True)

    ass_path = os.path.join(tmp_dir, 'subtitles.ass')
    hook_path = os.path.join(tmp_dir, 'hook.png')
    output_path = data['output_path']

    # Step 1: Validate
    print("\n[1/5] Validating input.json...")
    run(f"python3 {os.path.join(SCRIPT_DIR, 'validate.py')} {input_path}")

    # Step 2: Generate ASS
    print("\n[2/5] Generating ASS subtitles...")
    run(f"python3 {os.path.join(SCRIPT_DIR, 'gen_ass.py')} {input_path} {style_path} {ass_path}")

    # Step 3: Generate cards
    print("\n[3/5] Generating card PNGs...")
    run(f"NODE_PATH={NODE_PATH} node {os.path.join(SCRIPT_DIR, 'gen_cards.js')} {input_path} {style_path} {cards_dir}")

    # Step 4: Generate hook
    print("\n[4/5] Generating hook PNG...")
    run(f"NODE_PATH={NODE_PATH} node {os.path.join(SCRIPT_DIR, 'gen_hook.js')} {input_path} {style_path} {hook_path}")

    # Step 5: Compose with ffmpeg
    print("\n[5/5] Composing video with ffmpeg...")

    layout = style['layout']
    card_files = sorted(glob.glob(os.path.join(cards_dir, 'card_*.png')),
                       key=lambda x: int(os.path.basename(x).replace('card_','').replace('.png','')))
    num_cards = len(card_files)
    card_scale_w = int(layout['output_width'] * layout['card_scale_ratio'])

    # Read transcript to get card timing
    with open(data['transcript_path']) as f:
        transcript = json.load(f)
    segs = transcript['segments']
    first_idx = data['subtitles'][0]['seg_index']
    offset = segs[first_idx]['start']

    # Group cards by seg_index to get timing (same order as gen_cards.js)
    groups = {}
    for card in data['cards']:
        key = card['seg_index']
        if key not in groups:
            groups[key] = card
    sorted_keys = sorted(groups.keys())

    # Build ffmpeg command
    inputs = f"-i {data['video_path']} -i {hook_path}"
    for cf in card_files:
        inputs += f" -i {cf}"

    # Filter complex
    fc_parts = []
    fc_parts.append(f"[0:v]scale={layout['output_width']}:{layout['output_height']},ass={ass_path}[sub]")

    # Scale cards
    for i in range(num_cards):
        fc_parts.append(f"[{i+2}:v]scale={card_scale_w}:-1[c{i+1}]")

    # Hook overlay (input index 1)
    fc_parts.append(f"[sub][1:v]overlay=x=(W-w)/2:y={layout['hook_y']}[h]")

    # Card overlays
    prev = "h"
    for i, key in enumerate(sorted_keys):
        seg = segs[key]
        start = seg['start'] - offset
        end = seg['end'] - offset
        out = f"v{i+1}" if i < num_cards - 1 else "out"
        fc_parts.append(f"[{prev}][c{i+1}]overlay=x=(W-w)/2:y={layout['card_y_expr']}:enable='between(t,{start:.1f},{end:.1f})'[{out}]")
        prev = out

    filter_complex = ";".join(fc_parts)

    cmd = (f"ffmpeg -y {inputs} "
           f"-filter_complex \"{filter_complex}\" "
           f"-map '[out]' -map 0:a "
           f"-c:v libx264 -crf {layout['crf']} -preset fast "
           f"-c:a aac -b:a {layout['audio_bitrate']} "
           f"{output_path}")

    run(cmd)

    # Check file size
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Done! Output: {output_path} ({size_mb:.1f}MB)")
    if size_mb > 8:
        print(f"⚠️  File is {size_mb:.1f}MB (>8MB). Consider increasing CRF.")

if __name__ == '__main__':
    main()
