# Quick Start Guide

## For Users

### Step 1: Install the Integration

**Option A: HACS (Recommended)**
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click ⋮ (three dots) → "Custom repositories"
4. Add: `https://github.com/jm-cook/ha-havvarsel-custom-integration`
5. Category: "Integration"
6. Search for "Havvarsel" and download
7. Restart Home Assistant

**Option B: Manual**
1. Copy `custom_components/havvarsel` to your `config/custom_components/` folder
2. Restart Home Assistant

### Step 2: Add Your First Sensor

1. Go to: **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Havvarsel"
4. Fill in the form:
   - **Sensor Name**: e.g., "Nordnes Sea Temperature"
   - **Longitude**: e.g., `5.302337`
   - **Latitude**: e.g., `60.398942`
   - **Depth**: `0` (for surface) or other depth in meters
5. Click **Submit**

### Step 3: View Your Sensor

Your sensor will appear as:
- Entity: `sensor.nordnes_sea_temperature` (based on your name)
- State: Current temperature in °C
- Attributes: Forecast data, coordinates, timestamp

## For Developers

### Testing Your Changes

```bash
# 1. Make changes to the code
# 2. Copy to Home Assistant
cp -r custom_components/havvarsel /path/to/homeassistant/config/custom_components/

# 3. Restart Home Assistant
# 4. Check logs
tail -f /path/to/homeassistant/home-assistant.log | grep havvarsel
```

### Enable Debug Logging

Add to `configuration.yaml`:
```yaml
logger:
  default: info
  logs:
    custom_components.havvarsel: debug
```

### Project Structure
```
custom_components/havvarsel/
├── __init__.py          # Entry point
├── api.py              # API client
├── config_flow.py      # UI configuration
├── const.py            # Constants
├── coordinator.py      # Data updates
├── manifest.json       # Metadata
├── sensor.py           # Sensor entity
├── strings.json        # UI strings
└── translations/       # Localizations
    └── en.json
```

## Example Dashboard Card

### Basic Temperature Display
```yaml
type: sensor
entity: sensor.nordnes_sea_temperature
graph: line
detail: 1
```

### Temperature Forecast Chart (requires ApexCharts)
```yaml
type: custom:apexcharts-card
graph_span: 72h
header:
  show: true
  title: Sea Temperature Forecast
series:
  - entity: sensor.nordnes_sea_temperature
    name: Temperature
    data_generator: |
      return entity.attributes.forecast.map((entry) => {
        return [new Date(entry.timestamp).getTime(), entry.temperature];
      });
```

### Map with Multiple Sensors
```yaml
type: map
entities:
  - entity: sensor.nordnes_sea_temperature
  - entity: sensor.another_location
default_zoom: 12
```

## Common Issues

### "Integration not found"
- Ensure folder is named exactly `havvarsel`
- Check it's in `custom_components/havvarsel/`
- Restart Home Assistant

### "Cannot connect"
- Verify coordinates are valid
- Check internet connection
- Ensure coordinates are near Norwegian coast

### Sensor shows "Unavailable"
- Wait 10 minutes for first update
- Check Home Assistant logs
- Verify API is accessible

## Next Steps

- Add multiple sensors for different locations
- Create beautiful dashboards with forecast charts
- Set up automations based on temperature
- Share your configuration with the community!

## Need Help?

- 📖 Full Documentation: [README.md](README.md)
- 🔄 Migration Guide: [MIGRATION.md](MIGRATION.md)
- 🐛 Report Issues: [GitHub Issues](https://github.com/jm-cook/ha-havvarsel-custom-integration/issues)
