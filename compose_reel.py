#!/usr/bin/env python3
"""
Compose Reel (9:16) learning video.
Usage: python3 compose_reel.py <input.json> [style.json]

Outputs 1080x1920 Reel format:
- ASS burned on original resolution → scale to 1080w
- Pad to 1080x1920 with video vertically centered
- Hook overlay at top of video area
- Cards overlay in bottom black area below video
"""
import json, sys, os, subprocess, glob

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_STYLE = os.path.join(SCRIPT_DIR, 'style.json')
NODE_PATH = os.environ.get('NODE_PATH', os.path.join(SCRIPT_DIR, 'node_modules'))

def run(cmd, check=True):
    print(f"  → {cmd[:100]}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"  ❌ FAILED: {result.stderr[:300]}")
        sys.exit(1)
    if result.stdout.strip():
        print(f"    {result.stdout.strip()}")
    return result

def get_video_dimensions(video_path):
    """Get video width and height via ffprobe."""
    cmd = f"ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 {video_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    parts = result.stdout.strip().split(',')
    return int(parts[0]), int(parts[1])

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 compose_reel.py <input.json> [style.json]")
        sys.exit(1)

    input_path = sys.argv[1]
    style_path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_STYLE

    with open(input_path) as f:
        data = json.load(f)
    with open(style_path) as f:
        style = json.load(f)

    output_name = os.path.splitext(os.path.basename(data['output_path']))[0]
    tmp_dir = f'/tmp/learning_video_reel_{output_name}'
    os.makedirs(tmp_dir, exist_ok=True)
    cards_dir = os.path.join(tmp_dir, 'cards')
    os.makedirs(cards_dir, exist_ok=True)

    ass_path = os.path.join(tmp_dir, 'subtitles.ass')
    hook_path = os.path.join(tmp_dir, 'hook.png')
    output_path = data['output_path']

    # Step 1: Validate
    print("\n[1/6] Validating input.json...")
    run(f"python3 {os.path.join(SCRIPT_DIR, 'validate.py')} {input_path}")

    # Step 2: Generate ASS
    print("\n[2/6] Generating ASS subtitles...")
    run(f"python3 {os.path.join(SCRIPT_DIR, 'gen_ass.py')} {input_path} {style_path} {ass_path}")

    # Step 3: Generate cards
    print("\n[3/6] Generating card PNGs...")
    run(f"NODE_PATH={NODE_PATH} node {os.path.join(SCRIPT_DIR, 'gen_cards.js')} {input_path} {style_path} {cards_dir}")

    # Step 4: Generate hook
    print("\n[4/6] Generating hook PNG...")
    run(f"NODE_PATH={NODE_PATH} node {os.path.join(SCRIPT_DIR, 'gen_hook.js')} {input_path} {style_path} {hook_path}")

    # Step 5: Build Reel ffmpeg command
    print("\n[5/6] Building Reel ffmpeg command...")

    with open(data['transcript_path']) as f:
        transcript = json.load(f)
    segs = transcript['segments']

    first_idx = data['subtitles'][0]['seg_index']
    last_idx = data['subtitles'][-1]['seg_index']
    offset = segs[first_idx]['start']
    duration = segs[last_idx]['end'] - offset + 0.3

    # Get original video dimensions for dynamic layout
    video_path = data['video_path']
    orig_w, orig_h = get_video_dimensions(video_path)

    # Calculate scaled height (width fixed at 1080)
    scaled_h = int(1080 * orig_h / orig_w)
    if scaled_h % 2 != 0:
        scaled_h += 1

    # Dynamic layout: video vertically centered
    video_y = (1920 - scaled_h) // 2
    hook_y = video_y  # hook at top of video
    card_y = video_y + scaled_h + 16  # cards just below video

    card_available = 1920 - card_y - 10
    card_scale_w = min(900, 1080 - 40)

    print(f"    Layout: video={orig_w}x{orig_h} → scaled=1080x{scaled_h}")
    print(f"    video_y={video_y}, hook_y={hook_y}, card_y={card_y}, card_area={card_available}px")

    if card_available < 80:
        print(f"  ⚠️  Video too tall ({scaled_h}px), card area insufficient ({card_available}px). Consider cropping to 16:9.")
        sys.exit(1)

    # Card timing: group by seg_index
    seen_keys = []
    for card in data['cards']:
        if card['seg_index'] not in seen_keys:
            seen_keys.append(card['seg_index'])

    card_files = sorted(glob.glob(os.path.join(cards_dir, 'card_*.png')),
                       key=lambda x: int(os.path.basename(x).replace('card_', '').replace('.png', '')))
    num_cards = len(card_files)

    if num_cards != len(seen_keys):
        print(f"  ⚠️  Card PNG count ({num_cards}) != unique card segments ({len(seen_keys)})")
        sys.exit(1)
    print(f"    ✅ {num_cards} cards, {len(data['subtitles'])} subtitles, duration={duration:.1f}s")

    # Build ffmpeg
    inputs = f"-ss {offset} -to {offset + duration} -i {video_path} -i {hook_path}"
    for cf in card_files:
        inputs += f" -i {cf}"

    fc_parts = []
    # Burn ASS on original → scale → pad with video centered
    fc_parts.append(f"[0:v]ass={ass_path},scale=1080:{scaled_h},pad=1080:1920:0:{video_y}:black[bg]")
    fc_parts.append(f"[1:v]scale=648:-1[hook]")
    for i in range(num_cards):
        fc_parts.append(f"[{i+2}:v]scale={card_scale_w}:-1[c{i+1}]")
    # Hook overlay at top of video area
    fc_parts.append(f"[bg][hook]overlay=x=(W-w)/2:y={hook_y}:enable='between(t,0,{duration:.1f})'[h]")

    prev = "h"
    for i, key in enumerate(seen_keys):
        seg = segs[key]
        start = seg['start'] - offset
        end = seg['end'] - offset
        out = f"v{i+1}" if i < num_cards - 1 else "out"
        fc_parts.append(f"[{prev}][c{i+1}]overlay=x=(W-w)/2:y={card_y}:enable='between(t,{start:.2f},{end:.2f})'[{out}]")
        prev = out

    filter_complex = ";".join(fc_parts)
    cmd = (f"ffmpeg -y {inputs} "
           f"-filter_complex \"{filter_complex}\" "
           f"-map '[out]' -map 0:a "
           f"-c:v libx264 -crf 26 -preset fast "
           f"-c:a aac -b:a 96k "
           f"{output_path}")

    # Step 6: Execute ffmpeg
    print("\n[6/6] Composing Reel video...")
    run(cmd)

    # Final verification
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n✅ Done! Output: {output_path} ({size_mb:.1f}MB)")

    probe = subprocess.run(
        f"ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 {output_path}",
        shell=True, capture_output=True, text=True)
    dims = probe.stdout.strip()
    if dims != "1080,1920":
        print(f"  ⚠️  Output resolution is {dims}, expected 1080,1920")
    else:
        print(f"    ✅ Resolution: {dims}")

    if size_mb > 8:
        print(f"  ⚠️  File is {size_mb:.1f}MB (>8MB Discord limit). Consider increasing CRF.")

if __name__ == '__main__':
    main()
