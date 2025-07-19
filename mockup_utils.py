from PIL import Image
import os
from template_coordinates import TEMPLATE_COORDINATES

def generate_filename(template_name, artwork_name, client_name, live_date):
    """
    Generates the final output filename with the format:
    Site Name - Site Code - Client - Campaign - DDMMYY - Type
    """
    site = template_name.replace(".png", "")
    campaign = artwork_name.split("-", 1)[-1].rsplit(".", 1)[0].strip()
    filename = f"{site} - {client_name} - {campaign} - {live_date} - Mock Up.jpg"
    return filename

def generate_mockup(template_path, artwork_path, output_path, coords):
    try:
        template = Image.open(template_path).convert("RGBA")
        artwork = Image.open(artwork_path).convert("RGBA")

        src_coords = [(0, 0), (artwork.width, 0), (artwork.width, artwork.height), (0, artwork.height)]
        dst_coords = coords

        if len(dst_coords) != 4:
            raise ValueError("Template coordinates must contain exactly 4 points.")

        coeffs = find_perspective_transform(src_coords, dst_coords)
        transformed_artwork = artwork.transform(template.size, Image.PERSPECTIVE, coeffs, Image.BICUBIC)

        # Composite artwork beneath the template
        base = Image.new("RGBA", template.size, (0, 0, 0, 0))
        base.paste(transformed_artwork, (0, 0), transformed_artwork)
        base.paste(template, (0, 0), template)
        base.convert("RGB").save(output_path, "JPEG", quality=95)

    except Exception as e:
        raise RuntimeError(f"Error generating mockup: {e}")

def find_perspective_transform(src, dst):
    from numpy import array, linalg

    matrix = []
    for p1, p2 in zip(dst, src):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0]*p1[0], -p2[0]*p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1]*p1[0], -p2[1]*p1[1]])
    A = array(matrix)
    B = array(src).reshape(8)
    res = linalg.lstsq(A, B, rcond=None)[0]
    return res.tolist()
