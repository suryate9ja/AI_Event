import streamlit as st
import tempfile
import os
from video_processing.reel_generator import ReelGenerator
import plotly.graph_objects as go
import time
import subprocess
from contextlib import ExitStack
import gc

# Initialize session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Page configuration
st.set_page_config(
    page_title="AI Event Reel Generator",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- DARK MODE MANAGEMENT ---
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

def set_theme():
    theme = 'dark' if st.session_state.dark_mode else 'light'
    st.markdown(f"""
        <script>
            document.body.setAttribute('data-theme', '{theme}');
            document.documentElement.setAttribute('data-theme', '{theme}');
        </script>
    """, unsafe_allow_html=True)

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode
    set_theme()

set_theme()

# --- APPLE-LIKE CSS ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        background: none !important;
    }
    
    /* Animated gradient background */
    body::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        z-index: -2;
        background: linear-gradient(120deg, #e0e7ef 0%, #f5f7fa 100%);
        background-size: 400% 400%;
        animation: gradientMove 18s ease infinite;
        opacity: 0.7;
    }
    
    @keyframes gradientMove {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Dark mode overrides */
    [data-theme="dark"] body::before {
        background: linear-gradient(120deg, #232526 0%, #414345 100%);
        opacity: 0.85;
    }
    /* Glassmorphism card */
    .section-container {
        background: rgba(255,255,255,0.55);
        border-radius: 24px;
        box-shadow: 0 8px 32px 0 rgba(31,38,135,0.10);
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255,255,255,0.18);
        margin: 2rem 0;
        padding: 2.5rem 2rem 2rem 2rem;
        transition: box-shadow 0.3s, background 0.3s;
    }
    [data-theme="dark"] .section-container {
        background: rgba(36, 37, 38, 0.65);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.25);
    }
    .section-container:hover {
        box-shadow: 0 16px 48px 0 rgba(31,38,135,0.18);
        background: rgba(255,255,255,0.65);
    }
    [data-theme="dark"] .section-container:hover {
        background: rgba(36, 37, 38, 0.85);
    }
    /* Floating nav bar */
    .nav-bar {
        position: fixed;
        top: 24px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 100;
        background: rgba(255,255,255,0.7);
        border-radius: 18px;
        box-shadow: 0 2px 16px 0 rgba(31,38,135,0.10);
        padding: 0.5rem 2.5rem;
        display: flex;
        gap: 2rem;
        align-items: center;
        font-size: 1.1rem;
        font-weight: 500;
        letter-spacing: 0.01em;
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.18);
        transition: background 0.3s;
    }
    [data-theme="dark"] .nav-bar {
        background: rgba(36, 37, 38, 0.85);
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 2px 16px 0 rgba(0,0,0,0.18);
    }
    .nav-bar .nav-logo {
        font-size: 1.5rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-right: 1.5rem;
        color: #007AFF;
        background: linear-gradient(90deg, #007AFF, #5856D6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .nav-bar .nav-link {
        color: #222;
        text-decoration: none;
        padding: 0.2rem 0.7rem;
        border-radius: 8px;
        transition: background 0.2s, color 0.2s;
    }
    .nav-bar .nav-link:hover {
        background: #f0f4fa;
        color: #007AFF;
    }
    [data-theme="dark"] .nav-bar .nav-link {
        color: #f5f5f7;
    }
    [data-theme="dark"] .nav-bar .nav-link:hover {
        background: #232526;
        color: #0A84FF;
    }
    /* Apple-style dark mode toggle */
    .dark-toggle {
        margin-left: 1.5rem;
        cursor: pointer;
        border-radius: 50%;
        width: 38px; height: 38px;
        display: flex; align-items: center; justify-content: center;
        background: rgba(255,255,255,0.7);
        box-shadow: 0 2px 8px 0 rgba(31,38,135,0.10);
        border: 1px solid rgba(255,255,255,0.18);
        transition: background 0.3s, box-shadow 0.3s;
        font-size: 1.3rem;
    }
    .dark-toggle:hover {
        background: #f0f4fa;
        box-shadow: 0 4px 16px 0 rgba(31,38,135,0.18);
    }
    [data-theme="dark"] .dark-toggle {
        background: rgba(36, 37, 38, 0.85);
        border: 1px solid rgba(255,255,255,0.08);
        color: #f5f5f7;
    }
    [data-theme="dark"] .dark-toggle:hover {
        background: #232526;
    }
    /* Title and typography */
    .apple-title {
        font-size: 2.8rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        margin-bottom: 0.5rem;
        background: linear-gradient(90deg, #007AFF, #5856D6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-top: 2.5rem;
        margin-bottom: 2.5rem;
        line-height: 1.1;
    }
    .apple-subtitle {
        font-size: 1.25rem;
        color: #555;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    [data-theme="dark"] .apple-subtitle {
        color: #bbb;
    }
    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #e0e7ef; border-radius: 4px; }
    [data-theme="dark"] ::-webkit-scrollbar-thumb { background: #232526; }
    /* Progress bar, video, plotly, etc. */
    .stProgress > div > div { background: linear-gradient(90deg, #007AFF, #5856D6); }
    .stVideo, .js-plotly-plot { border-radius: 18px !important; box-shadow: 0 4px 16px 0 rgba(31,38,135,0.10); }
    .stButton>button { border-radius: 12px !important; font-weight: 600; font-size: 1.1rem; padding: 0.5rem 1.5rem; }
    .stButton>button:hover { background: #007AFF !important; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# --- FLOATING NAV BAR ---
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">ReelGen</div>
    <a class="nav-link" href="#upload">Upload</a>
    <a class="nav-link" href="#generate">Generate</a>
    <a class="nav-link" href="#seating">Seating Map</a>
    <button class="dark-toggle" onclick="document.dispatchEvent(new CustomEvent('dark_mode_toggle'));">
        🌙
    </button>
</div>
""", unsafe_allow_html=True)

# JavaScript for dark mode toggle
st.markdown("""
<script>
document.addEventListener('dark_mode_toggle', function() {
    window.parent.postMessage({type: 'dark_mode_toggle'}, '*');
});
</script>
""", unsafe_allow_html=True)

# --- DARK MODE TOGGLE ---
col1, col2 = st.columns([10,1])
with col2:
    if st.button('🌙' if not st.session_state.dark_mode else '☀️', key='dark_mode_toggle', help='Toggle dark mode', use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        set_theme()
        st.experimental_rerun()

# --- HERO SECTION ---
st.markdown("""
<style>
    .hero-section {
        max-width: 800px;
        margin: 0 auto;
        padding-top: 96px;
        text-align: center;
    }
    .hero-heading {
        font-size: 64px;
        font-weight: 600;
        color: #2D3436;
        line-height: 1.2;
        margin-bottom: 24px;
    }
    [data-theme="dark"] .hero-heading {
        color: #F5F6FA;
    }
    .hero-subtext {
        font-size: 24px;
        line-height: 1.5;
        color: #636E72;
        margin-bottom: 40px;
    }
    [data-theme="dark"] .hero-subtext {
        color: #B2BEC3;
    }
    .hero-cta {
        display: inline-block;
        padding: 16px 32px;
        font-size: 18px;
        font-weight: 600;
        color: white;
        background: linear-gradient(135deg, #0984E3, #74B9FF);
        border-radius: 48px;
        text-decoration: none;
        transition: transform 0.2s, box-shadow 0.2s;
        margin-bottom: 16px;
    }
    .hero-cta:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(9, 132, 227, 0.3);
    }
    .hero-secondary {
        display: block;
        color: #0984E3;
        text-decoration: none;
        font-size: 16px;
        font-weight: 500;
        margin-top: 16px;
    }
    .hero-secondary:hover {
        text-decoration: underline;
    }
</style>
<div class="hero-section">
    <h1 class="hero-heading">Transform Your Event Footage</h1>
    <p class="hero-subtext">
        Create stunning highlight reels automatically with our AI-powered video generator. 
        Perfect for events, conferences, and memorable occasions.
    </p>
    <a href="#upload" class="hero-cta">Start Creating →</a>
    <a href="#" class="hero-secondary">Create New Project</a>
</div>
""", unsafe_allow_html=True)

# --- MAIN TITLE ---
st.markdown('<div class="apple-title">AI Event Reel Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="apple-subtitle">Create stunning event highlight reels with AI, in true Apple style.</div>', unsafe_allow_html=True)

# --- VIDEO UPLOAD SECTION ---
st.markdown('<div class="section-container" id="upload">', unsafe_allow_html=True)
st.header("🎥 Upload Event Videos")
st.markdown("""
<p style='font-size: 1.1rem;'>Upload your event videos to create an AI-powered highlight reel. We support MP4 format.</p>
""", unsafe_allow_html=True)
uploaded_files = st.file_uploader(
    "Choose your video files",
    type=["mp4"],
    accept_multiple_files=True
)
st.markdown('</div>', unsafe_allow_html=True)

# --- REEL GENERATION SECTION ---
st.markdown('<div class="section-container" id="generate">', unsafe_allow_html=True)
st.header("✨ Generate AI Reel")
reel_path = None
generator = ReelGenerator()

def handle_video_upload(uploaded_files):
    with ExitStack() as stack:
        temp_video_paths = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        error_text = st.empty()
        
        try:
            # Validate uploads
            if not uploaded_files:
                raise ValueError("No files uploaded")
                
            # Save uploaded files
            status_text.text("📥 Saving uploaded files...")
            for i, file in enumerate(uploaded_files):
                temp_file = stack.enter_context(tempfile.NamedTemporaryFile(suffix=".mp4", delete=False))
                temp_file.write(file.getvalue())
                temp_file.flush()
                temp_video_paths.append(temp_file.name)
                progress_bar.progress((i + 1) * 20 // len(uploaded_files))
            
            # Generate reel
            status_text.text("🎬 Generating reel...")
            generator = ReelGenerator()
            output_path = generator.merge_clips(
                temp_video_paths,
                progress_callback=lambda p: progress_bar.progress(20 + int(p * 0.8))
            )
            
            return output_path
            
        except Exception as e:
            error_text.error(f"❌ Error: {str(e)}")
            return None
        finally:
            # Cleanup
            progress_bar.empty()
            status_text.empty()
            for path in temp_video_paths:
                try:
                    if os.path.exists(path):
                        os.unlink(path)
                except:
                    pass
            gc.collect()

if uploaded_files:
    reel_path = handle_video_upload(uploaded_files)
    if reel_path and os.path.exists(reel_path):
        st.success("✨ Your AI-generated reel is ready!")
        st.video(reel_path)
        with open(reel_path, "rb") as f:
            st.download_button(
                label="⬇️ Download Reel",
                data=f,
                file_name="event_reel.mp4",
                mime="video/mp4",
                help="Click to download your generated reel"
            )
        os.unlink(reel_path)
st.markdown('</div>', unsafe_allow_html=True)

# --- SEATING MAP SECTION ---
st.markdown('<div class="section-container" id="seating">', unsafe_allow_html=True)
st.header("🗺️ Seating Map Visualization")
st.markdown("""
<p style='font-size: 1.1rem;'>Interactive seating map for your event. Hover over tables to see details.</p>
""", unsafe_allow_html=True)
table_x = [1, 2, 3, 1, 2, 3]
table_y = [1, 1, 1, 2, 2, 2]
labels = ["A1", "A2", "A3", "B1", "B2", "B3"]

def create_seating_map():
    is_dark = st.session_state.dark_mode
    bg_color = 'rgba(36, 37, 38, 0.85)' if is_dark else 'rgba(255,255,255,0.7)'
    text_color = '#f5f5f7' if is_dark else '#222'
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=table_x,
        y=table_y,
        mode='markers+text',
        marker=dict(
            size=40,
            color='#007AFF',
            line=dict(
                color=text_color,
                width=2
            )
        ),
        text=labels,
        textposition="middle center",
        textfont=dict(color=text_color),
        hoverinfo='text',
        hovertext=[f"Table {label}" for label in labels]
    ))
    
    fig.update_layout(
        title="Event Seating Map",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 3]),
        height=400,
        plot_bgcolor=bg_color,
        paper_bgcolor=bg_color,
        font=dict(
            family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
            size=14,
            color=text_color
        )
    )
    return fig

# Update seating map section
st.plotly_chart(create_seating_map(), use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- ACTION CARDS GRID ---
st.markdown("""
<style>
    .cards-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 32px;
        max-width: 1200px;
        margin: 48px auto;
        padding: 0 24px;
    }
    .action-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
    }
    [data-theme="dark"] .action-card {
        background: rgba(36, 37, 38, 0.95);
        box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.2);
    }
    .action-card:hover {
        transform: scale(1.02);
        box-shadow: 0px 12px 32px rgba(0, 0, 0, 0.15);
    }
    .card-header {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 16px;
    }
    .card-checkbox {
        width: 20px;
        height: 20px;
        border: 2px solid #0984E3;
        border-radius: 6px;
        cursor: pointer;
    }
    .card-icon {
        font-size: 24px;
        color: #0984E3;
    }
    .card-title {
        font-size: 20px;
        font-weight: 600;
        color: #2D3436;
        margin: 0;
        line-height: 1.4;
    }
    [data-theme="dark"] .card-title {
        color: #F5F6FA;
    }
</style>
<div class="cards-grid">
    <div class="action-card">
        <div class="card-header">
            <div class="card-checkbox"></div>
            <div class="card-icon">📤</div>
        </div>
        <h3 class="card-title">Upload Event Videos</h3>
    </div>
    <div class="action-card">
        <div class="card-header">
            <div class="card-checkbox"></div>
            <div class="card-icon">✨</div>
        </div>
        <h3 class="card-title">Generate AI Highlights</h3>
    </div>
    <div class="action-card">
        <div class="card-header">
            <div class="card-checkbox"></div>
            <div class="card-icon">⬇️</div>
        </div>
        <h3 class="card-title">Download Your Reel</h3>
    </div>
</div>
""", unsafe_allow_html=True)

# --- RECENT CREATIONS GRID ---
st.markdown("""
<style>
    .creations-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 24px;
        max-width: 1200px;
        margin: 48px auto;
        padding: 0 24px;
    }
    @media (max-width: 768px) {
        .creations-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    .creation-card {
        position: relative;
        border-radius: 12px;
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.3s ease;
    }
    .creation-card:hover {
        transform: translateY(-4px);
    }
    .thumbnail {
        position: relative;
        padding-top: 56.25%; /* 16:9 aspect ratio */
        background: linear-gradient(135deg, #636E72, #2D3436);
    }
    .thumbnail-overlay {
        position: absolute;
        inset: 0;
        background: linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 50%);
        transition: background 0.3s ease;
    }
    .creation-card:hover .thumbnail-overlay {
        background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.2) 50%);
    }
    .creation-title {
        position: absolute;
        bottom: 16px;
        left: 16px;
        right: 16px;
        color: white;
        font-size: 20px;
        font-weight: 600;
        line-height: 1.3;
        margin: 0;
        z-index: 2;
    }
    .creation-metadata {
        position: absolute;
""", unsafe_allow_html=True)

# --- FLOATING CONTROL PANEL ---
st.markdown("""
<style>
    .control-panel {
        position: fixed;
        bottom: 48px;
        right: 48px;
        z-index: 1000;
        display: flex;
        flex-direction: column;
        gap: 16px;
        align-items: center;
    }
    .control-button {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        border: none;
        background: linear-gradient(135deg, #0984E3, #74B9FF);
        color: white;
        font-size: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(9, 132, 227, 0.3);
        transition: transform 0.3s cubic-bezier(0.68, -0.6, 0.32, 1.6);
    }
    .control-button:hover {
        transform: scale(1.1);
    }
    .control-button.secondary {
        width: 48px;
        height: 48px;
        font-size: 20px;
        background: rgba(255,255,255,0.9);
        color: #0984E3;
        opacity: 0;
        transform: translateY(20px);
        transition: transform 0.3s cubic-bezier(0.68, -0.6, 0.32, 1.6), 
                    opacity 0.3s ease;
    }
    [data-theme="dark"] .control-button.secondary {
        background: rgba(36, 37, 38, 0.95);
        color: #74B9FF;
    }
    .control-panel:hover .control-button.secondary {
        opacity: 1;
        transform: translateY(0);
    }
    .control-menu {
        position: absolute;
        bottom: 70px;
        right: 70px;
        background: white;
        border-radius: 12px;
        padding: 8px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.15);
        opacity: 0;
        transform: scale(0.95) translateY(10px);
        transition: all 0.3s cubic-bezier(0.68, -0.6, 0.32, 1.6);
        pointer-events: none;
    }
    [data-theme="dark"] .control-
</style>
<div class="control-panel">
    <button class="control-button">+</button>
    <button class="control-button secondary">📤</button>
    <button class="control-button secondary">✨</button>
    <button class="control-button secondary">⬇️</button>
</div>
""", unsafe_allow_html=True)

# --- PROGRESS TIMELINE ---
st.markdown("""
<style>
    .progress-timeline {
        max-width: 800px;
        margin: 48px auto;
        padding: 24px 0;
        position: relative;
    }
    .timeline-line {
        position: absolute;
        top: 36px;
        left: 50%;
        transform: translateX(-50%);
        width: calc(100% - 96px);
        height: 2px;
        background: #E2E8F0;
        z-index: 1;
    }
    [data-theme="dark"] .timeline-line {
        background: #4A5568;
    }
    .timeline-steps {
        position: relative;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        z-index: 2;
    }
    .timeline-step {
        display: flex;
        flex
""", unsafe_allow_html=True)

def error_boundary(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            if st.checkbox("Show error details"):
                st.exception(e)
    return wrapper

@error_boundary
def main():
    pass

if __name__ == "__main__":
    main()