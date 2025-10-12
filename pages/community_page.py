import streamlit as st
import os
import json
from PIL import Image
import requests
from datetime import datetime
import hashlib
from agents.community_database import CommunityDatabase

class CommunityApp:
    def __init__(self):
        self.db = CommunityDatabase()
        self.init_session_state()
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'logged_in' not in st.session_state:
            st.session_state.logged_in = False
        if 'user_data' not in st.session_state:
            st.session_state.user_data = None
        if 'current_view' not in st.session_state:
            st.session_state.current_view = 'feed'
    
    def run_community_section(self):
        """Main community section entry point"""
        st.title("📸 Travel Community")
        
        # Authentication check
        if not st.session_state.logged_in:
            self.show_auth_section()
            return
        
        # Navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🏠 Feed", "📤 Create Post", "👤 Profile", "🔥 Trending"])
        
        with tab1:
            self.show_feed()
        
        with tab2:
            self.show_create_post()
        
        with tab3:
            self.show_profile()
        
        with tab4:
            self.show_trending()
    
    def show_auth_section(self):
        """Show login/register interface"""
        auth_tab1, auth_tab2 = st.tabs(["Login", "Register"])
        
        with auth_tab1:
            self.show_login()
        
        with auth_tab2:
            self.show_register()
    
    def show_login(self):
        """Login form"""
        st.subheader("Welcome Back! 👋")
        
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                user = self.db.authenticate_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")
    
    def show_register(self):
        """Registration form"""
        st.subheader("Join the Community! 🌟")
        
        with st.form("register_form"):
            username = st.text_input("Choose a Username")
            email = st.text_input("Email Address")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            bio = st.text_area("Tell us about yourself (optional)", max_chars=200)
            register_btn = st.form_submit_button("Create Account")
            
            if register_btn:
                if password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                elif len(username) < 3:
                    st.error("Username must be at least 3 characters")
                else:
                    user_id = self.db.create_user(username, email, password, bio)
                    if user_id:
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Username or email already exists")
    
    def show_feed(self):
        """Main feed display"""
        st.subheader("Latest Travel Posts 📸")
        
        # Filter options
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            location_filter = st.selectbox("Filter by Location", ["All Locations"] + self.get_popular_locations())
        with col2:
            if st.button("🔄 Refresh"):
                st.rerun()
        with col3:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.user_data = None
                st.rerun()
        
        # Load and display posts
        posts = self.db.get_feed_posts(limit=10)
        
        if not posts:
            st.info("No posts yet! Be the first to share your travel memories! 🌍")
            return
        
        for post in posts:
            self.display_post_card(post)
            st.divider()
    
    def display_post_card(self, post):
        """Display a single post card"""
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Display image
            if os.path.exists(post['image_url']):
                st.image(post['image_url'], width=200)
            else:
                st.image("https://via.placeholder.com/200x200?text=Image+Not+Found", width=200)
        
        with col2:
            # Post header
            st.markdown(f"**@{post['username']}** • {self.format_timestamp(post['created_at'])}")
            
            # Location
            if post['location_name']:
                st.markdown(f"📍 {post['location_name']}")
            
            # Caption
            st.markdown(post['caption'])
            
            # Hashtags
            if post['hashtags']:
                hashtag_str = " ".join([f"#{tag}" for tag in post['hashtags']])
                st.markdown(f"*{hashtag_str}*")
            
            # Engagement buttons
            col_like, col_comment, col_stats = st.columns([1, 1, 2])
            
            with col_like:
                if st.button(f"❤️ Like", key=f"like_{post['id']}"):
                    self.db.like_post(post['id'], st.session_state.user_data['id'])
                    st.rerun()
            
            with col_comment:
                if st.button(f"💬 Comment", key=f"comment_btn_{post['id']}"):
                    st.session_state[f"show_comments_{post['id']}"] = True
            
            with col_stats:
                st.markdown(f"❤️ {post['like_count']} • 💬 {post['comment_count']}")
            
            # Comment section
            if st.session_state.get(f"show_comments_{post['id']}", False):
                self.show_comments_section(post['id'])
    
    def show_comments_section(self, post_id):
        """Display comments for a post"""
        st.markdown("**Comments:**")
        
        # Add comment form
        with st.form(f"comment_form_{post_id}"):
            comment_text = st.text_input("Add a comment...")
            submit_comment = st.form_submit_button("Post Comment")
            
            if submit_comment and comment_text:
                self.db.add_comment(post_id, st.session_state.user_data['id'], comment_text)
                st.success("Comment added!")
                st.rerun()
        
        # Display existing comments
        comments = self.db.get_post_comments(post_id)
        for comment in comments[:5]:  # Show only first 5 comments
            st.markdown(f"**@{comment['username']}**: {comment['comment']}")
            st.caption(self.format_timestamp(comment['created_at']))
    
    def show_create_post(self):
        """Post creation interface"""
        st.subheader("Share Your Travel Memory 📷")
        
        with st.form("create_post_form"):
            # Image upload
            uploaded_file = st.file_uploader("Choose a photo", type=['png', 'jpg', 'jpeg'])
            
            # Caption
            caption = st.text_area("Write a caption...", max_chars=500)
            
            # Hashtags
            hashtags_input = st.text_input("Hashtags (separated by spaces)", placeholder="#travel #adventure #wanderlust")
            
            # Location
            location_name = st.text_input("Location (optional)", placeholder="Paris, France")
            
            # Location coordinates (optional)
            col1, col2 = st.columns(2)
            with col1:
                lat = st.number_input("Latitude (optional)", value=None, format="%.6f")
            with col2:
                lon = st.number_input("Longitude (optional)", value=None, format="%.6f")
            
            submit_post = st.form_submit_button("Share Post 🚀")
            
            if submit_post:
                if uploaded_file is None:
                    st.error("Please upload an image!")
                elif not caption.strip():
                    st.error("Please add a caption!")
                else:
                    # Save uploaded image
                    image_path = self.save_uploaded_image(uploaded_file)
                    
                    # Process hashtags
                    hashtags = [tag.strip('#').strip() for tag in hashtags_input.split() if tag.strip()]
                    
                    # Create post
                    post_id = self.db.create_post(
                        user_id=st.session_state.user_data['id'],
                        image_url=image_path,
                        caption=caption,
                        hashtags=hashtags,
                        location_name=location_name if location_name else None,
                        lat=lat,
                        lon=lon
                    )
                    
                    if post_id:
                        st.success("Post shared successfully! 🎉")
                        st.balloons()
                    else:
                        st.error("Failed to create post. Please try again.")
    
    def show_profile(self):
        """User profile section"""
        username = st.session_state.user_data['username']
        st.subheader(f"@{username}'s Profile")
        
        profile = self.db.get_user_profile(username)
        if profile:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Profile picture placeholder
                if profile['profile_pic']:
                    st.image(profile['profile_pic'], width=150)
                else:
                    st.image("https://via.placeholder.com/150x150?text=👤", width=150)
            
            with col2:
                st.markdown(f"**Username:** {profile['username']}")
                st.markdown(f"**Posts:** {profile['post_count']}")
                st.markdown(f"**Member since:** {self.format_timestamp(profile['created_at'])}")
                
                if profile['bio']:
                    st.markdown(f"**Bio:** {profile['bio']}")
        
        # User's posts
        st.subheader("Your Posts")
        # Here you would fetch and display user's posts
        st.info("Your posts will appear here (implement user-specific post fetching)")
    
    def show_trending(self):
        """Trending section"""
        st.subheader("🔥 What's Trending")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Trending Hashtags")
            trending_hashtags = self.db.get_trending_hashtags(10)
            
            if trending_hashtags:
                for i, hashtag in enumerate(trending_hashtags, 1):
                    st.markdown(f"{i}. **#{hashtag['hashtag']}** ({hashtag['count']} posts)")
            else:
                st.info("No trending hashtags yet!")
        
        with col2:
            st.markdown("### 🌍 Popular Destinations")
            popular_locations = self.get_popular_locations()
            
            for i, location in enumerate(popular_locations[:10], 1):
                st.markdown(f"{i}. {location}")
    
    def save_uploaded_image(self, uploaded_file):
        """Save uploaded image to local storage"""
        # Create images directory if it doesn't exist
        images_dir = "community_images"
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(uploaded_file.getvalue()).hexdigest()[:8]
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"{timestamp}_{file_hash}.{file_extension}"
        
        file_path = os.path.join(images_dir, filename)
        
        # Save image
        image = Image.open(uploaded_file)
        # Resize image if too large
        if image.width > 800 or image.height > 800:
            image.thumbnail((800, 800), Image.Resampling.LANCZOS)
        
        image.save(file_path, optimize=True, quality=85)
        return file_path
    
    def get_popular_locations(self):
        """Get list of popular travel locations (placeholder)"""
        return [
            "Paris, France", "Tokyo, Japan", "New York, USA", "London, UK",
            "Rome, Italy", "Barcelona, Spain", "Bangkok, Thailand", "Sydney, Australia",
            "Dubai, UAE", "Istanbul, Turkey"
        ]
    
    def format_timestamp(self, timestamp_str):
        """Format timestamp for display"""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - timestamp.replace(tzinfo=None)
            
            if diff.days > 7:
                return timestamp.strftime("%b %d, %Y")
            elif diff.days > 0:
                return f"{diff.days}d ago"
            elif diff.seconds > 3600:
                return f"{diff.seconds // 3600}h ago"
            elif diff.seconds > 60:
                return f"{diff.seconds // 60}m ago"
            else:
                return "Just now"
        except:
            return timestamp_str

# Usage example for integration with your main app
def add_community_to_sidebar():
    """Add community section to your existing Streamlit sidebar"""
    if st.sidebar.button("📸 Community"):
        st.session_state.current_page = "community"

def main():
    """Main function to run the community app standalone"""
    st.set_page_config(
        page_title="Travel Community",
        page_icon="📸",
        layout="wide"
    )
    
    community_app = CommunityApp()
    community_app.run_community_section()

if __name__ == "__main__":
    main()