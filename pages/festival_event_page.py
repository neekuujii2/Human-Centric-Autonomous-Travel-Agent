# pages/event_page.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
from typing import List, Dict

st.set_page_config(page_title="Events Finder", page_icon="🎭", layout="wide")

# ---------------------------
# Scraper Function (No API needed)
# ---------------------------
def scrape_bookmyshow(city: str, category: str) -> List[Dict]:
    url = f"https://in.bookmyshow.com/explore/{category}-{city}"
    events = []

    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if res.status_code != 200:
            return []

        soup = BeautifulSoup(res.text, "html.parser")

        # Event containers
        event_cards = soup.find_all("div", class_="card-container wow fadeIn")
        for card in event_cards:
            title_tag = card.find("div", class_="card-title")
            img_tag = card.find("img")
            link_tag = card.find("a", href=True)

            if not title_tag or not img_tag or not link_tag:
                continue

            events.append({
                "name": title_tag.text.strip(),
                "image": img_tag["src"],
                "url": "https://in.bookmyshow.com" + link_tag["href"],
                "category": category.capitalize()
            })

    except Exception as e:
        st.error(f"Error scraping: {e}")
        return []

    return events

# ---------------------------
# Streamlit UI
# ---------------------------
st.title("🎭 Events & Entertainment Finder (BookMyShow)")

col1, col2 = st.columns(2)
with col1:
    city = st.text_input("Enter your city", "delhi").lower().strip()
with col2:
    category = st.selectbox(
        "Choose category",
        ["movies", "events", "plays", "sports"]
    )

if st.button("🔍 Search Events"):
    data = scrape_bookmyshow(city, category)
    if not data:
        st.warning("No events found for this city & category.")
    else:
        for ev in data:
            with st.container():
                st.image(ev["image"], width=250)
                st.markdown(f"### {ev['name']}")
                st.markdown(f"[🎟️ Book Now]({ev['url']})")
                st.markdown(f"*Category: {ev['category']}*")
                st.markdown("---")
