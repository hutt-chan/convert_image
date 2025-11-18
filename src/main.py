from PIL import Image
from utils import load_image, save_image, pixels_to_image
from sketch_effects import sketch_effect, cartoon_effect

def apply_effect(img_or_path, path_out=None, effect='sketch', params=None):
    if params is None:
        params = {}

    # Hỗ trợ cả path và Image object
    if isinstance(img_or_path, Image.Image):
        img = img_or_path
    else:
        img = load_image(img_or_path)

    if effect == 'sketch':
        out_img = sketch_effect(img,
                               edge_strength=params.get('edge_strength', 1.2),
                               blur_radius=params.get('blur_radius', 2),
                               threshold_val=params.get('threshold_val', 100),
                               sigma_r=params.get('sigma_r', 50.0))
    elif effect == 'cartoon':
        out_img = cartoon_effect(img,
                                 blur_radius=params.get('blur_radius', 2),
                                 posterize_levels=params.get('posterize_levels', 6),
                                 edge_thresh=params.get('edge_thresh', 60),
                                 edge_strength=params.get('edge_strength', 1.2))
    else:
        raise ValueError('Unknown effect')

    if path_out:
        save_image(out_img, path_out)

    return out_img        # luôn trả về PIL.Image