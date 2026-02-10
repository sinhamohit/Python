## YouTube Promo Agent Helper

This repository now includes a lightweight Python CLI that generates a practical, repeatable promotion plan for a YouTube video.

### What it does

- Builds a day-by-day promotion workflow.
- Rotates across social platforms you choose.
- Generates starter post drafts and hashtag ideas.
- Includes optimization reminders so you can improve performance weekly.

### Usage

```bash
python3 youtube_promo_agent.py \
  --title "How I Edit Videos 3x Faster" \
  --niche "video editing" \
  --audience "new YouTube creators" \
  --goal "get more qualified subscribers" \
  --cta "Watch now and comment your editing bottleneck" \
  --days 7 \
  --platforms x,linkedin,instagram,tiktok
```

You can shorten the campaign or change platforms:

```bash
python3 youtube_promo_agent.py \
  --title "My Thumbnail Framework" \
  --niche "youtube thumbnails" \
  --audience "small channel owners" \
  --days 3 \
  --platforms reddit,x
```

### Why this can help you as an agent

If you're acting as a promotion assistant, this tool gives you:

- A structured output you can execute daily.
- Reusable copy starting points for multiple platforms.
- A repeatable checklist for optimization, instead of guessing.
