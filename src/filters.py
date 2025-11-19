# src/filters.py
from math import exp, sqrt

def to_grayscale(pixels):
    """Simple luminance grayscale"""
    return [int(0.299*r + 0.587*g + 0.114*b) for (r,g,b) in pixels]

def invert_grayscale(gray_pixels):
    return [255 - v for v in gray_pixels]

def bilateral_blur_gray(gray_pixels, w, h, radius=2, sigma_d=3.0, sigma_r=50.0):
    out = [0] * (w * h)

    # Precompute spatial weights
    spatial = []
    for dy in range(-radius, radius+1):
        row = []
        for dx in range(-radius, radius+1):
            dist_sq = dx*dx + dy*dy
            row.append(exp(-dist_sq / (2.0 * sigma_d * sigma_d)))
        spatial.append(row)

    for y in range(h):
        for x in range(w):
            center_val = gray_pixels[y * w + x]
            total_weight = 0.0
            weighted_sum = 0.0
            for dy in range(-radius, radius + 1):
                yy = y + dy
                if yy < 0 or yy >= h: continue
                for dx in range(-radius, radius + 1):
                    xx = x + dx
                    if xx < 0 or xx >= w: continue
                    pixel_val = gray_pixels[yy * w + xx]
                    weight_spatial = spatial[dy+radius][dx+radius]
                    intensity_diff = pixel_val - center_val
                    weight_intensity = exp(-intensity_diff*intensity_diff / (2.0 * sigma_r * sigma_r))
                    weight = weight_spatial * weight_intensity
                    weighted_sum += pixel_val * weight
                    total_weight += weight
            out[y * w + x] = int(weighted_sum / total_weight + 0.5)
    return out

def gaussian_blur_gray(gray_pixels, w, h, radius=2, sigma_d=3.0):
    out = [0] * (w * h)
    for y in range(h):
        for x in range(w):
            total_weight = 0.0
            weighted_sum = 0.0
            for dy in range(-radius, radius + 1):
                yy = y + dy
                if yy < 0 or yy >= h: continue
                for dx in range(-radius, radius + 1):
                    xx = x + dx
                    if xx < 0 or xx >= w: continue
                    pixel_val = gray_pixels[yy * w + xx]
                    dist_sq = dx*dx + dy*dy
                    weight = exp(-dist_sq / (2.0 * sigma_d * sigma_d))
                    weighted_sum += pixel_val * weight
                    total_weight += weight
            out[y * w + x] = int(weighted_sum / total_weight + 0.5) if total_weight > 0 else gray_pixels[y * w + x]
    return out

def get_padded_pixel(gray_pixels, w, h, x, y):
    # Replicate padding: Clamp coordinates
    xx = max(0, min(w-1, x))
    yy = max(0, min(h-1, y))
    return gray_pixels[yy * w + xx]

def sobel_edges(gray_pixels, w, h, strength=1.0):
    out = [0] * (w * h)
    gx_k = [[-1,0,1], [-2,0,2], [-1,0,1]]
    gy_k = [[1,2,1], [0,0,0], [-1,-2,-1]]
    for y in range(h):
        for x in range(w):
            gx = gy = 0
            for ky in range(-1, 2):
                for kx in range(-1, 2):
                    p = get_padded_pixel(gray_pixels, w, h, x + kx, y + ky)
                    gx += p * gx_k[ky+1][kx+1]
                    gy += p * gy_k[ky+1][kx+1]
            mag = int(sqrt(gx*gx + gy*gy) * strength)
            out[y * w + x] = max(0, min(255, mag))
    return out

def dog_edges(gray, w, h, r1=1, r2=2):
    g1 = gaussian_blur_gray(gray, w, h, radius=r1, sigma_d=r1)
    g2 = gaussian_blur_gray(gray, w, h, radius=r2, sigma_d=r2)
    return [min(255, abs(a-b)*2) for a,b in zip(g1, g2)]

def otsu_threshold(gray):
    hist = [0]*256
    for v in gray: hist[v] += 1
    total = len(gray)

    sum_total = sum(i*hist[i] for i in range(256))
    sumB = 0
    wB = 0
    max_var = 0
    best_t = 128

    for t in range(256):
        wB += hist[t]
        if wB == 0: continue
        wF = total - wB
        if wF == 0: break

        sumB += t*hist[t]
        mB = sumB / wB
        mF = (sum_total - sumB) / wF

        var = wB * wF * (mB - mF) ** 2
        if var > max_var:
            max_var = var
            best_t = t

    return [255 if v >= best_t else 0 for v in gray]

def median3(a, b, c):
    return sorted([a, b, c])[1]

def posterize_color(pixels, levels):
    if levels < 2: levels = 2
    step = 255 // (levels - 1)
    out = []
    for (r,g,b) in pixels:
        rr = (r // step) * step
        gg = (g // step) * step
        bb = (b // step) * step
        rr = median3(rr, r, min(255, rr + step))
        gg = median3(gg, g, min(255, gg + step))
        bb = median3(bb, b, min(255, bb + step))
        out.append((max(0,min(255,rr)), max(0,min(255,gg)), max(0,min(255,bb))))
    return out

def edge_mask_to_rgb(edge_gray, original_pixels):
    # blend edges (black) over original (simulate sketch)
    out = []
    for e,(r,g,b) in zip(edge_gray, original_pixels):
        if e > 40: # edge presence
            out.append((0,0,0))
        else:
            out.append((r,g,b))
    return out