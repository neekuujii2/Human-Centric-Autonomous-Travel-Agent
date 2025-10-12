# travel_agent.py - Main file (Clean & Simple)

import streamlit as st
from datetime import date
import datetime
from dotenv import load_dotenv
import os

# Import separate page modules
from pages import flight_search_page, main_travel_page, hotels_page, travel_news_page, youtube_guides_page


# Load environment variables
load_dotenv()

# Streamlit page settings
st.set_page_config(page_title="AI Travel Planner", layout="wide", page_icon="✈️")

# Initialize session state for page navigation
if "current_page" not in st.session_state:
    st.session_state.current_page = "main"

def main():
    """Main function to route between pages"""
    
    # Navigation in sidebar (optional)
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        
        # Navigation buttons
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.current_page = "main"
            st.rerun()
            
        if st.button("✈️ Flight Search", use_container_width=True):
            st.session_state.current_page = "flight_search"
            st.rerun()

        if st.button("🏨 Hotels & Cuisines", use_container_width=True):
            st.session_state.current_page = "hotels"
            st.rerun()
        
        if st.button("📰 Travel News & Blogs", use_container_width=True):  # ✅ New button
            st.session_state.current_page = "travel_news"
            st.rerun()

        if st.button("📺 Travel Guides", use_container_width=True):
            st.session_state.current_page = "travel_guides"
            st.rerun()    
        
        st.markdown("---")
        st.markdown("### 🔑 Current Page")
        if st.session_state.current_page == "main":
            st.success("📋 Travel Planner")
        elif st.session_state.current_page == "flight_search":
            st.info("✈️ Flight Search")
        elif st.session_state.current_page == "hotels":
            st.info("🏨 Hotels & Cuisines")
        elif st.session_state.current_page == "travel_news":  # ✅ New state display
            st.info("📰 Travel News & Blogs")
        elif st.session_state.current_page == "travel_guides":
            st.info("📺 Travel Guides")

    
    # Route to appropriate page
    if st.session_state.current_page == "flight_search":
        flight_search_page.render()
    elif st.session_state.current_page == "hotels":
        hotels_page.render()
    elif st.session_state.current_page == "travel_news":  # ✅ Route to new page   
        travel_news_page.render()
    elif st.session_state.current_page == "travel_guides":
        youtube_guides_page.render()    
    else:
        main_travel_page.render()

if __name__ == "__main__":
    main()
