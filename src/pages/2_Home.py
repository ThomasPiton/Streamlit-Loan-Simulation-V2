import streamlit as st
import base64
import os

# --- Page config ---
st.set_page_config(
    page_title="My App",
    page_icon="🏦",
    layout="wide",
)

# --- Hide default Streamlit chrome ---
hide_streamlit_style = """
    <style>
      #MainMenu, footer { visibility: hidden; }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- Function to encode video to base64 ---
def get_video_base64(video_path):
    """Convert video file to base64 string"""
    try:
        with open(video_path, "rb") as video_file:
            video_bytes = video_file.read()
            video_base64 = base64.b64encode(video_bytes).decode()
            return video_base64
    except FileNotFoundError:
        st.error(f"Video file not found: {video_path}")
        return None

# --- Hero video section ---
video_path = "./static/videos/intro.mp4"

# Check if video file exists
if os.path.exists(video_path):
    # Method 1: Using st.video (recommended for simplicity)
    st.video(video_path)
    
    # Alternative Method 2: Using base64 encoding for more control
    # Uncomment the following lines if you need autoplay, loop, etc.
    """
    video_base64 = get_video_base64(video_path)
    if video_base64:
        st.markdown(
            f'''
            <div class="banner-video-container" style="text-align: center; margin-bottom: 2rem;">
                <video width="100%" height="100" autoplay muted loop controls>
                    <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    """
else:
    st.warning("Video file not found. Please check the path: ./static/videos/intro.mp4")
    # Show placeholder or alternative content
    st.markdown(
        """
        <div style="background-color: #f0f2f6; padding: 3rem; text-align: center; margin-bottom: 2rem;">
            <h3>🎥 Video Coming Soon</h3>
            <p>Video content will be displayed here once the file is available.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# 3) Headline + Subheader
st.markdown(
    "<h1 style='text-align:center; margin-top:0;'>Welcome to Your App</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<h4 style='text-align:center; color:#666;'>"
    "Discover insights, run simulations, and connect with our community."
    "</h4>",
    unsafe_allow_html=True,
)

st.write("")  # spacer

# 4) Key Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Users", "12K+", "+5%")
col2.metric("Simulations Run", "3.4K", "+12%")
col3.metric("Satisfaction", "98%", "▲2%")

st.write("---")

# 5) About Section
left, right = st.columns((2, 3))
with left:
    st.subheader("Why Choose Us?")
    st.write(
        """
        - Interactive, real-time simulations  
        - Comprehensive analytics dashboard  
        - 24/7 community & support  
        - Enterprise-grade security
        """
    )
    if st.button("Learn More"):
        # Use st.switch_page for navigation (updated method)
        st.query_params.page = "3_About"
        st.rerun()

with right:
    # Check if image exists before displaying
    image_path = "./static/img/about_preview.png"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)
    else:
        st.markdown(
            """
            <div style="background-color: #f0f2f6; padding: 2rem; text-align: center; border-radius: 10px;">
                <p>🖼️ Preview image will be displayed here</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("---")

# 6) Call to Action
st.markdown(
    """
    <div style="text-align:center; margin:2rem 0;">
      <button onclick="window.location.href='?page=3_About'"
              style="
                background-color: #0078D4;
                color: white;
                padding: 1rem 2rem;
                font-size: 1.1rem;
                border: none;
                border-radius: 5px;
                cursor: pointer;
              ">
        Get Started Now
      </button>
    </div>
    """,
    unsafe_allow_html=True,
)

# 7) Footer
st.markdown(
    """
    <hr>
    <div style="text-align:center; color:#888; font-size:0.9rem; padding:1rem 0;">
      © 2025 Your Company &nbsp;&middot;&nbsp;
      <a href="?page=4_Contact" style="color:#0078D4;">Contact Us</a> &nbsp;&middot;&nbsp;
      <a href="?page=1_FAQ" style="color:#0078D4;">FAQ</a>
    </div>
    """,
    unsafe_allow_html=True,
)