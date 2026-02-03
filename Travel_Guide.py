import os
import json
import re
from io import BytesIO
from datetime import datetime

import streamlit as st
from openai import OpenAI
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


# ----------------------------
# Helpers
# ----------------------------
def _extract_json(text: str) -> dict:
    """
    Best-effort extraction of a JSON object from model output.
    """
    text = text.strip()

    # If it's already pure JSON
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try to find the first {...} block
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass

    raise ValueError("Could not parse JSON from the model output.")


def generate_itinerary(destination: str, days: int, interests: list[str], guardrails: str) -> dict:
    client = OpenAI()  # Uses OPENAI_API_KEY from env

    interests_text = ", ".join([i for i in interests if i]) if interests else "No specific interests"
    guardrails_text = guardrails.strip() if guardrails.strip() else "No extra guardrails"

    # Ask for STRICT JSON so it’s easy to render + PDF
    prompt = f"""
You are a travel planner. Create a realistic, family-friendly travel itinerary.

Return ONLY valid JSON (no markdown, no extra text) that matches this schema:
{{
  "trip_title": string,
  "destination": string,
  "days": number,
  "assumptions": [string, ...],
  "daily_plan": [
    {{
      "day": number,
      "theme": string,
      "morning": [string, ...],
      "afternoon": [string, ...],
      "evening": [string, ...],
      "notes": [string, ...]
    }},
    ...
  ],
  "tips": [string, ...]
}}

User Inputs:
- Destination: {destination}
- Number of days: {days}
- Special interests: {interests_text}
- Guardrails (MUST follow): {guardrails_text}

Rules:
- Respect guardrails strictly (e.g., if "no walking tours", avoid those; if "wheelchair accessible only", ensure accessibility).
- Keep daily activities practical (don’t overpack), include meal ideas aligned to interests.
- Include at least 2 assumptions to reduce ambiguity.
"""

    # Pick a current text-capable model you have access to
    resp = client.responses.create(
        model="gpt-5.2",
        input=prompt,
    )

    data = _extract_json(resp.output_text)

    # Minimal validation
    if "daily_plan" not in data or not isinstance(data["daily_plan"], list):
        raise ValueError("Model response missing 'daily_plan'.")

    return data


def itinerary_to_markdown(itin: dict) -> str:
    lines = []
    lines.append(f"# {itin.get('trip_title', 'Travel Plan')}")
    lines.append(f"**Destination:** {itin.get('destination', '')}")
    lines.append(f"**Days:** {itin.get('days', '')}")
    lines.append("")
    lines.append("## Assumptions")
    for a in itin.get("assumptions", []):
        lines.append(f"- {a}")
    lines.append("")
    lines.append("## Day-by-day Plan")

    for day in itin.get("daily_plan", []):
        lines.append(f"### Day {day.get('day', '')}: {day.get('theme', '')}")
        lines.append("**Morning**")
        for x in day.get("morning", []):
            lines.append(f"- {x}")
        lines.append("**Afternoon**")
        for x in day.get("afternoon", []):
            lines.append(f"- {x}")
        lines.append("**Evening**")
        for x in day.get("evening", []):
            lines.append(f"- {x}")
        notes = day.get("notes", [])
        if notes:
            lines.append("**Notes**")
            for n in notes:
                lines.append(f"- {n}")
        lines.append("")

    lines.append("## Tips")
    for t in itin.get("tips", []):
        lines.append(f"- {t}")

    return "\n".join(lines)


def build_pdf_bytes(itin: dict) -> bytes:
    """
    Simple PDF generator (ReportLab).
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left = 0.8 * inch
    top = height - 0.8 * inch
    y = top

    def write_line(text: str, font="Helvetica", size=10, leading=14):
        nonlocal y
        c.setFont(font, size)

        # wrap naively by splitting long lines
        max_chars = 95
        chunks = [text[i : i + max_chars] for i in range(0, len(text), max_chars)] or [""]
        for chunk in chunks:
            if y < 0.8 * inch:
                c.showPage()
                y = top
                c.setFont(font, size)
            c.drawString(left, y, chunk)
            y -= leading

    # Title
    write_line(itin.get("trip_title", "Travel Plan"), font="Helvetica-Bold", size=16, leading=20)
    write_line(f"Destination: {itin.get('destination', '')}", font="Helvetica", size=11)
    write_line(f"Days: {itin.get('days', '')}", font="Helvetica", size=11)
    write_line(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", font="Helvetica-Oblique", size=9)
    write_line("")

    # Assumptions
    write_line("Assumptions", font="Helvetica-Bold", size=12, leading=18)
    for a in itin.get("assumptions", []):
        write_line(f"• {a}")
    write_line("")

    # Daily plan
    write_line("Day-by-day Plan", font="Helvetica-Bold", size=12, leading=18)
    for day in itin.get("daily_plan", []):
        write_line(f"Day {day.get('day', '')}: {day.get('theme', '')}", font="Helvetica-Bold", size=11, leading=16)

        write_line("  Morning:", font="Helvetica-Bold", size=10)
        for x in day.get("morning", []):
            write_line(f"   - {x}")

        write_line("  Afternoon:", font="Helvetica-Bold", size=10)
        for x in day.get("afternoon", []):
            write_line(f"   - {x}")

        write_line("  Evening:", font="Helvetica-Bold", size=10)
        for x in day.get("evening", []):
            write_line(f"   - {x}")

        notes = day.get("notes", [])
        if notes:
            write_line("  Notes:", font="Helvetica-Bold", size=10)
            for n in notes:
                write_line(f"   - {n}")

        write_line("")

    # Tips
    tips = itin.get("tips", [])
    if tips:
        write_line("Tips", font="Helvetica-Bold", size=12, leading=18)
        for t in tips:
            write_line(f"• {t}")

    c.save()
    return buffer.getvalue()


# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Travel Guide", page_icon="🧳", layout="centered")
st.title("🧳 Travel Guide")

if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

with st.form("travel_form"):
    destination = st.text_input("Destination to Travel", placeholder="e.g., Chicago, IL")
    days = st.number_input("Number of Days", min_value=1, max_value=30, value=3, step=1)

    interests = st.multiselect(
        "Special Interests",
        options=["Museums", "Food & Cuisine", "Historic sites", "Nightlife", "Nature", "Shopping", "Kids activities", "Beaches", "Adventure"],
        default=["Food & Cuisine", "Museums"],
    )

    guardrails = st.text_area(
        "Guardrails (must follow)",
        placeholder="e.g., No walking tours. Only kids-friendly activities. Only wheelchair accessible places.",
        height=90,
    )

    col1, col2 = st.columns(2)
    with col1:
        generate = st.form_submit_button("Generate Plan ✅")
    with col2:
        reset = st.form_submit_button("Reset Form 🔄")

if reset:
    st.session_state.itinerary = None
    st.rerun()

if generate:
    if not destination.strip():
        st.error("Please enter a destination.")
    else:
        with st.spinner("Generating your travel plan..."):
            try:
                itin = generate_itinerary(destination.strip(), int(days), interests, guardrails)
                st.session_state.itinerary = itin
            except Exception as e:
                st.error(f"Failed to generate itinerary: {e}")

itin = st.session_state.itinerary
if itin:
    st.success("Travel plan generated!")
    md = itinerary_to_markdown(itin)
    st.markdown(md)

    pdf_bytes = build_pdf_bytes(itin)
    filename = f"Travel_Plan_{itin.get('destination','Trip').replace(' ', '_')}.pdf"
    st.download_button(
        label="Download PDF 📄",
        data=pdf_bytes,
        file_name=filename,
        mime="application/pdf",
    )

