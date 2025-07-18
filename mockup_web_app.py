import streamlit as st
import os
import zipfile
from PIL import Image
from mockup_utils import generate_mockup, generate_filename
from template_coordinates import TEMPLATE_COORDINATES

st.set_page_config(
    page_title="Gawk: Mock Up Machine",
    page_icon="🖼️",
    layout="centered",
)
    
if "generated_outputs" not in st.session_state:
    st.session_state["generated_outputs"] = []

st.markdown("""
    <style>
        .block-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# Paths
TEMPLATE_DIR = "templates"
OUTPUT_DIR = "generated_mockups"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# UI Config
st.set_page_config(page_title="Mock Up Web App", layout="wide")
st.title("Mock Up Machine 🧚🏻‍♀️")

# Template Selection
template_keys = list(TEMPLATE_COORDINATES.keys())
template_display_names = [name.replace(".png", "") for name in template_keys]
selected_display_names = st.multiselect("📍 Select Billboard(s):", template_display_names)
selected_templates = [name + ".png" for name in selected_display_names]

# Artwork Upload
artwork_files = st.file_uploader("🖼️ Upload Artwork File(s):", type=["jpg", "jpeg"], accept_multiple_files=True)

# Client & Date Input
client_name = st.text_input("Client Name:")
live_date = st.text_input("Live Date (DDMMYY):")

# Make Mockups
if st.button("Generate"):
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
                    st.success(f"✅ Generated: {final_filename}")

                except Exception as e:
                    st.error(f"❌ Error generating mockup for {selected_template}: {e}")

# Display thumbnails
if st.session_state.generated_outputs:
    st.subheader("Generated Preview")
    cols = st.columns(4)
    for i, (filename, path) in enumerate(st.session_state.generated_outputs):
        with cols[i % 4]:
            st.image(path, caption=filename, use_container_width=True)

# Safely check and prepare generated_outputs
if "generated_outputs" in st.session_state and st.session_state.generated_outputs:
    zip_name = f"Mock_Ups_{client_name}_{live_date}.zip"
    zip_path = os.path.join("generated_mockups", zip_name)

    # Create ZIP with all generated mockups
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for _, file_path in st.session_state.generated_outputs:
            zipf.write(path, arcname=filename)

    # Provide download button
    with open(zip_path, "rb") as f:
        st.download_button(
            label="Download Mock Ups",
            data=f,
            file_name=zip_name,
            mime="application/zip"
        )
