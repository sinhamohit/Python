#!/usr/bin/env python3
"""YouTube Promo Agent assistant.

Create a practical multi-platform promotion plan for a YouTube video.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, timedelta
from textwrap import fill


@dataclass
class PromoInput:
    title: str
    niche: str
    audience: str
    goal: str
    call_to_action: str
    days: int


def make_hashtags(niche: str) -> list[str]:
    cleaned = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in niche)
    words = [w for w in cleaned.lower().split() if len(w) > 2][:3]
    base = ["youtube", "creator", "contentmarketing"]
    niche_tags = [w.replace(" ", "") for w in words]
    tags = [f"#{tag}" for tag in (base + niche_tags)]
    # preserve order while removing duplicates
    return list(dict.fromkeys(tags))


def platform_task(platform: str, day: int, p: PromoInput) -> str:
    opening = {
        "x": "Post a punchy hook thread",
        "linkedin": "Share a story-based insight post",
        "instagram": "Publish a Reel + carousel teaser",
        "tiktok": "Post a short clip with a bold claim",
        "reddit": "Contribute value in a relevant subreddit",
        "facebook": "Share a conversational update in groups",
    }
    action = opening.get(platform.lower(), "Publish a platform-native post")
    return (
        f"{action} about '{p.title}'. Focus on {p.goal}. "
        f"CTA: {p.call_to_action}."
    )


def draft_post(platform: str, p: PromoInput) -> str:
    examples = {
        "x": (
            f"Most people struggle with {p.niche} because they miss one key step. "
            f"I broke it down in my new video: '{p.title}'. {p.call_to_action}"
        ),
        "linkedin": (
            f"If you're working on {p.niche}, this might save you hours. "
            f"I just published '{p.title}' for {p.audience}. "
            f"Main takeaway: consistency + systems beat hacks. {p.call_to_action}"
        ),
        "instagram": (
            f"Quick tip for {p.audience}: stop overcomplicating {p.niche}. "
            f"Full walkthrough in my latest YouTube video '{p.title}'. {p.call_to_action}"
        ),
        "tiktok": (
            f"You can get better at {p.niche} faster than you think. "
            f"I mapped out a simple framework in '{p.title}'. {p.call_to_action}"
        ),
    }
    return examples.get(
        platform.lower(),
        f"New video: '{p.title}' for {p.audience}. {p.call_to_action}",
    )


def build_plan(p: PromoInput, platforms: list[str]) -> str:
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("YOUTUBE PROMO AGENT PLAN")
    lines.append("=" * 72)
    lines.append(f"Video title     : {p.title}")
    lines.append(f"Niche           : {p.niche}")
    lines.append(f"Target audience : {p.audience}")
    lines.append(f"Primary goal    : {p.goal}")
    lines.append(f"CTA             : {p.call_to_action}")
    lines.append("")

    hashtags = " ".join(make_hashtags(p.niche))
    lines.append(f"Starter hashtags: {hashtags}")
    lines.append("")

    lines.append("7-second hook formulas:")
    lines.append("- 'If you are [audience], stop doing X and do this instead.'")
    lines.append("- 'I tested this [niche] strategy for 30 days. Here is what happened.'")
    lines.append("- 'The biggest mistake in [niche] is easier to fix than you think.'")
    lines.append("")

    lines.append("Daily action plan:")
    start = date.today()
    for day in range(1, p.days + 1):
        current = start + timedelta(days=day - 1)
        platform = platforms[(day - 1) % len(platforms)]
        lines.append(f"Day {day} ({current.isoformat()}) - {platform.title()}")
        lines.append(f"  - {platform_task(platform, day, p)}")
        lines.append("  - Engage for 20 minutes with every comment and question.")
    lines.append("")

    lines.append("Ready-to-post draft examples:")
    for platform in platforms[:4]:
        lines.append(f"[{platform.title()}]")
        lines.append(fill(draft_post(platform, p), width=72, initial_indent="  ", subsequent_indent="  "))
    lines.append("")

    lines.append("Weekly optimization checklist:")
    lines.append("- Track CTR, average view duration, and comment-to-view ratio.")
    lines.append("- Replace thumbnail/title if CTR is under your channel average.")
    lines.append("- Turn top audience questions into next week's short-form clips.")
    lines.append("- Repost best-performing short with a fresh first line.")

    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a practical YouTube promotion workflow."
    )
    parser.add_argument("--title", required=True, help="YouTube video title")
    parser.add_argument("--niche", required=True, help="Your niche or topic")
    parser.add_argument("--audience", required=True, help="Target audience")
    parser.add_argument("--goal", default="increase views", help="Promotion goal")
    parser.add_argument(
        "--cta",
        default="Watch now and tell me your biggest challenge in the comments.",
        help="Call to action",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="How many days to generate in your promotion plan",
    )
    parser.add_argument(
        "--platforms",
        default="x,linkedin,instagram,tiktok",
        help="Comma-separated platforms in rotation",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    if not platforms:
        raise SystemExit("Please pass at least one platform in --platforms.")
    if args.days < 1:
        raise SystemExit("--days must be >= 1")

    promo_input = PromoInput(
        title=args.title,
        niche=args.niche,
        audience=args.audience,
        goal=args.goal,
        call_to_action=args.cta,
        days=args.days,
    )
    print(build_plan(promo_input, platforms))


if __name__ == "__main__":
    main()
