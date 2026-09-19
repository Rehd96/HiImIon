---
name: extract-kitten-frames
description: Extract sharp, well-framed, and properly oriented still photos and video frames of active kittens/black cats from videos and phone photos for adoption websites and print flyers.
---

# Extract Kitten Frames & Photo Curation Skill

## Overview

Active kittens (especially 6–9 weeks old) move fast and unpredictably. Standard smartphone still photos often result in motion blur, missed facial expressions, or awkward poses. Taking short 1080p/4K video clips captures micro-expressions, play gestures, purring cuddles, and eye contact that are otherwise impossible to catch in a single shutter click.

However, extracting usable stills from kitten footage presents specific technical challenges:
1. **Black Cat Contrast & Naive Sharpness Pitfall**: Standard edge detection (Laplacian variance) favors textured backgrounds (e.g. plaid armchair cushions, rugs, wood grain) over a dark, featureless animal. An empty frame of a patterned sofa can score 3x higher than a real shot of a black kitten.
2. **Motion Blur vs Pose Sharpness**: Even at 30/60 fps, rapid paw swipes and head turns blur individual frames. Strict edge thresholds are needed to filter out blurry frames.
3. **Orientation Lag & Gyroscope Inconsistencies**: When recording starts quickly, smartphone accelerometers may record video with `rot=0` (landscape) even when held vertically, or EXIF metadata might orient portrait photos sideways in renderers (browsers, PDF generators like ReportLab/WeasyPrint).
4. **Temporal Clustering / Duplicate Rejection**: Kittens frequently pause for 1–2 seconds. Extracting at 1.5 fps can yield 5 nearly identical frames of the same pause. Frames must be clustered per scene to ensure diversity.

This skill defines the complete pipeline, heuristic scoring algorithm, orientation fixes, and folder organization for creating production-ready media.

---

## Technical Pipeline

```
[Phone Videos & Photos]
          │
          ├──> 1. EXIF Transposition on Still Photos (ImageOps.exif_transpose)
          │
          └──> 2. Frame Extraction at 1.5 fps (ffmpeg -q:v 2)
                    │
                    ▼
               3. Black Cat Heuristic Scoring
                  - Laplacian variance (sharpness > 500)
                  - Luminance & dark ratio (cat coat 8%–60%)
                  - Center 50% framing weight
                  - Exposure bounds (40 < brightness < 220)
                    │
                    ▼
               4. Temporal Deduplication (skip ±2s neighbors)
                    │
                    ▼
               5. Orientation Correction (ffprobe + PIL 90°/180° fix)
                    │
                    ▼
               6. Curated Organization (Top picks, frames, photos)
```

---

## 1. Frame Extraction Parameters

Use `ffmpeg` with constant high JPEG quality (`-q:v 2`) and a moderate sample rate (`fps=1.5`). This balances frame density (capturing fast gestures) without overwhelming disk space:

```bash
ffmpeg -y -i input_video.mp4 -vf "fps=1.5" -q:v 2 output_dir/frame_%04d.jpg
```

---

## 2. Black Kitten Heuristic Scoring Logic

To evaluate whether a frame contains a clear, well-framed black kitten:

### A. Grayscale Downsampling
Resize images to a normalized width of 640px to ensure sharpness and brightness values are comparable across resolutions (1080p, 4K, still cameras).

### B. Sharpness (Laplacian Edge Variance)
Apply `ImageFilter.FIND_EDGES` and calculate variance (`ImageStat.Stat(edges).var[0]`).
- **Reject frames** with sharpness `< 400` (blurred).
- **Ideal range**: `800 – 4000+`.

### C. Dark Subject Ratio (`dark_ratio`)
Measure pixels with luminance `< 65` (0–255 scale).
- **Valid range**: `0.08 <= dark_ratio <= 0.65`.
- Rejects empty backgrounds where no kitten is present (`< 0.08`).
- Rejects shots where the lens was blocked by hands, blankets, or extreme underexposure (`> 0.65`).

### D. Center Weighting (`center_dark`)
Crop the central 50% box of the image (`cw ± w/4`, `ch ± h/4`) and measure dark pixels:
- Kittens framed in the center score significantly higher than kittens slipping out of frame edges.

### E. Composite Score Formula
```python
composite_score = (sharpness ** 0.8) * (1.0 + 2.5 * center_dark) * (1.0 + 1.2 * dark_ratio)
```

---

## 3. Smartphone Orientation Normalization

### Still Photos (JPEG EXIF)
Modern phones write portrait orientation into EXIF tag `0x0112` (typically orientation 6 or 8). Many web browsers, PDF generators, and thumbnailers ignore this tag and render photos sideways.
**Solution**: Always run `ImageOps.exif_transpose(img)` which rotates raw pixel matrices and clears the orientation tag:

```python
from PIL import Image, ImageOps

with Image.open(photo_path) as img:
    transposed = ImageOps.exif_transpose(img)
    transposed.save(dest_path, quality=95)
```

### Video Orientation & Gyroscope Lag
Check video stream tags using `ffprobe`:
```bash
ffprobe -v error -select_streams v:0 -show_entries stream_tags=rotate:stream_side_data=rotation -of json input.mp4
```
- If `rotation: -90` or `rotation: 90`: ffmpeg automatically rotates during extraction.
- **Sensor Lag Exception**: If a video was filmed vertically but the phone sensor failed to lock portrait before recording started (`rotation: None` or `rot=0`), frames will extract sideways (e.g. 1920x1080 horizontal). These require an explicit 90° counter-clockwise rotation:
  ```python
  img = img.rotate(90, expand=True)
  ```
- **Upside-down Exception**: If filmed inverted, apply `img.rotate(180, expand=True)`.

---

## 4. Diversity & Temporal Clustering

To prevent 10 identical frames of the kitten sitting still from dominating the top picks:
1. Group scored frames by source video (`stem = base.rsplit('_', 1)[0]`).
2. Sort each video's frames by composite score descending.
3. Keep the best frame, then enforce a minimum temporal gap (e.g. index difference `>= 3` frames, equivalent to ~2 seconds at 1.5 fps) before accepting subsequent frames from the same video.
4. Limit to top 2–3 diverse frames per video clip.

---

## 5. Output Directory Standard

Organize outputs into three distinct, user-friendly tiers:

```
selezionate_per_sito_poster/
├── 01_top_scelte_sito_e_volantino/    # The ~15 best curated files, descriptive names
├── 02_tutti_i_migliori_frame_video/   # All sharp frames (~50-60) from all clips
└── 03_foto_smartphone_orientate/      # Original photos with EXIF rotation baked in
```

### Top Pick Naming Convention
Use clear Italian action/pose tags with intended target placement:
- `01_mais_in_piedi_sguardo_fiero_HERO.jpg` (Website hero / main poster focal point)
- `02_mais_seduta_polpo_verde_VOLANTINO.jpg` (A4/A5 adoption flyer featured photo)
- `03_mais_ritratto_occhi_aperti_COVER.jpg` (Ultra-high-res portrait for cover/social preview)
- `04_mais_faccia_buffa_con_polpo_FEED.jpg` (Viral/funny photo for the kitten feed)
- `05_mais_nanna_coccole_sul_grembo_BANNER.jpg` (Landscape banner showing affection)
- `09_mais_poltrona_zampe_e_artigli_macro.jpg` (Playful detail shot)

---

## 6. Reusable CLI Command

Run the bundled extraction script from the repository:

```bash
# Run on today's media folder
/home/ion/HiImIon/venv/bin/python /home/ion/HiImIon/.agents/skills/extract-kitten-frames/scripts/extract_frames.py \
    --input-dir /home/ion/Scrivania/mais_video_foto \
    --output-dir /home/ion/Scrivania/mais_video_foto/selezionate_per_sito_poster \
    --fps 1.5 \
    --date-filter 20260919
```

---

## 7. Django Integration Guidelines

### Updating the Kitten Profile Cover
```python
from kitten.models import KittenProfile
from django.core.files import File

profile = KittenProfile.objects.get(slug='mais')
with open('/home/ion/Scrivania/mais_video_foto/selezionate_per_sito_poster/01_top_scelte_sito_e_volantino/03_mais_ritratto_occhi_aperti_COVER.jpg', 'rb') as f:
    profile.cover_image.save('mais_cover.jpg', File(f), save=True)
```

### Adding New Feed Posts
```python
from kitten.models import KittenProfile, KittenPost
from django.core.files import File

profile = KittenProfile.objects.get(slug='mais')
post = KittenPost(
    kitten=profile,
    title="In piedi come una leonessa!",
    caption="Mais esplora la stanza e si mette in posa sulle quattro zampe con lo sguardo più fiero del mondo! 🐾",
    tag="scoperte"
)
with open('.../01_mais_in_piedi_sguardo_fiero_HERO.jpg', 'rb') as f:
    post.image.save('mais_in_piedi.jpg', File(f), save=True)
```
