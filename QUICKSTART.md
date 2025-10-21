# Quick Start Guide

## For Users

### Step 1: Install the Integration

**Option A: HACS (Recommended)**
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click ⋮ (three dots) → "Custom repositories"
4. Add: `https://github.com/jm-cook/ha-havvarsel`
5. Category: "Integration"
6. Search for "Havvarsel" and download
7. Restart Home Assistant

**Option B: Manual**
1. Copy `custom_components/havvarsel` to your `config/custom_components/` folder
2. Restart Home Assistant

### Step 2: Add Your First Location

1. Go to: **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Havvarsel"
4. Fill in the form:
   - **Sensor Name**: e.g., "Home" (this names your location)
   - **Longitude**: e.g., `5.302337`
   - **Latitude**: e.g., `60.398942`
   - **Depth**: `0` (for surface) or other depth in meters
5. Click **Submit**

The integration will create 13 sensors for different oceanographic variables. Only the temperature sensor is enabled by default.

### Step 3: View Your Sensors

Your sensors will appear as:
- Entity: `sensor.havvarsel_home_sea_water_potential_temperature`
- State: Current value (e.g., temperature in °C)
- Attributes: 
  - `series`: Time series data with `timestamp` and `value` pairs
  - `metadata`: Variable information (units, standard names, etc.)
  - `longitude`, `latitude`: Your requested location
  - `nearest_grid`: Actual grid point used by the API

### Step 4: Enable Additional Sensors (Optional)

1. Go to: **Settings** → **Devices & Services** → **Havvarsel**
2. Click on your location device
3. Enable the sensors you want (salinity, currents, wave height, etc.)

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
entity: sensor.havvarsel_home_sea_water_potential_temperature
graph: line
detail: 1
```

### Temperature Time Series Chart (requires ApexCharts)
```yaml
type: custom:apexcharts-card
graph_span: 72h
span:
  offset: +60h
now:
  show: true
  label: Now
header:
  show: true
  show_states: true
apex_config:
  stroke:
    curve: smooth
yaxis:
  - id: temp
    decimals: 1
series:
  - entity: sensor.havvarsel_home_sea_water_potential_temperature
    yaxis_id: temp
    name: Temperature
    data_generator: |
      return entity.attributes.series.map((entry) => {
        return [new Date(entry.timestamp).getTime(), entry.value];
      });
  - entity: sensor.havvarsel_home_sea_water_potential_temperature
    yaxis_id: temp
    name: Trend (24h avg)
    group_by:
      duration: 24h
      func: avg
    data_generator: |
      return entity.attributes.series.map((entry) => {
        return [new Date(entry.timestamp).getTime(), entry.value];
      });
```

### Map with Sensors
```yaml
type: map
entities:
  - entity: sensor.havvarsel_home_sea_water_potential_temperature
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
- Ensure at least one sensor is enabled for the location

### Want more variables?
- Go to **Settings** → **Devices & Services** → **Havvarsel**
- Click on your location device
- Enable additional sensors (salinity, currents, waves, etc.)

## Next Steps

- Add multiple locations with different names
- Enable additional oceanographic variables (salinity, currents, waves)
- Create beautiful dashboards with time series charts
- Set up automations based on temperature or other variables
- Share your configuration with the community!

## Need Help?

- 📖 Full Documentation: [README.md](README.md)
- 🔄 Migration Guide: [MIGRATION.md](MIGRATION.md)
- 🐛 Report Issues: [GitHub Issues](https://github.com/jm-cook/ha-havvarsel/issues)
