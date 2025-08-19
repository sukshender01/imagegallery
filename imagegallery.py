import streamlit as st
import requests
from io import BytesIO
from PIL import Image
import random

# ------------------------------------------------------
# CONFIG - Your GitHub Repo
# ------------------------------------------------------
USERNAME = "sukshender01"
REPO = "imagegallery"
BRANCH = "main"
FOLDER = ""   # images are in repo root

# GitHub API and raw URLs
GITHUB_API_URL = f"https://api.github.com/repos/{USERNAME}/{REPO}/contents/{FOLDER}"
RAW_BASE_URL = f"https://raw.githubusercontent.com/{USERNAME}/{REPO}/{BRANCH}/{FOLDER}"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

# ------------------------------------------------------
# STREAMLIT APP
# ------------------------------------------------------
st.set_page_config(page_title="GitHub Image Gallery", layout="wide")
st.title("📸 GitHub Image Gallery with Slideshow")

@st.cache_data
def fetch_github_images():
    """Fetch list of image file names from GitHub directory"""
    try:
        response = requests.get(GITHUB_API_URL)
        response.raise_for_status()
        files = response.json()
        return [f["name"] for f in files if f["name"].lower().endswith(IMAGE_EXTENSIONS)]
    except Exception as e:
        st.error(f"Error fetching images: {e}")
        return []

# Initialize slideshow index
if "slide" not in st.session_state:
    st.session_state["slide"] = 1

# Sidebar controls
st.sidebar.header("⚙️ Gallery Controls")

# Refresh button
if st.sidebar.button("🔄 Refresh Images"):
    fetch_github_images.clear()   # Clear cache
    st.rerun()  # Reload app to fetch updated images

# Load images
images = fetch_github_images()

if not images:
    st.warning("No images found in the GitHub directory.")
    st.stop()

view_mode = st.sidebar.radio("Select View Mode", ["Gallery Grid", "Slideshow"])
shuffle = st.sidebar.checkbox("Shuffle Images", value=False)

if shuffle:
    random.shuffle(images)

# ------------------------------------------------------
# Gallery Mode
# ------------------------------------------------------
if view_mode == "Gallery Grid":
    cols = st.columns(3)  # Display in 3 columns
    for i, img_name in enumerate(images):
        with cols[i % 3]:
            img_url = f"{RAW_BASE_URL}{img_name}"
            st.image(img_url, caption=img_name, use_container_width=True)
            st.download_button("⬇️ Download", img_url, file_name=img_name)

# ------------------------------------------------------
# Slideshow Mode
# ------------------------------------------------------
else:
    st.markdown("### ▶️ Slideshow Mode")

    # Get current index
    index = st.session_state["slide"]

    # Safety check for index
    if index < 1:
        index = 1
    if index > len(images):
        index = len(images)
    st.session_state["slide"] = index

    img_name = images[index - 1]
    img_url = f"{RAW_BASE_URL}{img_name}"

    # Fetch & display
    response = requests.get(img_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))

        # Split image into clickable areas
        left, center, right = st.columns([1, 6, 1])

        with center:
            st.image(image, caption=img_name, use_container_width=True)

        # Clicking left/right to navigate
        with left:
            if st.button("⬅️", use_container_width=True):
                st.session_state["slide"] = max(1, index - 1)
                st.rerun()

        with right:
            if st.button("➡️", use_container_width=True):
                st.session_state["slide"] = min(len(images), index + 1)
                st.rerun()

        # Download button below image
        st.download_button("⬇️ Download this image", response.content, file_name=img_name)

    # Slider navigation
    st.session_state["slide"] = st.slider("Image", 1, len(images), index, step=1)
