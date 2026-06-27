import os, json

WORD_LIMIT = 400

SECTIONS = [
    ("Artificial Intelligence", "Artificial Intelligence", "🤖", "#6d28d9", "#f5f3ff", "#ede9fe"),
    ("Technology",              "Technology",              "💻", "#0369a1", "#f0f9ff", "#e0f2fe"),
    ("Business",               "Business",                "📈", "#047857", "#f0fdf4", "#dcfce7"),
]

def count_words(text: str) -> int:
    return len(text.split())

def truncate_to_words(text: str, budget: int):
    words = text.split()
    used = min(len(words), budget)
    return " ".join(words[:used]) + ("…" if used < len(words) else ""), used

def esc(text: str) -> str:
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))

    date_string = inp.get("date_string", "").strip()
    if not date_string:
        raise ValueError("'date_string' is required (e.g. 'Monday, June 9 2025').")

    stories = inp.get("stories", [])
    if not isinstance(stories, list) or len(stories) == 0:
        raise ValueError("'stories' must be a non-empty array of story objects.")

    for i, s in enumerate(stories):
        for field in ("headline", "summary", "source_name", "url", "assigned_section"):
            if not s.get(field):
                raise ValueError(f"Story at index {i} is missing required field '{field}'.")

    # --- Identify top story ---
    top_story = next((s for s in stories if s.get("top_story")), None)

    # --- Budget tracking ---
    word_budget = WORD_LIMIT
    parts = []

    # ---- HEADER (gradient wordmark) ----
    parts.append(f"""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#0f0c29;background-image:linear-gradient(135deg,#24243e 0%,#302b63 50%,#0f0c29 100%);">
  <tr>
    <td style="padding:34px 32px 30px 32px;">
      <div style="font-family:Arial,sans-serif;font-size:11px;font-weight:700;letter-spacing:4px;color:#a5b4fc;text-transform:uppercase;margin-bottom:10px;">Your Daily Digest</div>
      <div style="font-family:Georgia,'Times New Roman',serif;font-size:34px;font-weight:700;color:#ffffff;letter-spacing:-0.5px;line-height:1.05;">Morning&nbsp;Brief</div>
      <div style="font-family:Arial,sans-serif;font-size:14px;color:#c7d2fe;margin-top:8px;">{esc(date_string)}</div>
      <div style="height:4px;width:56px;background:linear-gradient(90deg,#f5c518,#fb7185);border-radius:3px;margin-top:16px;"></div>
    </td>
  </tr>
</table>
""")

    # ---- TOP STORY (hero card) ----
    if top_story:
        headline_words = count_words(top_story["headline"])
        summary_text, used = truncate_to_words(top_story["summary"], word_budget - headline_words - 5)
        word_budget -= (headline_words + used)

        parts.append(f"""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation">
  <tr>
    <td style="padding:28px 32px 4px 32px;">
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#fffdf5;border:1px solid #f3e2a8;border-radius:14px;box-shadow:0 6px 18px rgba(245,197,24,0.14);">
        <tr>
          <td style="height:5px;background:linear-gradient(90deg,#f5c518,#f59e0b);border-radius:14px 14px 0 0;line-height:5px;font-size:0;">&nbsp;</td>
        </tr>
        <tr>
          <td style="padding:22px 24px 24px 24px;">
            <span style="display:inline-block;font-family:Arial,sans-serif;font-size:10px;font-weight:700;letter-spacing:2px;color:#92660a;text-transform:uppercase;background:#fdf0c6;border-radius:20px;padding:5px 12px;margin-bottom:14px;">⭐ Top Story</span>
            <div style="font-family:Georgia,'Times New Roman',serif;font-size:23px;font-weight:700;color:#15151f;line-height:1.3;margin-bottom:12px;">{esc(top_story["headline"])}</div>
            <div style="font-family:Arial,sans-serif;font-size:15px;color:#3f3f46;line-height:1.65;margin-bottom:18px;">{esc(summary_text)}</div>
            <a href="{esc(top_story['url'])}" style="display:inline-block;font-family:Arial,sans-serif;font-size:13px;font-weight:700;color:#ffffff;background:#15151f;text-decoration:none;padding:11px 20px;border-radius:8px;">Read the full story →</a>
            <div style="font-family:Arial,sans-serif;font-size:12px;color:#a1a1aa;margin-top:14px;">{esc(top_story["source_name"])}</div>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
""")

    # ---- SECTION BLOCKS ----
    top_url = top_story["url"] if top_story else None

    for section_key, section_label, icon, accent, tint_bg, tint_border in SECTIONS:
        section_stories = [
            s for s in stories
            if s.get("assigned_section") == section_key and s.get("url") != top_url
        ]
        if not section_stories:
            continue

        rows = []
        n = 0
        for s in section_stories:
            if word_budget <= 0:
                break
            h_words = count_words(s["headline"])
            summary_text, used = truncate_to_words(s["summary"], max(0, word_budget - h_words - 3))
            word_budget -= (h_words + used)
            n += 1

            rows.append(f"""
            <tr>
              <td style="padding:0 0 14px 0;">
                <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:{tint_bg};border:1px solid {tint_border};border-radius:12px;">
                  <tr>
                    <td style="padding:16px 18px;">
                      <div style="font-family:Georgia,'Times New Roman',serif;font-size:17px;font-weight:700;line-height:1.35;margin-bottom:7px;">
                        <a href="{esc(s['url'])}" style="color:#15151f;text-decoration:none;">{esc(s['headline'])}</a>
                      </div>
                      <div style="font-family:Arial,sans-serif;font-size:14px;color:#52525b;line-height:1.6;margin-bottom:10px;">{esc(summary_text)}</div>
                      <div style="font-family:Arial,sans-serif;font-size:12px;color:{accent};">
                        <span style="font-weight:700;">{esc(s['source_name'])}</span>
                        &nbsp;·&nbsp;
                        <a href="{esc(s['url'])}" style="color:{accent};text-decoration:none;font-weight:700;">Read →</a>
                      </div>
                    </td>
                  </tr>
                </table>
              </td>
            </tr>
""")

        if not rows:
            continue

        parts.append(f"""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation">
  <tr>
    <td style="padding:22px 32px 0 32px;">
      <table cellpadding="0" cellspacing="0" role="presentation" style="margin-bottom:14px;">
        <tr>
          <td style="font-size:18px;padding-right:9px;line-height:1;">{icon}</td>
          <td style="font-family:Arial,sans-serif;font-size:13px;font-weight:700;letter-spacing:1.5px;color:{accent};text-transform:uppercase;">{esc(section_label)}</td>
        </tr>
      </table>
      <table width="100%" cellpadding="0" cellspacing="0" role="presentation">
        {"".join(rows)}
      </table>
    </td>
  </tr>
</table>
""")

    # ---- FOOTER ----
    parts.append("""
<table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="margin-top:14px;">
  <tr>
    <td style="padding:26px 32px 30px 32px;background:#0f0c29;background-image:linear-gradient(135deg,#24243e 0%,#0f0c29 100%);text-align:center;">
      <div style="font-family:Georgia,serif;font-size:16px;font-weight:700;color:#ffffff;margin-bottom:6px;">Morning Brief</div>
      <div style="font-family:Arial,sans-serif;font-size:12px;color:#9ca3cf;line-height:1.6;">
        Curated tech, AI &amp; business — every morning.
      </div>
      <div style="font-family:Arial,sans-serif;font-size:11px;color:#6b7280;margin-top:14px;">
        <a href="#" style="color:#9ca3cf;text-decoration:underline;">Unsubscribe</a>
        &nbsp;·&nbsp;
        <a href="#" style="color:#9ca3cf;text-decoration:underline;">Update preferences</a>
      </div>
    </td>
  </tr>
</table>
""")

    # ---- ASSEMBLE FULL HTML ----
    body_html = "\n".join(parts)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1.0">
  <title>Morning Brief – {esc(date_string)}</title>
</head>
<body style="margin:0;padding:0;background:#eef0f4;">
  <table width="100%" cellpadding="0" cellspacing="0" role="presentation" style="background:#eef0f4;padding:26px 0;">
    <tr>
      <td align="center">
        <table width="620" cellpadding="0" cellspacing="0" role="presentation" style="max-width:620px;width:100%;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 8px 30px rgba(15,12,41,0.12);">
          <tr><td>{body_html}</td></tr>
        </table>
        <div style="font-family:Arial,sans-serif;font-size:11px;color:#9aa0ac;margin-top:16px;">You're receiving this because you subscribed to Morning Brief.</div>
      </td>
    </tr>
  </table>
</body>
</html>"""

    subject = f"☀️ Morning Brief — {date_string}"

    result = {
        "subject": subject,
        "html": html,
        "word_count_used": WORD_LIMIT - word_budget,
    }

    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))
