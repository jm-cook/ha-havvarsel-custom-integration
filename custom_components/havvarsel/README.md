# Havvarsel Custom Integration for Home Assistant

This directory contains the Havvarsel custom integration.

## Structure

- `__init__.py` - Integration setup and entry point
- `manifest.json` - Integration metadata
- `const.py` - Constants and configuration
- `api.py` - API client for Havvarsel service
- `coordinator.py` - Data update coordinator
- `config_flow.py` - UI configuration flow
- `sensor.py` - Sensor platform implementation
- `strings.json` - UI strings
- `translations/` - Localization files

## Development

To test this integration:

1. Copy the `custom_components/havvarsel` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Add the integration through the UI: Settings → Devices & Services → Add Integration → Havvarsel

## API Reference

The integration uses the Havvarsel API from the Norwegian Institute for Marine Research:
- Base URL: https://api.havvarsel.no/apis/duapi/havvarsel/v2/
- Temperature projection: `/temperatureprojection/{lon}/{lat}?depth={depth}`
- Variables metadata: `/variables`

## Features

- Async API client with aiohttp
- DataUpdateCoordinator for efficient updates
- Config flow for UI-based setup
- Proper device and entity registry integration
- Forecast data as sensor attributes
