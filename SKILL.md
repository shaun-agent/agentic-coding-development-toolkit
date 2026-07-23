---
name: video-language-learning
description: "Video language learning: bilingual subtitles (with keyword highlighting) + vocabulary card overlays. Auto-detects landscape/Reel portrait format. Any language pair. Use when user says \"learning video\", \"subtitle cards\", \"video language learning\", \"reel\", \"reels\", or wants bilingual subtitles and vocab cards on a video."
---

# Video Language Learning

Add bilingual subtitles and vocabulary cards to any video. Supports any source and target language pair.

## Setup: Environment Installation

On first use, verify and install the following tools in order:

### 1. System Tools (Homebrew)

```bash
# Verify Homebrew is installed
which brew || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install ffmpeg (includes libass for subtitle burning)
brew install ffmpeg

# Install yt-dlp (video download)
brew install yt-dlp

# Install Node.js (card/hook rendering)
brew install node
```

### 2. Python Packages

```bash
# Install mlx-whisper (Apple Silicon speech-to-text)
pip install mlx-whisper
```

**mlx-whisper:** Apple's [MLX](https://github.com/ml-explore/mlx-examples/tree/main/whisper) framework Whisper implementation, optimized for Apple Silicon.

**Model:** Uses [mlx-community/whisper-large-v3-turbo](https://huggingface.co/mlx-community/whisper-large-v3-turbo). More available models at [MLX Community Whisper collection](https://huggingface.co/collections/mlx-community/whisper-663256f9964fbb1177db93dc).

On first transcription, the model is automatically downloaded from Hugging Face and cached at `~/.cache/huggingface/`. Works offline afterward.

To pre-download:
```bash
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('mlx-community/whisper-large-v3-turbo')"
```

### 3. Node.js Dependencies

```bash
cd <this-repo-directory>
npm install    # Installs Playwright + downloads Chromium
```

### 4. Verify Installation

```bash
ffmpeg -version | head -1          # Should show version number
yt-dlp --version                   # Should show date version
node --version                     # Should show v18+
python3 -c "import mlx_whisper; print('ok')"  # Should print ok
npx playwright --version           # Should show version number
```

Once all pass, you're ready to go.

---

## Parameters

- **Source language**: Original video language (auto-detect or manually specified)
- **Target language**: Default Traditional Chinese (user's native language)
- **Orientation**: Auto-detect (width > height → landscape, height > width → portrait)
- **Clip length**: 1-2 minutes (for focused study, easy to replay). If user doesn't specify segmenting, automatically split long videos into 1-2 minute semantically complete sections.

## Pipeline Overview

1. Get video (URL or local file)
2. Detect orientation and resolution
3. Transcribe (mlx_whisper)
4. **Knowledge segment discovery** — AI reads full transcript, identifies segments worth making into independent clips
5. User selects which segments to produce
6. Translate (only selected segments) + select vocabulary highlights
7. Prepare input.json (containing subtitles, cards, hook)
8. Compose output:
   - **Mode A (Landscape)**: `compose.py` one-shot (auto-runs gen_ass + gen_cards + gen_hook + ffmpeg)
   - **Mode B (Reel)**: `compose_reel.py` one-shot (auto-runs full pipeline + resolution verification)

## Step 0: Get Video

```bash
# Audio only (for transcription)
yt-dlp -x --audio-format wav -o '/tmp/yt-dlp_download/%(id)s.%(ext)s' '<URL>'

# Full video (for subtitle burning)
rm -rf /tmp/yt-dlp_download && mkdir -p /tmp/yt-dlp_download && \
yt-dlp -f 'bestvideo+bestaudio' --merge-output-format mp4 \
  -o '/tmp/yt-dlp_download/%(id)s.%(ext)s' '<URL>'
```

## Step 1: Detect Orientation and Resolution

```bash
ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=p=0 <FILE>
```

Set global variables based on result:

```
WIDTH, HEIGHT = ffprobe result
ORIENTATION = "landscape" if WIDTH > HEIGHT else "portrait"
```

## Step 2: Transcribe

```bash
# Convert to 16kHz WAV
ffmpeg -y -i '<INPUT_FILE>' -vn -acodec pcm_s16le -ar 16000 /tmp/whisper_out/input_16k.wav
```

```python
import mlx_whisper, json, os

os.makedirs('/tmp/whisper_out', exist_ok=True)
result = mlx_whisper.transcribe(
    '/tmp/whisper_out/input_16k.wav',
    path_or_hf_repo='mlx-community/whisper-large-v3-turbo',
    condition_on_previous_text=False,  # Prevents hallucination
    word_timestamps=True
)
with open('/tmp/whisper_out/{VIDEO_ID}_transcript.json', 'w') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print(f'done - {len(result.get("segments", []))} segments')
```

**Filename rules:**
- URL-downloaded video: `{video_id}_transcript.json` (e.g., `cUbe6HbFncE_transcript.json`)
- Local file: `{filename_without_ext}_{hash8}_transcript.json` (e.g., `my_recording_a3f2b1c9_transcript.json`)

The `transcript_path` in input.json points to this unique filename.

## Step 2.5: Knowledge Segment Discovery

AI reads the full transcript and identifies segments that can stand alone as learning video clips.

**Criteria:**
- Has a clear knowledge point (a concept/method/principle, not small talk or repetition)
- Semantically complete (has beginning, core, and ending — doesn't cut mid-thought)
- 60-90 seconds (12-20 segments)
- Oral language has learning value (contains phrases/patterns worth practicing)

**Output format:**
List all candidate segments with:
- Segment range (start and end index)
- Duration in seconds
- Topic summary (one sentence describing what can be learned)

**Only proceed to translation after user selects which segments to produce.**

## Step 3: Translation + Vocabulary Selection

AI completes the following:

### 3.1 Translation

**Translate with context, display per segment.**

1. Send adjacent segments in groups of 3-5 for translation (providing full context)
2. Translation results map back one-to-one per sentence (no merging)
3. Each segment displays as its own subtitle line

Translation principles:
- **Stay close to spoken form**: preserve filler words (I don't know, you know, sort of like)
- Don't omit hesitations, repetitions, or self-corrections in speech
- Keep tone conversational in target language

### 3.2 Vocabulary Selection

**Selection criteria (oral-language focused):**
- ✅ High-frequency in native speaker speech, but learners might "understand but wouldn't actively produce"
- ✅ Practical framing phrases, discourse markers, phrasal verbs
- ❌ Too academic/literary rare words (e.g., nascent)
- ❌ Too simple words learners already actively use

**Quantity rules (by video length):**
| Video Length | Suggested Count |
|---|---|
| 30-60 seconds | 5-7 |
| 1-2 minutes | 8-12 |
| 2-3 minutes | 12-15 |

Can be fewer if content isn't rich enough, but don't pad.

**Mix rules:**
- 30-40% phrases (phrasal verbs, discourse markers, common collocations)
- 20-30% single words (oral high-frequency but learners rarely produce)
- 30-40% sentence patterns (framing sentences, subjunctive mood, conditionals)

**Highlight rules:**
- Each keyword is only highlighted in its corresponding card segment, no global matching
- Use segment start time for precise matching, not string search

**Same-segment merge rules:**
- Multiple keywords in same segment → merge into one card PNG
- Card display time = that segment's start ~ end (full sentence, not word-level timestamp)
- Max 2 cards displayed simultaneously; if 3 overlap, avoid during selection

Each keyword records:
- Word/phrase
- Target language explanation
- Usage note
- Additional example sentence (not from the source — subtitles already show that)

### Subtitle Segmentation Principles

**Use whisper's segments directly as subtitle units. Do not merge.**

Whisper already segments based on speech pauses and semantics (each segment ~3-10 seconds). Use as-is:
- Each segment = one subtitle line
- Translated independently
- Short lines are readable and sync with speech

Only consider merging adjacent segments when whisper breaks too finely (< 2 second fragments).

**Do not combine multiple complete sentences into one long subtitle.**

### Translation Strategy: Context-Aware Translation, Per-Segment Display

(See Step 3.1 translation principles)

**Translation prompt example:**
```
Below are consecutive segments from a video transcript. Translate each sentence to Traditional Chinese.
Keep each sentence independently mapped, but reference context for coherence.
Preserve oral filler words (I don't know, you know, sort of like, etc.), do not omit.

1. "To me, it feels like right now in the world of loops where, I don't know, maybe where"
2. "agents were a year and a half ago."
3. "So it's still fairly early, but we're starting to see signs that it's working."

→ Return format:
1. 對我來說，現在 loops 的世界大概在⋯我不確定，可能像
2. agent 一年半前的狀態。
3. 所以還蠻早期的，但我們開始看到它有效的跡象了。
```

## Step 4: Generate ASS Subtitles

**Must use `gen_ass.py`. Never hand-calculate timestamps.**

```bash
python3 gen_ass.py input.json style.json subtitles.ass
```

### input.json Format

See Step 6 "Complete input.json format" for full spec. gen_ass.py uses these fields:

- `transcript_path`: path to whisper transcription JSON
- `subtitles`: each subtitle's segment index and target language translation
- `cards`: each card's segment index and English phrase to highlight (for subtitle coloring)

### style.json Format

Default at repo root `style.json`. To override, copy and modify the `subtitle` block:

```json
{
  "subtitle": {
    "play_res_x": 1920,
    "play_res_y": 1080,
    "en_font": "Arial",
    "en_size": 60,
    "zh_font": "Noto Sans CJK TC",
    "zh_size": 50,
    "margin_lr": 100,
    "margin_v": 40,
    "highlight_color": "ff9e4a",
    "bg_color": "A0000000"
  }
}
```

Set PlayRes to **original video resolution** (not output resolution). Same for Reel, since subtitles are burned before scaling.

### What gen_ass.py Handles Automatically

- Reads exact start/end from transcript.json for each segment
- Auto-calculates offset (first segment's start time)
- Extends each line by 0.3s (capped at next line's start)
- Auto-applies highlight coloring
- Output verification (missing translations, highlight count)

### CJK Line Breaking

gen_ass.py does not break CJK lines. If PlayResX is narrow (≤ 1080), manually insert `\N` in the `zh` field of input.json. Usually unnecessary when PlayResX > 1080.

### Dialogue Format (auto-generated by gen_ass.py)

```
Dialogue: 0,{start},{end},En,,0,0,0,,{english_with_highlights}\N{\rZh}{chinese}
```

## Step 5: Generate Vocabulary Card PNGs

**Use `gen_cards.js`. Never hand-write HTML.**

```bash
node gen_cards.js input.json style.json ./cards/
```

### What gen_cards.js Handles Automatically

- Groups by `seg_index` — multiple keywords in same segment merge into one PNG
- Screenshots via Playwright (transparent background)
- Styles read from style.json (card block)
- `type: "word"/"phrase"` → card title uses `highlight`
- `type: "pattern"` → card title uses `title` (required field)

### Card Content (input.json cards field)

Each card needs:
- `highlight`: English phrase to color in subtitle (also used for ASS highlight matching)
- `zh`: Target language explanation
- `usage`: **General usage** (what context to use it in), not describing the specific source sentence
- `example`: An example sentence in a **different context** (don't use the source)
- `type`: `word` / `phrase` (use this by default) / `pattern`

### Card Timing

- Each card displays in sync with its corresponding segment
- Card display time = that segment's start ~ end
- Same-segment keywords already merged — no overlap
- Different-segment cards don't overlap (whisper segments don't overlap in time)

## Step 6: Compose Output

Two modes, based on user preference:

---

### Mode A: Landscape (Default)

**Use `compose.py` one-shot. Never hand-write ffmpeg commands.**

`compose.py` auto-runs: validate → gen_ass.py → gen_cards.js → gen_hook.js → ffmpeg composition.

```bash
# First trim the clip
ffmpeg -y -ss {start} -to {end} -i original.mp4 -c copy clip.mp4

# Compose (video_path points to trimmed clip)
python3 compose.py input.json [style.json]
```

**Note:** compose.py does not support -ss/-to trimming. Must pre-trim with ffmpeg first.

---

### Mode B: Reel (9:16 Portrait)

Use when user requests "reel" or "portrait" format.

**Use `compose_reel.py` one-shot. Never hand-write ffmpeg commands.**

`compose_reel.py` auto-runs: validate → gen_ass.py → gen_cards.js → gen_hook.js → Reel ffmpeg composition → resolution verification.

```bash
python3 compose_reel.py input.json [style.json]
```

**⚠️ `video_path` must point to the original full video (do not pre-trim).** compose_reel.py auto-calculates `-ss`/`-to` from seg_range to trim from the original. Feeding a pre-trimmed clip will cause timestamp mismatch and empty output.

**Reel Layout (handled automatically):**
```
┌──────────────────┐
│  [Hook - 648px]   │ ← y=671 (top of video area)
│                  │
│   Video (1080x608)│ ← starts at y=656
│   [Subtitles]     │ ← ASS burned before scale/pad
│                  │
├──────────────────┤
│                  │
│  [Card - 900px]   │ ← y=1320 (bottom black area)
│                  │
└──────────────────┘
```

**compose_reel.py verification:**
- validate.py checks input.json format
- gen_ass.py verifies highlight count
- Card PNG count = unique card segments count
- Output resolution = 1080x1920
- File size check (>8MB warning)

---

### Complete input.json Format

```json
{
  "transcript_path": "/tmp/whisper_out/transcript.json",
  "video_path": "/tmp/vll_output/clip.mp4",
  "output_path": "/tmp/vll_output/segment_a.mp4",
  "seg_range": [27, 38],
  "hook": { "en": "The secret to sounding natural", "zh": "聽起來自然的秘密", "accent": "sounding natural" },
  "subtitles": [
    { "seg_index": 27, "zh": "Translation here..." }
  ],
  "cards": [
    { "seg_index": 28, "highlight": "reward centers", "zh": "獎勵中心", "usage": "Usage note", "example": "Example sentence", "type": "phrase" }
  ]
}
```

- `seg_range`: [start index, end index]
- `hook.en`: Hook full text, `hook.accent`: keyword to color-highlight
- `cards[].type`: determines card title display
  - `word`: single word, card title = `highlight`
  - `phrase`: phrase/pattern, card title = `highlight` (**most common, use this by default**)
  - `pattern`: when `highlight` is too long for a title, card title = `title` (required field), `highlight` only used for subtitle color matching
  - **Recommendation: unless highlight is too long, always use `phrase`.**

### style.json

Default at repo root `style.json`, containing subtitle, card, hook, and layout parameters. To override, copy and modify then pass as argument.

### Output Resolution

| Output | CRF | Use Case |
|--------|-----|----------|
| Original | 22-24 | Local storage |
| 1080p | 24-26 | General sharing |
| 720p | 28-30 | Discord/small files |

## Step 7: Hook Title

A one-line summary at the top of each video so viewers instantly know the topic. Generated by default unless user explicitly opts out.

**Use `gen_hook.js`. Never hand-write HTML.**

```bash
node gen_hook.js input.json style.json hook.png
```

### input.json hook Field Format

```json
{
  "hook": {
    "en": "The golden question that builds instant trust",
    "zh": "一個問題讓人立刻信任你",
    "accent": "golden question"
  }
}
```

- `en`: English title
- `zh`: Target language translation
- `accent`: keyword to color-highlight (must be substring of `en`)

gen_hook.js produces a "{en} — {zh}" format PNG with accent word in blue.

## Notes

- mlx_whisper requires Apple Silicon Mac
- ffmpeg needs libass support (`brew install ffmpeg` includes it by default)
- Playwright requires Chromium (auto-downloaded after `npm install`)
- ASS subtitles use UTF-8 encoding
- After generating card PNGs, always verify dimensions with ffprobe and compare with video to determine scale ratio
