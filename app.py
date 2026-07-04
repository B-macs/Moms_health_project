"""
Daily/Weekly Athlete Check-In
A simple mobile-friendly Streamlit form that records a 5-question wellness
check-in to a Google Sheet, one row per submission.
"""

import logging
import traceback
from datetime import datetime

import gspread
import streamlit as st
from google.oauth2.service_account import Credentials
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

TIMEZONE = ZoneInfo("Europe/Berlin")

SHEET_HEADER = [
    "timestamp",
    "movement_energy",
    "muscle_recovery",
    "joint_comfort",
    "digestive_capacity",
    "perceived_effort",
    "notes",
]

# Each question: a key (matches the sheet column), the prompt text, and the
# 1-5 label descriptions shown to the user.
QUESTIONS = [
    {
        "key": "movement_energy",
        "title": "1. Daily Movement Energy",
        "question": "How did your physical stamina hold up through the afternoon and evenings this week?",
        "labels": {
            1: "Drastic evening crash; felt completely wiped out after basic tasks.",
            2: "Noticeable slump; had to force myself to stay active later in the day.",
            3: "Normal energy; felt a little tired by bed, but nothing unusual.",
            4: "Strong stamina; easily transitioned from morning sports to evening activities.",
            5: "Peak vitality; vibrant, high energy sustained right up until sleep.",
        },
    },
    {
        "key": "muscle_recovery",
        "title": "2. Muscle Recovery & Soreness",
        "question": "How quickly did your muscles bounce back and feel ready after high-intensity training or tennis matches?",
        "labels": {
            1: "Prolonged, deep muscle soreness that lasted for days or hindered movement.",
            2: "Slower recovery than usual; heavy legs and stiffness during daily walks.",
            3: "Standard recovery; typical minor tightness that cleared within 24 hours.",
            4: "Fast recovery; minimal stiffness, ready for subsequent physical activity.",
            5: "Rapid rebound; felt fully refreshed and unbothered by previous exertion.",
        },
    },
    {
        "key": "joint_comfort",
        "title": "3. Joint and Court Comfort",
        "question": "How did your back, knees, and joints feel during high-impact court movements, sudden stops, or structural twists this week?",
        "labels": {
            1: "Significant structural aching or deep discomfort that forced me to hold back.",
            2: "Mild, persistent nagging aches that felt vulnerable during dynamic moves.",
            3: "Baseline minor stiffness that reliably warmed up and disappeared during play.",
            4: "Clean, fluid movement; zero pain or distraction during sport.",
            5: "Exceptionally loose and resilient; joints felt completely shock-absorbent.",
        },
    },
    {
        "key": "digestive_capacity",
        "title": "4. Digestive Fuel Capacity",
        "question": "How comfortable and efficient did your digestion feel after your main meals this week?",
        "labels": {
            1: "Intense fullness or immediate bloating; felt like food sat heavy for hours.",
            2: "Filled up way too fast; struggled to finish normal, healthy portions.",
            3: "Standard digestion; occasional light fullness, but easily processed.",
            4: "Efficient digestion; processed food cleanly with steady post-meal energy.",
            5: "Perfect assimilation; ready for regular fuel cycles with absolutely zero discomfort.",
        },
    },
    {
        "key": "perceived_effort",
        "title": "5. Perceived Training Effort (RPE)",
        "question": "How hard did your training and tennis feel this week?",
        "labels": {
            1: "Effortless; everything felt light and easy, well within my limits.",
            2: "Comfortable; a normal workload that never felt taxing.",
            3: "Moderate; solid effort, appropriately challenging but manageable.",
            4: "Hard; sessions felt heavy and took real willpower to complete.",
            5: "Brutal; even familiar workouts felt exhausting or beyond my capacity.",
        },
    },
]

DEFAULT_RATING = 3

# --------------------------------------------------------------------------
# Google Sheets connection
# --------------------------------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


@st.cache_resource(show_spinner=False)
def get_worksheet():
    """Authenticate with Google and return the first worksheet, creating the
    header row if the sheet is empty. Cached so we only auth/open once per
    server process, not on every rerun."""
    creds_info = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(creds_info, scopes=SCOPES)
    client = gspread.authorize(credentials)

    sheet_id = st.secrets["sheet"]["sheet_id"]
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.sheet1

    first_row = worksheet.row_values(1)
    if first_row != SHEET_HEADER:
        worksheet.insert_row(SHEET_HEADER, index=1)

    return worksheet


def append_checkin(answers: dict, notes: str) -> None:
    """Append one check-in as a new row: timestamp, then the 5 ratings, then notes."""
    worksheet = get_worksheet()
    timestamp = datetime.now(TIMEZONE).isoformat()
    row = [timestamp] + [answers[q["key"]] for q in QUESTIONS] + [notes]
    worksheet.append_row(row, value_input_option="USER_ENTERED")


# --------------------------------------------------------------------------
# UI
# --------------------------------------------------------------------------

st.set_page_config(page_title="Weekly Check-In", page_icon="🎾", layout="centered")

st.title("Weekly Check-In 🎾")
st.caption("Answer all 5 questions, add a note if you like, then hit Submit.")

with st.form("checkin_form", clear_on_submit=True):
    answers = {}

    for q in QUESTIONS:
        st.subheader(q["title"])
        st.write(q["question"])

        rating = st.select_slider(
            label="Your rating",
            options=[1, 2, 3, 4, 5],
            value=DEFAULT_RATING,
            key=q["key"],
            label_visibility="collapsed",
        )
        for n, text in q["labels"].items():
            if n == rating:
                st.caption(f"**{n} - {text}**")
            else:
                st.caption(f"{n} - {text}")
        answers[q["key"]] = rating

        st.divider()

    notes = st.text_area(
        "Notes (optional)",
        placeholder="Anything else you want to mention...",
        height=100,
    )

    submitted = st.form_submit_button("Submit", use_container_width=True)

if submitted:
    if len(answers) != len(QUESTIONS) or any(
        answers.get(q["key"]) is None for q in QUESTIONS
    ):
        st.error("Please answer all 5 questions before submitting.")
    else:
        try:
            append_checkin(answers, notes.strip())
        except Exception:
            logger.error("Failed to save check-in:\n%s", traceback.format_exc())
            st.error(
                "⚠️ Sorry, something went wrong saving your check-in. "
                "Please try again in a moment, or let your son know."
            )
        else:
            st.success("✅ Saved — thank you!")
            st.balloons()
