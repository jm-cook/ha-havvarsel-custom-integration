# Quick Start: Converting SVG to PNG

## Required Files for Home Assistant Brands

You need to convert these SVG files to PNG format:

1. **icon.svg** → **icon.png** (256x256px)
2. **icon@2x.svg** → **icon@2x.png** (256x256px) - for dark mode
3. **logo.svg** → **logo.png** (256x128px) - optional

## Easiest Method: Using Online Converter

1. Go to https://svgtopng.com/ or https://cloudconvert.com/svg-to-png

2. Upload each SVG file one at a time

3. Set the dimensions:
   - For **icon.svg** and **icon@2x.svg**: 256 x 256 pixels
   - For **logo.svg**: 256 x 128 pixels

4. Make sure "Transparent background" is enabled

5. Download the converted PNG files

6. Rename them:
   - `icon.svg` → `icon.png`
   - `icon@2x.svg` → `icon@2x.png`
   - `logo.svg` → `logo.png`

## Using PowerShell (Windows) with ImageMagick

If you have ImageMagick installed:

```powershell
cd brands\havvarsel

# Convert icon
magick convert -background none -density 300 icon.svg -resize 256x256 icon.png

# Convert dark mode icon
magick convert -background none -density 300 "icon@2x.svg" -resize 256x256 "icon@2x.png"

# Convert logo
magick convert -background none -density 300 logo.svg -resize 256x128 logo.png
```

## Verify Your PNGs

Check that your PNG files:
- ✅ Have transparent backgrounds (not white)
- ✅ Are the correct dimensions (256x256 or 256x128)
- ✅ Are under 50KB each (preferably under 10KB)
- ✅ Look crisp and clear

## Submit to Home Assistant

Once you have the PNG files:

1. Fork: https://github.com/home-assistant/brands
2. Create folder: `brands/custom_integrations/havvarsel/`
3. Copy PNG files to that folder
4. Create Pull Request with title: "Add Havvarsel integration logos"

That's it! 🎉
