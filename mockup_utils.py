from PIL import Image
import os
from template_coordinates import TEMPLATE_COORDINATES

def generate_mockup(template_path, artwork_path, client, campaign, date_str, output_dir):
    # Load template and artwork
    template_img = Image.open(template_path).convert("RGBA")
    artwork_img = Image.open(artwork_path).convert("RGBA")

    # Get coordinates for template
    template_filename = os.path.basename(template_path)
    coords = TEMPLATE_COORDINATES.get(template_filename)
    if not coords:
        raise ValueError(f"No coordinates found for: {template_filename}")

    # Resize artwork to match destination polygon bounding box (very simple logic)
    # We assume coords form a rectangle for now
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = coords
    min_x = min(x1, x2, x3, x4)
    max_x = max(x1, x2, x3, x4)
    min_y = min(y1, y2, y3, y4)
    max_y = max(y1, y2, y3, y4)

    width = max_x - min_x
    height = max_y - min_y
    artwork_resized = artwork_img.resize((width, height))

    # Paste artwork onto template using simple paste (future: perspective transform)
    template_img.paste(artwork_resized, (min_x, min_y), artwork_resized)

    # Construct filename
    template_name = os.path.splitext(template_filename)[0]  # remove .png
    artwork_name = os.path.splitext(os.path.basename(artwork_path))[0]
    campaign_suffix = "-".join(artwork_name.split("-")[1:]).strip() or "Artwork"

    output_name = f"{template_name} - {client} - {campaign_suffix} - {date_str} - Mock Up.png"
    output_path = os.path.join(output_dir, output_name)

    # Save result
    template_img.save(output_path)
    return output_path