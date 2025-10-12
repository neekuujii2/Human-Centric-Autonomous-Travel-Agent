# pages/travel_guides_page.py
import streamlit as st
from datetime import datetime

from agents.youtube_travel_agent import (
    get_destination_video_data,
    answer_question_about_captions,
    DEFAULT_LANGS,
)

def render():
    # Custom CSS for better UI
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .search-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }
    .video-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .filter-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin: 1rem 0;
    }
    .pill {
        background: #e9ecef;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        border: 1px solid #dee2e6;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stat-item {
        text-align: center;
    }
    .caption-status {
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .caption-yes {
        background: #d4edda;
        color: #155724;
    }
    .caption-no {
        background: #f8d7da;
        color: #721c24;
    }
    </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌟 AI-Powered Travel Guides</h1>
        <p style="font-size: 1.2rem; margin: 0;">Discover amazing destinations through AI-powered video analysis</p>
        <p style="font-size: 1rem; opacity: 0.9; margin: 0.5rem 0 0 0;">Search → Watch → Get AI Insights → Ask Questions</p>
    </div>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'video_data' not in st.session_state:
        st.session_state.video_data = []
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False
    if 'current_destination' not in st.session_state:
        st.session_state.current_destination = ""

    # Search Section
    st.markdown('<div class="search-container">', unsafe_allow_html=True)
    
    # Main search input
    col1, col2 = st.columns([3, 1])
    with col1:
        destination = st.text_input(
            "Destination", 
            placeholder="🔍 Enter your dream destination (e.g., Paris, Tokyo, Bali, New York)",
            key="destination_input",
            label_visibility="collapsed"
        )
    
    with col2:
        search_clicked = st.button("🚀 Explore", use_container_width=True, type="primary")

    # Advanced options in expandable section
    with st.expander("⚙️ Advanced Search Options", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**🎯 Search Preferences**")
            max_results = st.slider("Number of videos", 1, 10, 6)
            order = st.selectbox(
                "Sort by",
                options=["relevance", "date", "viewCount", "rating"],
                index=0,
                format_func=lambda x: {
                    "relevance": "🎯 Most Relevant",
                    "date": "📅 Latest",
                    "viewCount": "👁️ Most Viewed", 
                    "rating": "⭐ Highest Rated"
                }[x]
            )
        
        with col2:
            st.markdown("**⏱️ Video Length**")
            duration = st.selectbox(
                "Duration",
                options=["any", "short", "medium", "long"],
                index=0,
                format_func=lambda x: {
                    "any": "🎬 Any Length",
                    "short": "⚡ Short (< 4 min)",
                    "medium": "⏰ Medium (4-20 min)",
                    "long": "🎞️ Long (> 20 min)"
                }[x]
            )
            
            use_date_filter = st.checkbox("📅 Recent videos only", value=False)
            published_after = None
            if use_date_filter:
                months_back = st.selectbox("Published in last", [1, 3, 6, 12], index=1, format_func=lambda x: f"{x} month{'s' if x > 1 else ''}")
                from datetime import datetime, timedelta
                dt = datetime.now() - timedelta(days=30*months_back)
                published_after = f"{dt.date().isoformat()}T00:00:00Z"
        
        with col3:
            st.markdown("**🌐 Language Preferences**")
            lang_preference = st.selectbox(
                "Primary language",
                ["English", "Hindi", "Spanish", "French", "German", "Japanese", "Mixed"],
                index=0
            )
            
            lang_map = {
                "English": ["en", "en-US", "en-GB"],
                "Hindi": ["hi", "hi-IN", "en"],
                "Spanish": ["es", "es-ES", "en"],
                "French": ["fr", "fr-FR", "en"],
                "German": ["de", "de-DE", "en"], 
                "Japanese": ["ja", "ja-JP", "en"],
                "Mixed": DEFAULT_LANGS
            }
            lang_candidates = lang_map.get(lang_preference, DEFAULT_LANGS)
            
            channel_id = st.text_input("🎬 Specific Channel ID (optional)", placeholder="UC...")

    st.markdown('</div>', unsafe_allow_html=True)

    # Search execution
    if search_clicked:
        if not destination.strip():
            st.error("🚨 Please enter a destination to explore!")
            return

        # Show search progress
        with st.spinner("🔍 Finding the best travel videos for you..."):
            progress_bar = st.progress(0)
            progress_bar.progress(25, text="Searching YouTube...")
            
            data_list = get_destination_video_data(
                destination=destination,
                max_results=max_results,
                order=order,
                duration=duration,
                channel_id=channel_id or None,
                published_after=published_after,
                lang_candidates=lang_candidates,
                prefer_with_captions=True,
            )
            
            progress_bar.progress(75, text="Analyzing videos...")
            
            # Store in session state
            st.session_state.video_data = data_list
            st.session_state.search_performed = True
            st.session_state.current_destination = destination
            
            progress_bar.progress(100, text="Ready!")
            progress_bar.empty()

        if not data_list:
            st.warning("🤷‍♂️ No videos found. Try a different destination or adjust your filters!")
            st.session_state.search_performed = False
            return

    # Display results
    if st.session_state.search_performed and st.session_state.video_data:
        data_list = st.session_state.video_data
        
        # Results header with stats
        st.markdown(f"## 🎯 Results for: **{st.session_state.current_destination}**")
        
        # Statistics
        videos_with_captions = sum(1 for d in data_list if d.get("has_captions", False))
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🎬 Total Videos", len(data_list))
        with col2:
            st.metric("📝 With Transcripts", videos_with_captions)
        with col3:
            st.metric("❓ Q&A Ready", videos_with_captions)
        with col4:
            if st.button("🔄 New Search", use_container_width=True):
                st.session_state.video_data = []
                st.session_state.search_performed = False
                st.session_state.current_destination = ""
                for key in list(st.session_state.keys()):
                    if key.startswith("answer_"):
                        del st.session_state[key]
                st.rerun()

        st.markdown("---")

        # Display videos
        for i, data in enumerate(data_list, start=1):
            v = data["video"]
            has_captions = data.get("has_captions", False)
            
            # Video card
            st.markdown(f'<div class="video-card">', unsafe_allow_html=True)
            
            # Video header
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"### {i}. {v['title']}")
                st.markdown(f"**📺 {v['channel_title']}** • {v.get('published_at', '').split('T')[0]}")
            
            with col2:
                if has_captions:
                    st.markdown('<span class="caption-status caption-yes">✅ Transcript Available</span>', unsafe_allow_html=True)
                else:
                    st.markdown('<span class="caption-status caption-no">❌ No Transcript</span>', unsafe_allow_html=True)

            # Thumbnail and video
            if v.get("thumbnail"):
                st.image(v["thumbnail"], use_column_width=True)
            
            # Video embed in expandable section
            with st.expander("▶️ Watch Video", expanded=False):
                st.video(f"https://www.youtube.com/watch?v={v['video_id']}")

            # Two column layout for summary and Q&A
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown("#### 📋 AI Summary")
                if has_captions:
                    with st.container():
                        st.markdown(f"<div style='background: #f8f9fa; padding: 1rem; border-radius: 8px; border-left: 3px solid #28a745;'>{data['summary']}</div>", unsafe_allow_html=True)
                else:
                    st.error("⚠️ No transcript available - Cannot generate summary")
                    st.info("💡 **Tip**: Look for videos with CC (closed captions) for better analysis")

            with col2:
                st.markdown("#### ❓ Ask Questions")
                if has_captions:
                    q = st.text_input(
                        "Question Input:",
                        key=f"q_{v['video_id']}",
                        placeholder="e.g., Best time to visit? Budget tips? Must-see places?",
                        label_visibility="collapsed"
                    )
                    
                    answer_key = f"answer_{v['video_id']}"
                    
                    if st.button(f"🤔 Get Answer", key=f"ask_{v['video_id']}", use_container_width=True):
                        if not q.strip():
                            st.warning("Please type a question first!")
                        else:
                            with st.spinner("🧠 AI is analyzing the video..."):
                                answer = answer_question_about_captions(data["captions"], q)
                            st.session_state[answer_key] = answer
                    
                    # Display answer
                    if answer_key in st.session_state:
                        st.success("**Answer:**")
                        st.markdown(f"<div style='background: #d4edda; padding: 1rem; border-radius: 8px; border-left: 3px solid #155724;'>{st.session_state[answer_key]}</div>", unsafe_allow_html=True)
                else:
                    st.error("🚫 Questions not available")
                    st.markdown("**Why?** This video doesn't have captions/subtitles")
                    st.markdown("**Try:** Look for videos with auto-generated or manual subtitles")

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")

    # Footer
    if not st.session_state.search_performed:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #6c757d;">
            <h3>🌍 Ready to explore the world?</h3>
            <p>Enter any destination above and discover it through AI-powered video insights!</p>
            <div style="display: flex; justify-content: center; gap: 20px; margin-top: 1rem;">
                <span>🎥 Smart Video Search</span>
                <span>📝 AI Summaries</span>
                <span>🤖 Interactive Q&A</span>
                <span>🌐 Multi-language Support</span>
            </div>
        </div>
        """, unsafe_allow_html=True)