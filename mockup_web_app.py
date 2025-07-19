import os
import zipfile
from PIL import Image
from mockup_utils import generate_mockup, generate_filename
from template_coordinates import TEMPLATE_COORDINATES
import streamlit as st

st.image("https://raw.githubusercontent.com/phoebegawk/mockup-machine/main/Header-UI-Mock.png", use_container_width=True)

st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-size: 18px !important;
    }

    label, button, input, textarea, select {
        font-size: 18px !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    .block-container {
        padding-top: 2rem !important;
    }

    /* Ensure file uploader text is left-aligned */
    section[data-testid="stFileUploader"] label > div {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        text-align: left;
    }

    section[data-testid="stFileUploader"] p {
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .stButton > button {
        display: block;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

if "generated_outputs" not in st.session_state:
    st.session_state["generated_outputs"] = []

# Paths
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "generated_mockups"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# UI Config
st.set_page_config(page_title="Mock Up Machine", layout="wide")

# Template Selection
template_keys = list(TEMPLATE_COORDINATES.keys())
template_display_names = [name.replace(".png", "") for name in template_keys]
selected_display_names = st.multiselect("📍 Select Billboard(s):", template_display_names)
selected_templates = [name + ".png" for name in selected_display_names]

# Artwork Upload
artwork_files = st.file_uploader("🖼️ Upload Artwork File(s):", type=["jpg", "jpeg"], accept_multiple_files=True)

# Artwork preview with filename
if artwork_files:
    os.makedirs("uploaded_artwork", exist_ok=True)
    
    cols = st.columns(4)  # Up to 4 previews per row
    for idx, file in enumerate(artwork_files):
        artwork_path = os.path.join("uploaded_artwork", file.name)
        with open(artwork_path, "wb") as f:
            f.write(file.getbuffer())
        with cols[idx % 4]:
            st.image(artwork_path, caption=file.name, width=250)
            st.markdown("<div style='margin-bottom: -10px;'></div>", unsafe_allow_html=True)

# Client & Date Input
client_name = st.text_input("🔍 Client Name:")
live_date = st.text_input("🗓️ Live Date (DDMMYY):")

# Centered row with Generate and conditional Download buttons
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    generate_clicked = st.button("Generate")

# Trigger generation logic
if generate_clicked:
    if not selected_templates:
        st.warning("Please select at least one template.")
    elif not artwork_files:
        st.warning("Please upload at least one artwork file.")
    elif not client_name or not live_date:
        st.warning("Please enter client name and live date.")
    else:
        if "generated_outputs" not in st.session_state:
            st.session_state.generated_outputs = []

        for selected_template in selected_templates:
            if not selected_template.endswith(".png"):
                selected_template += ".png"
            template_path = os.path.join("Templates", "Digital", selected_template)

            template_data = TEMPLATE_COORDINATES.get(selected_template)
            if not template_data or "LHS" not in template_data:
                st.error(f"Coordinates not found or malformed for {selected_template}.")
                continue
            coords = template_data["LHS"]

            for artwork_file in artwork_files:
                try:
                    artwork_path = os.path.join("uploaded_artwork", artwork_file.name)
                    os.makedirs("uploaded_artwork", exist_ok=True)
                    with open(artwork_path, "wb") as f:
                        f.write(artwork_file.getbuffer())

                    campaign_name = artwork_file.name.split("-", 1)[-1].rsplit(".", 1)[0].strip()
                    final_filename = generate_filename(selected_template, client_name, campaign_name, live_date)
                    output_path = os.path.join(OUTPUT_DIR, final_filename)

                    generate_mockup(template_path, artwork_path, output_path, coords)

                    st.session_state.generated_outputs.append((final_filename, output_path))
                except Exception as e:
                    st.error(f"❌ Error generating mockup for {selected_template}: {e}")

# Recreate button row again with download enabled
if st.session_state.generated_outputs:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        zip_name = f"Mock_Ups_{client_name}_{live_date}.zip"
        zip_path = os.path.join("generated_mockups", zip_name)

        with zipfile.ZipFile(zip_path, "w") as zipf:
            for filename, file_path in st.session_state.generated_outputs:
                zipf.write(file_path, arcname=filename)

        with open(zip_path, "rb") as f:
            st.download_button(
                label="Download Mock Ups",
                data=f,
                file_name=zip_name,
                mime="application/zip"
            )
            
        for selected_template in selected_templates:
            if not selected_template.endswith(".png"):
                selected_template += ".png"
            template_path = os.path.join("Templates", "Digital", selected_template)

            template_data = TEMPLATE_COORDINATES.get(selected_template)
            if not template_data or "LHS" not in template_data:
                st.error(f"Coordinates not found or malformed for {selected_template}.")
                continue
            coords = template_data["LHS"]

            for artwork_file in artwork_files:
                try:
                    artwork_path = os.path.join("uploaded_artwork", artwork_file.name)
                    os.makedirs("uploaded_artwork", exist_ok=True)
                    with open(artwork_path, "wb") as f:
                        f.write(artwork_file.getbuffer())

                    campaign_name = artwork_file.name.split("-", 1)[-1].rsplit(".", 1)[0].strip()
                    final_filename = generate_filename(selected_template, client_name, campaign_name, live_date)
                    output_path = os.path.join(OUTPUT_DIR, final_filename)

                    generate_mockup(template_path, artwork_path, output_path, coords)

                    st.session_state.generated_outputs.append((final_filename, output_path))
                except Exception as e:
                    st.error(f"❌ Error generating mockup for {selected_template}: {e}")

# Display thumbnails in a 4-column layout after all are generated
if st.session_state.generated_outputs:
    cols = st.columns(4)
    for i, (filename, path) in enumerate(st.session_state.generated_outputs):
        with cols[i % 4]:
            st.image(path, caption=filename, use_container_width=True)

    for filename, _ in st.session_state.generated_outputs:
        st.success(f"✅ Generated: {filename}")

# Safely check and prepare generated_outputs
if "generated_outputs" in st.session_state and st.session_state.generated_outputs:
    zip_name = f"Mock_Ups_{client_name}_{live_date}.zip"
    zip_path = os.path.join("generated_mockups", zip_name)

    # Create ZIP with all generated mockups
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for filename, file_path in st.session_state.generated_outputs:
            zipf.write(file_path, arcname=filename)

# Provide download button
with col3:
    if st.session_state.generated_outputs:
        with open(zip_path, "rb") as f:
            st.download_button(
                label="Download Mock Ups",
                data=f,
                file_name=zip_name,
                mime="application/zip",
                key="download_button"
            )
    else:
        st.download_button(
            label="Download Mock Ups",
            data=b"",
            file_name="",
            disabled=True,
            key="download_button"
        )
