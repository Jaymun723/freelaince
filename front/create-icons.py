#!/usr/bin/env python3
from PIL import Image, ImageDraw
import os

def create_icon(size, filename):
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a simple chat bubble icon
    # Main bubble
    bubble_color = (66, 153, 225, 255)  # Blue color
    margin = size // 8
    
    # Main circle
    draw.ellipse([margin, margin, size - margin, size - margin - size//6], 
                 fill=bubble_color)
    
    # Small tail
    tail_points = [
        (size//2 - size//8, size - margin - size//6),
        (size//2 - size//12, size - margin),
        (size//2 + size//12, size - margin - size//8)
    ]
    draw.polygon(tail_points, fill=bubble_color)
    
    # Save the image
    img.save(filename, 'PNG')
    print(f"Created {filename}")

# Create icons in different sizes
create_icon(16, 'icon16.png')
create_icon(48, 'icon48.png')
create_icon(128, 'icon128.png')

print("All icons created successfully!")