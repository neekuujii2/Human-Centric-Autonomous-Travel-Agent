"""
Shopping Page - AI Trip Planner
Find nearby shopping places including malls, local markets, and retail areas
"""

import streamlit as st
import folium
from streamlit_folium import st_folium
import plotly.express as px
import pandas as pd
from typing import Dict
from agents.shopping_places import ShoppingPlacesFinder, GEOAPIFY_API_KEY, PEXELS_API_KEY

# Page configuration
st.set_page_config(
    page_title="Shopping Places Finder",
    page_icon="🛍️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .shopping-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 15px;
        border-left: 5px solid #ff6b35;
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .shopping-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .famous-market {
        background-color: #fff7e6;
        border-left-color: #ffc107;
    }
</style>
""", unsafe_allow_html=True)

def initialize_shopping_finder():
    """Initialize the shopping finder with API key"""
    if not GEOAPIFY_API_KEY:
        st.error("⚠️ Geoapify API key not found. Please set GEOAPIFY_API_KEY in your environment variables.")
        st.info("Get your free API key from: https://www.geoapify.com/")
        return None
    return ShoppingPlacesFinder(GEOAPIFY_API_KEY)

def create_shopping_map(places_data: Dict, center_coords: tuple):
    """Create an interactive map with shopping places"""
    m = folium.Map(location=center_coords, zoom_start=13, tiles='OpenStreetMap')

    folium.Marker(
        center_coords,
        popup="📍 Search Location",
        tooltip="Your search location",
        icon=folium.Icon(color='red', icon='home')
    ).add_to(m)

    category_colors = {
        'shopping_malls': 'blue',
        'local_markets': 'orange',
        'retail_areas': 'green',
        'supermarkets': 'purple'
    }
    category_icons = {
        'shopping_malls': 'shopping-cart',
        'local_markets': 'star',
        'retail_areas': 'store',
        'supermarkets': 'shopping-basket'
    }

    for category, places in places_data.items():
        if category == 'all_places' or not places:
            continue
        color = category_colors.get(category, 'gray')
        icon_name = category_icons.get(category, 'info-sign')

        for place in places:
            coords = place.get('coordinates')
            if not coords:
                continue
            address = place.get('address', '') or ''
            popup_content = f"""
            <div style="width: 200px;">
                <h4>{place.get('name','')}</h4>
                <p><b>Distance:</b> {place.get('distance_km','?')} km</p>
                <p><b>Address:</b> {address[:50]}...</p>
                {'<p><b>⭐ Famous Local Market!</b></p>' if place.get('is_famous_local') else ''}
            </div>
            """
            folium.Marker(
                coords,
                popup=folium.Popup(popup_content, max_width=250),
                tooltip=place.get('name',''),
                icon=folium.Icon(color=color, icon=icon_name, prefix='fa')
            ).add_to(m)
    return m

def display_places_by_category(places_data: Dict, finder: ShoppingPlacesFinder):
    """Display places organized by category with images"""
    categories = [
        ('local_markets', '🏪 Local Markets & Bazaars', 'Famous local shopping destinations'),
        ('shopping_malls', '🏬 Shopping Malls', 'Modern shopping centers'),
        ('retail_areas', '🛍️ Retail Areas', 'Shopping streets and districts'),
        ('supermarkets', '🛒 Supermarkets', 'Grocery stores and markets')
    ]

    for category_key, category_title, category_desc in categories:
        places = places_data.get(category_key, [])
        if not places:
            continue

        st.markdown(f"### {category_title}")
        st.markdown(f"*{category_desc}*")

        cols = st.columns(2)
        for idx, place in enumerate(places[:10]):
            col = cols[idx % 2]
            with col:
                card_class = "shopping-card"
                if place.get('is_famous_local'):
                    card_class += " famous-market"

                # Prefer the image attached by the agent, else call the method, else placeholder
                img_url = (
                    place.get('image_url')
                    or finder.get_place_image(place.get('name', 'shopping'))
                    or "https://source.unsplash.com/400x300/?shopping"
                )

                with st.container():
                    st.markdown(f"""
                    <div class="{card_class}" style="box-shadow:0 4px 12px rgba(0,0,0,0.1);">
                        <img src="{img_url}" style="width:100%;height:180px;object-fit:cover;border-radius:8px;margin-bottom:10px;" />
                        <h4>{place.get('name','')} {'⭐' if place.get('is_famous_local') else ''}</h4>
                        <p><strong>📍 Distance:</strong> {place.get('distance_km','?')} km away</p>
                        <p><strong>🏠 Address:</strong> {place.get('address','')}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    with st.expander("More Details"):
                        col1, col2 = st.columns(2)
                        with col1:
                            phone = (place.get('contact') or {}).get('phone')
                            if phone:
                                st.write(f"📞 **Phone:** {phone}")
                            rating = place.get('rating')
                            if rating:
                                st.write(f"⭐ **Rating:** {rating}/5")
                            if place.get('is_famous_local'):
                                st.success("🌟 **Famous Local Market**")
                        with col2:
                            website = (place.get('contact') or {}).get('website')
                            if website:
                                st.write(f"🌐 **Website:** [Visit]({website})")
                            if place.get('coordinates'):
                                lat, lng = place['coordinates']
                                maps_url = f"https://www.google.com/maps?q={lat},{lng}"
                                st.write(f"🗺️ **Maps:** [Open in Google Maps]({maps_url})")
        st.markdown("---")

def create_summary_metrics(summary: Dict):
    """Create summary metrics display"""
    st.markdown("### 📊 Shopping Places Summary")
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="🏪 Local Markets", value=summary.get('local_markets', 0), help="Traditional markets and bazaars")
    with col2:
        st.metric(label="🏬 Shopping Malls", value=summary.get('shopping_malls', 0), help="Modern shopping centers")
    with col3:
        st.metric(label="🛍️ Retail Areas", value=summary.get('retail_areas', 0), help="Shopping streets and districts")
    with col4:
        st.metric(label="🛒 Supermarkets", value=summary.get('supermarkets', 0), help="Grocery stores and markets")
    with col5:
        st.metric(label="📍 Total Places", value=summary.get('total_places', 0), help="All shopping places found")

def create_distance_chart(places_data: Dict):
    """Create a chart showing distance distribution"""
    if not places_data.get('all_places'):
        return
    chart_data = []
    for place in places_data['all_places']:
        category = "Other"
        for cat_key, cat_places in places_data.items():
            if cat_key != 'all_places' and place in cat_places:
                category = cat_key.replace('_', ' ').title()
                break
        chart_data.append({
            'Name': place['name'][:20] + '...' if len(place['name']) > 20 else place['name'],
            'Distance (km)': place['distance_km'],
            'Category': category,
            'Famous': 'Yes' if place.get('is_famous_local') else 'No'
        })
    df = pd.DataFrame(chart_data)
    fig = px.scatter(
        df, x='Distance (km)', y='Name', color='Category', symbol='Famous',
        title='Shopping Places by Distance', height=400
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

def main():
    """Main shopping page function"""
    st.title("🛍️ Shopping Places Finder")
    st.markdown("Discover the best shopping destinations around your location!")

    finder = initialize_shopping_finder()
    if not finder:
        return

    with st.form(key="shopping_form"):
        st.subheader("🔍 Search Parameters")
        location = st.text_input(
            "📍 Enter Location",
            placeholder="e.g., Karol Bagh, Delhi",
            help="Enter a location to find nearby shopping places"
        )
        radius = st.slider("📏 Search Radius (km)", min_value=1, max_value=15, value=5,
                           help="How far to search for shopping places")
        limit = st.slider("📊 Maximum Results", min_value=1, max_value=15, value=5,
                          help="Maximum number of places to find")
        search_button = st.form_submit_button("🔍 Find Shopping Places")

    if search_button and location:
        with st.spinner("🔍 Searching for shopping places..."):
            results = finder.find_shopping_places(location=location, radius_km=radius, limit=limit)
            if "error" in results:
                st.error(f"❌ Error: {results['error']}")
                return
            st.session_state.shopping_results = results
            st.session_state.search_location = location
            coords = finder.geocode_location(location)
            if coords:
                st.session_state.search_coords = coords

    if hasattr(st.session_state, 'shopping_results') and st.session_state.shopping_results:
        results = st.session_state.shopping_results
        summary = finder.get_shopping_summary(results)
        create_summary_metrics(summary)
        st.markdown("---")

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### 🗺️ Shopping Places Map")
            if hasattr(st.session_state, 'search_coords'):
                shopping_map = create_shopping_map(results, st.session_state.search_coords)
                st_folium(shopping_map, width=500, height=400)
            else:
                st.info("Map not available - coordinates not found")

        with col2:
            st.markdown("### 📈 Distance Distribution")
            create_distance_chart(results)

        st.markdown("---")
        display_places_by_category(results, finder)

    elif search_button and not location:
        st.warning("⚠️ Please enter a location to search for shopping places.")

    with st.subheader("ℹ️ How to Use"):
        st.markdown("---")
        st.markdown("### ℹ️ Help")
        st.info("""
        **How to use:**
        1. Enter a location (city, area, or landmark)
        2. Adjust search radius and result limit
        3. Click 'Find Shopping Places'
        4. Explore results on map and in categories

        **Features:**
        - ⭐ Famous local markets highlighted
        - 🗺️ Interactive map with markers
        - 📊 Distance-based analysis
        - 📱 Mobile-friendly interface
        """)

if __name__ == "__main__":
    main()
