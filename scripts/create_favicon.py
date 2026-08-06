#!/usr/bin/env python3
"""Generate Cymbal Children's Hospital favicon.ico and favicon.svg assets."""
from pathlib import Path
import struct
import zlib

def create_png_32x32():
    width = 32
    height = 32
    
    # RGBA pixels for 32x32 Cymbal Hospital cross icon
    # Primary teal: (13, 148, 136, 255) #0d9488
    # Blue heart/cross center: (37, 99, 235, 255) #2563eb
    # Background: Transparent (0, 0, 0, 0)
    
    raw_pixels = bytearray()
    for y in range(height):
        raw_pixels.append(0)  # PNG filter byte 0 (None)
        for x in range(width):
            # Distance from center
            dx = abs(x - 15.5)
            dy = abs(y - 15.5)
            
            # Hospital Cross geometry (horizontal bar dy < 4, dx < 11; vertical bar dx < 4, dy < 11)
            is_cross = (dy < 4.5 and dx < 11.5) or (dx < 4.5 and dy < 11.5)
            # Center heart/accent (dx < 2.5 and dy < 2.5)
            is_center = (dx < 2.5 and dy < 2.5)
            
            # Rounded outer badge border
            is_badge = (dx*dx + dy*dy) <= (14.5 * 14.5)
            
            if is_badge:
                if is_center:
                    raw_pixels.extend([37, 99, 235, 255])  # Accent Blue
                elif is_cross:
                    raw_pixels.extend([255, 255, 255, 255])  # White Cross
                else:
                    raw_pixels.extend([13, 148, 136, 255])  # CCH Teal
            else:
                raw_pixels.extend([0, 0, 0, 0])  # Transparent
                
    # Build valid PNG bytes
    png_header = b"\x89PNG\r\n\x1a\n"
    
    # IHDR chunk
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    ihdr_crc = struct.pack(">I", zlib.crc32(b"IHDR" + ihdr_data) & 0xffffffff)
    ihdr_chunk = struct.pack(">I", len(ihdr_data)) + b"IHDR" + ihdr_data + ihdr_crc
    
    # IDAT chunk
    compressed_data = zlib.compress(bytes(raw_pixels))
    idat_crc = struct.pack(">I", zlib.crc32(b"IDAT" + compressed_data) & 0xffffffff)
    idat_chunk = struct.pack(">I", len(compressed_data)) + b"IDAT" + compressed_data + idat_crc
    
    # IEND chunk
    iend_crc = struct.pack(">I", zlib.crc32(b"IEND") & 0xffffffff)
    iend_chunk = struct.pack(">I", 0) + b"IEND" + iend_crc
    
    png_bytes = png_header + ihdr_chunk + idat_chunk + iend_chunk
    
    # ICO Wrapper header
    ico_header = struct.pack("<HHH", 0, 1, 1)  # Reserved, Type ICO, Count 1
    ico_dir = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(png_bytes), 22)
    
    return ico_header + ico_dir + png_bytes

def main():
    static_dir = Path(__file__).parent.parent / "app" / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Write favicon.ico
    ico_bytes = create_png_32x32()
    ico_path = static_dir / "favicon.ico"
    ico_path.write_bytes(ico_bytes)
    print(f"Created favicon.ico ({len(ico_bytes)} bytes) at {ico_path}")
    
    # Write SVG vector favicon
    svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="8" fill="#0d9488"/>
  <path d="M13 8h6v5h5v6h-5v5h-6v-5H8v-6h5V8z" fill="#ffffff"/>
  <circle cx="16" cy="16" r="2.5" fill="#2563eb"/>
</svg>"""
    svg_path = static_dir / "favicon.svg"
    svg_path.write_text(svg_content, encoding="utf-8")
    print(f"Created favicon.svg at {svg_path}")

if __name__ == "__main__":
    main()
