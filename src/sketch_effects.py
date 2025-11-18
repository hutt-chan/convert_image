# src/sketch_effects.py
from utils import pixels_to_image
from filters import (to_grayscale, bilateral_blur_gray, sobel_edges,
                    threshold, invert_grayscale, posterize_color)

def sketch_effect(img, edge_strength=1.2, blur_radius=2, threshold_val=100, sigma_r=50.0):
    w, h = img.size
    pixels = list(img.getdata())
    gray = to_grayscale(pixels)
    blurred = bilateral_blur_gray(gray, w, h, radius=blur_radius, sigma_r=sigma_r)
    edges = sobel_edges(blurred, w, h, strength=edge_strength)
    inv = invert_grayscale(edges)
    th = threshold(inv, threshold_val)
    out_pixels = [(255,255,255) if v == 255 else (0,0,0) for v in th]
    return pixels_to_image(out_pixels, (w, h))

def cartoon_effect(img, blur_radius=2, posterize_levels=6, edge_thresh=60, edge_strength=1.2):
    w, h = img.size
    pixels = list(img.getdata())
    gray = to_grayscale(pixels)
    blurred = bilateral_blur_gray(gray, w, h, radius=blur_radius, sigma_r=50.0)
    edges = sobel_edges(blurred, w, h, strength=edge_strength)
    poster = posterize_color(pixels, posterize_levels)
    edge_mask = [255 if e > edge_thresh else 0 for e in edges]
    out_pixels = [(0,0,0) if em == 255 else col for em, col in zip(edge_mask, poster)]
    return pixels_to_image(out_pixels, (w, h))