# Havvarsel Brand Assets for Home Assistant

This folder contains the brand assets for the Havvarsel integration, prepared according to [Home Assistant Brands Guidelines](https://github.com/home-assistant/brands).

## Files Included

- `icon.svg` - Square icon (256x256) for light mode
- `dark_icon.svg` - Square icon (256x256) for dark mode
- `logo.svg` - Horizontal logo (256x128) for light mode (optional)
- `dark_logo.svg` - Horizontal logo (256x128) for dark mode (optional)

## Converting to PNG for Submission

The Home Assistant brands repository requires PNG files. You can convert the SVGs using various tools:

### Option 1: Using Inkscape (Recommended)

```bash
# Light mode icon (256x256)
inkscape icon.svg --export-type=png --export-width=256 --export-height=256 --export-filename=icon.png

# Dark mode icon (256x256)
inkscape dark_icon.svg --export-type=png --export-width=256 --export-height=256 --export-filename=dark_icon.png

# Light mode logo (256x128) - if using
inkscape logo.svg --export-type=png --export-width=256 --export-height=128 --export-filename=logo.png

# Dark mode logo (256x128) - if using
inkscape dark_logo.svg --export-type=png --export-width=256 --export-height=128 --export-filename=dark_logo.png
```

### Option 2: Using ImageMagick

```bash
# Light mode icon
convert -background none -density 300 icon.svg -resize 256x256 icon.png

# Dark mode icon
convert -background none -density 300 dark_icon.svg -resize 256x256 dark_icon.png

# Light mode logo (if using)
convert -background none -density 300 logo.svg -resize 256x128 logo.png

# Dark mode logo (if using)
convert -background none -density 300 dark_logo.svg -resize 256x128 dark_logo.png
```

### Option 3: Online Converter

Use an online SVG to PNG converter like:
- https://cloudconvert.com/svg-to-png
- https://svgtopng.com/

**Settings:**
- Width: 256px (icon and dark icon) or 256px (logo)
- Height: 256px (icon and dark icon) or 128px (logo)
- Maintain transparency

## Optimizing PNGs

After conversion, optimize the PNG files to reduce file size:

```bash
# Using optipng
optipng -o7 icon.png dark_icon.png logo.png dark_logo.png

# Using pngquant (for even smaller files)
pngquant --quality=85-95 --ext .png --force icon.png dark_icon.png logo.png dark_logo.png
```

## Submitting to Home Assistant Brands

1. **Fork the repository**: https://github.com/home-assistant/brands

2. **Create the folder structure**:
   ```
   brands/
   └── custom_integrations/
       └── havvarsel/
           ├── icon.png (required)
           ├── dark_icon.png (optional, for dark mode)
           ├── logo.png (optional)
           └── dark_logo.png (optional, for dark mode)
   ```

3. **Copy your PNG files** to the appropriate folder

4. **Verify requirements**:
   - ✅ `icon.png` is 256x256px with transparent background
   - ✅ `dark_icon.png` is 256x256px with transparent background (if included)
   - ✅ `logo.png` is 256x128px with transparent background (if included)
   - ✅ `dark_logo.png` is 256x128px with transparent background (if included)
   - ✅ All PNGs are optimized (preferably under 10KB each)

5. **Create a Pull Request** with the title: `Add Havvarsel integration logos`

## Design Notes

- **Primary Color**: #05134d (Dark Navy - light mode background)
- **Secondary Color**: #033cbd (Blue - light mode waves)
- **Accent Color**: #2d6dff (Light Blue - light mode top wave)
- **Dark Mode Background**: #1a2332 (Darker slate)
- **Dark Mode Waves**: #4a7fff (Bright blue) and #7da4ff (Lighter blue)
- **Icon**: Features the "H" letter representing Havvarsel with wave patterns symbolizing ocean/sea conditions
- **Dark Mode**: Uses darker background with brighter blue accents for better visibility on dark interfaces

## Python Conversion Script (Alternative)

If you have Python with Inkscape installed, you can use this script to batch convert:

```python
import subprocess
from pathlib import Path

files = [
    ("icon.svg", "icon.png", 256, 256),
    ("dark_icon.svg", "dark_icon.png", 256, 256),
    ("logo.svg", "logo.png", 256, 128),
    ("dark_logo.svg", "dark_logo.png", 256, 128),
]

for svg, png, width, height in files:
    cmd = f'inkscape {svg} --export-type=png --export-width={width} --export-height={height} --export-filename={png}'
    subprocess.run(cmd, shell=True)
    print(f"✓ Created {png}")
```

**Note**: PNG conversion requires external tools (Inkscape, ImageMagick, etc.) as Python libraries for SVG→PNG conversion require system dependencies not available on all systems.

## Testing

Before submitting, test the icons in Home Assistant:

1. Place the PNG files in `custom_components/havvarsel/`
2. Restart Home Assistant
3. Check the integration page to see how the icon appears
4. Test both light and dark themes

## License

These brand assets follow the same license as the Havvarsel integration.
