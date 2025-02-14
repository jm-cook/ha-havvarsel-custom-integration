Navigate to: [My smart home](https://github.com/jm-cook/my-smart-home/tree/main)
# HA Havvarsel
HA Havvarsel is an AppDaemon app which will provide current sea temperature model data and prognosis from the Norwegian Institute for Marine Research 
(Havforskningsinstituttet).

This standalone python app for AppDaemon will create a sensor for the sea temperature at 
the specified location. 
To use it you will use the Home Assistant addons appdaemon and mqtt and install this python app
for appdaemon. This method may initially seem 
complicated but installation *should* be straightforward and the solution gives the best results out of all the methods that I tried.

## Installation

To install the codes you must follow these steps:

1. install the mosquitto broker add on for home assistant. To do this go to the add-ons configuration section and select the mosquitto broker from the list of official addons.

   [![Open your Home Assistant instance and show the add-on store.](https://my.home-assistant.io/badges/supervisor_store.svg)](https://my.home-assistant.io/redirect/supervisor_store/)
TEST:
 <a href="https://my.home-assistant.io/redirect/supervisor_store/" target="_BLANK" foo="bar">LINK</a>


   Install mosquitto and configure it.

3. You will need the MQTT integration from the integrations page:
   
   [![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mqtt)

4. Now install the appdaemon addon which is available form the addon store.

   [![Open your Home Assistant instance and show the add-on store.](https://my.home-assistant.io/badges/supervisor_store.svg)](https://my.home-assistant.io/redirect/supervisor_store/)

-----------------------------------------
The script "havvarsel.py" is an app for AppDaemon that periodically fetches the current sea temperature
for the specified location. A sensor is created by posting to a *create* topic on the MQTT server. The data is updated 
by posting to a topic that was specified in the *create* payload. The payloads are constructed so that your Home Assistant
instance will auto-discover the sensor, and it will be available for display.

Copy the files in the folder ```apps/havvarsel``` to your appdaemon app folder. It will probably be in something like: ```/addon_configs/a0d7b954_appdaemon/apps```, you can copy the whole folder and contents
You will need to upload the file yourself, or copy/paste using an editor.

Then configure the app in the ```apps.yml``` file located in the AppDaemon apps folder. Similar to the following:

```yaml
havvarsel_nordnes:
  module: havvarsel
  class: HavvarselRest
  log_level: INFO
  device: Havvarsel
  manufacturer: IMR, Norway
  longitude: 5.302337
  latitude: 60.398942
  sensor_name: Nordnes sea temperature
  unit_of_measurement: °C
```

 - ```module```, and ```class``` are mandatory and must be written as shown
 - ```log_level``` can be INFO or DEBUG and is optional
 - ```device``` is the name your HA device wil get
 - ```manufacturer``` is optional and displayed for the device to show the data provider
 - ```longitude``` and ```latitude``` are the location on the Norwegian coast where you want the forecast from
 - ```sensor_name``` will be the name of the sensor in your instance
 - ```unit_of_measurement``` is optional and overrides the units provided by the underlying rest service.
 
 When you save the ```app.yaml``` file in your configuration, AppDaemon will start the havvarsel app. You can add several configurations 
 for different locations if you want more sensors.

For example to add a new location include the following, or similar, in addition to the above configuration:

```yaml
havvarsel_kyrketangen:
  module: havvarsel
  class: HavvarselRest
  log_level: INFO
  device: Havvarsel
  manufacturer: IMR, Norway
  longitude: 5.302686
  latitude: 60.324667
  sensor_name: Kyrketangen sea temperature
  unit_of_measurement: °C
```

Note that the app script specifies that MQTT topics should be retained. This is to ensure continuity between restarts
of HA (otherwise the sensors become unavailable). MQTT retention can be tricky, and if something goes wrong, or you want to remove a line/sensor, then 
it will most likely be retained. This may mean that old line sensors are still available after you have 
removed them from the configuration. There is currently no automatic purge to remove previous configurations (but see below).

## Use

The sensors created show the forecasted temperature at each location. The sensor includes the position of the 
forecast, which means they can also be shown in HA on a map. The sensor includes the whole forecast 
as an attribute giving the possibility to plot the forecast. 

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
            entity: sensor.havvarsel_nordnes_sea_temperature
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
                  - entity: sensor.havvarsel_nordnes_sea_temperature
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
              - entity: sensor.havvarsel_nordnes_sea_temperature
              - entity: sensor.havvarsel_kyrketangen_sea_temperature
            theme_mode: auto
            grid_options:
              columns: full
              rows: 8
```

------------------------------------------
If you should use a configuration that created a  sensor that you no longer need, the sensor will continue to exist even if you remove it from the configuration. This is due to
message retention in the mosquitto broker. The current method to remove unwanted sensor is to access the mosquitto broker using MQTT Explorer (take a look here https://community.home-assistant.io/t/addon-mqtt-explorer-new-version/603739). If you connect MQTT Explorer to your broker, you can delete the unwanted topics there:

![image](img/mqtt_explorer.png)
