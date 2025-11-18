from PIL import Image

def load_image(path):
    return Image.open(path).convert('RGB')

def save_image(img, path):
    img.save(path)

def pixels_to_image(pixels, size):
    """pixels: iterable của (r,g,b), size: (w,h)"""
    img = Image.new('RGB', size)
    img.putdata([tuple(map(int, p)) for p in pixels])
    return img