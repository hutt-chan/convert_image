# src/sketch_effects.py
from utils import pixels_to_image
from filters import (to_grayscale, bilateral_blur_gray, gaussian_blur_gray, sobel_edges,
                    otsu_threshold, invert_grayscale, posterize_color, dog_edges)

def sketch_effect(img, edge_strength=1.2, blur_radius=2, sigma_r=50.0, filter_type='bilateral'):
    w, h = img.size
    pixels = list(img.getdata())
    gray = to_grayscale(pixels)
    # Giảm nhiễu trước Sobel
    gray = gaussian_blur_gray(gray, w, h, radius=1, sigma_d=1.0)
    if filter_type == 'bilateral':
        blurred = bilateral_blur_gray(gray, w, h, radius=blur_radius, sigma_r=sigma_r)
    elif filter_type == 'gaussian':
        blurred = gaussian_blur_gray(gray, w, h, radius=blur_radius, sigma_d=blur_radius * 1.5)
    else:
        raise ValueError('Unknown filter type')
    edges = sobel_edges(blurred, w, h, strength=edge_strength)
    inv = invert_grayscale(edges)
    th = otsu_threshold(inv)
    out_pixels = [(255,255,255) if v == 255 else (0,0,0) for v in th]
    return pixels_to_image(out_pixels, (w, h))

def cartoon_effect(img, blur_radius=2, posterize_levels=6, edge_thresh=60, edge_strength=1.2, sigma_r=50.0, filter_type='bilateral'):
    w, h = img.size
    pixels = list(img.getdata())
    gray = to_grayscale(pixels)
    # Giảm nhiễu trước DoG
    gray = gaussian_blur_gray(gray, w, h, radius=1, sigma_d=1.0)
    if filter_type == 'bilateral':
        blurred = bilateral_blur_gray(gray, w, h, radius=blur_radius, sigma_r=sigma_r)
    elif filter_type == 'gaussian':
        blurred = gaussian_blur_gray(gray, w, h, radius=blur_radius, sigma_d=blur_radius * 1.5)
    else:
        raise ValueError('Unknown filter type')
    edges = dog_edges(gray, w, h, r1=1, r2=2)
    poster = posterize_color(pixels, posterize_levels)
    edge_mask = [255 if e > edge_thresh else 0 for e in edges]
    out_pixels = [(0,0,0) if em == 255 else col for em, col in zip(edge_mask, poster)]
    return pixels_to_image(out_pixels, (w, h))