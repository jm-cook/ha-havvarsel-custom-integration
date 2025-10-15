Navigate to: [My smart home](https://github.com/jm-cook/my-smart-home/tree/main)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/jm-cook/ha-havvarsel-custom-integration)
[![Validate with HACS](https://github.com/jm-cook/ha-havvarsel-custom-integration/actions/workflows/validate.yaml/badge.svg)](https://github.com/jm-cook/ha-havvarsel-custom-integration/actions/workflows/validate.yaml)
[![GitHub Release](https://img.shields.io/github/release/jm-cook/ha-havvarsel-custom-integration.svg)](https://github.com/jm-cook/ha-havvarsel-custom-integration/releases)
![Project Maintenance](https://img.shields.io/maintenance/yes/2025.svg)

# HA Havvarsel Custom Integration
HA Havvarsel is a Home Assistant custom integration that provides current sea temperature model data and forecasts from the Norwegian Institute for Marine Research (Havforskningsinstituttet).

This custom integration creates sensors for sea temperature at specified locations along the Norwegian coast. It integrates directly with Home Assistant without requiring AppDaemon or MQTT.

## Installation

### Installation with HACS (Recommended)

1. Open HACS in your Home Assistant instance
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add the URL: `https://github.com/jm-cook/ha-havvarsel-custom-integration`
6. Select category: "Integration"
7. Click "Add"
8. Search for "Havvarsel" in HACS
9. Click "Download"
10. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/havvarsel` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

After installation, add the integration through the Home Assistant UI:

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Havvarsel"
4. Follow the configuration steps:
   - **Sensor Name**: A descriptive name for your sensor (e.g., "Nordnes Sea Temperature")
   - **Longitude**: The longitude of your desired location (e.g., 5.302337)
   - **Latitude**: The latitude of your desired location (e.g., 60.398942)
   - **Depth**: The depth in meters (default: 0 for surface temperature)

You can add multiple sensors for different locations by repeating the process.

## Use

The sensors created show the current temperature and forecast at each location. Each sensor includes:

- **Current temperature**: The sea temperature at the specified location and depth
- **Location data**: Coordinates of your location and the nearest grid point
- **Forecast data**: Temperature forecast as an attribute for plotting

The sensors can be displayed on maps and in various cards.

## Features

- 🌊 Current sea temperature at specified locations along the Norwegian coast
- 📊 Temperature forecast data stored as attributes
- 🗺️ Location information (your coordinates and nearest grid point)
- ♻️ Automatic updates every 10 minutes
- 🔄 Config flow UI for easy setup
- 📍 Support for multiple locations and depths

### Example view configuration

![example_view.png](img/example_view.png)

The example view shown here is configured using the yaml code below. To plot future 
values from the forecast attribute, the custom apex charts card must be installed (https://github.com/RomRider/apexcharts-card)

```yaml
views:
  - type: sections
    max_columns: 2
    title: Sea temperature demo
    path: sea-temperature-demo
    sections:
      - type: grid
        cards:
          - type: heading
            heading: Nordnes sjøbad
            heading_style: title
          - graph: line
            type: sensor
            entity: sensor.nordnes_sea_temperature
            detail: 1
            icon: mdi:swim
            grid_options:
              columns: full
            name: Current sea temperature Nordnes sjøbad
          - type: vertical-stack
            cards:
              - type: custom:apexcharts-card
                experimental:
                  disable_config_validation: true
                grid_options:
                  columns: full
                  rows: 4
                graph_span: 72h
                span:
                  offset: +60h
                now:
                  show: true
                  label: Now
                header:
                  show: true
                  show_states: true
                series:
                  - entity: sensor.nordnes_sea_temperature
                    name: Temperature forecast
                    stroke_width: 2
                    decimals: 2
                    show:
                      in_header: false
                      legend_value: false
                    data_generator: |
                      return entity.attributes.forecast.map((entry) => {
                        return [new Date(entry.timestamp).getTime(), entry.temperature];
                      });
      - type: grid
        cards:
          - type: heading
            heading: Map
            heading_style: title
          - type: map
            entities:
              - entity: sensor.nordnes_sea_temperature
              - entity: sensor.kyrketangen_sea_temperature
            theme_mode: auto
            grid_options:
              columns: full
              rows: 8
```

## Removing Sensors

To remove a sensor, simply delete the integration from **Settings** → **Devices & Services** → **Havvarsel** → (select the device) → **Delete**.
