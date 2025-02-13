import appdaemon.plugins.hass.hassapi as hass
from string import Template
from datetime import datetime, timedelta
from datetime import UTC as dtUTC
import requests
from mqtt_sensor_utils import MQTTSensorUtils

def sortByTimestamp(item):
    return item["timestamp"]

class HavvarselRest(hass.Hass):
    havvarsel_base_url="https://api.havvarsel.no/apis/duapi/havvarsel/v2/"
    havvarsel_projection_url=f"{havvarsel_base_url}temperatureprojection"
    havvarsel_variables_url=f"{havvarsel_base_url}variables"

    projectionTemplate = "$url/$lon/$lat?depth=$depth"
    service_data ={"method": "GET", "headers": {"User-agent": "Home Assistant", "Content-type": "application/xml"}}

    def initialize(self):
        rest_url_template = Template(HavvarselRest.projectionTemplate)
        self.module = self.args.get('module')
        self.device_id = self.args.get('device', 'Havvarsel')
        self.manufacturer = self.args.get('manufacturer', '<unknown>')
        self.longitude = self.args.get('longitude', 5.303883)
        self.latitude = self.args.get('latitude', 60.400485)
        self.depth = self.args.get('depth', 0)
        self.sensor_name = self.args.get('sensor_name', 'unnamed')
        self.slug_name = self.sensor_name.replace(' ', '_')
        self.unit_of_measurement = self.args.get('unit_of_measurement', None)
        self.local_tz = datetime.now().astimezone().tzinfo

        self.service_url = rest_url_template.substitute(
                url= HavvarselRest.havvarsel_projection_url, 
                lon=self.longitude, 
                lat=self.latitude, 
                depth=self.depth
            )
            
        self.run_every(self.poll_havvarsel, datetime.now()+timedelta(seconds=5), 600)
        self.log(
            f"\n{self.args.get('class')} initialized:\n"
            f"    name: {self.name.capitalize().replace(' ', '_')}\n"
            f"    device_id: {self.device_id}\n"
            f"    manufacturer: {self.manufacturer}\n"
            f"    longitude: {self.longitude}\n"
            f"    latitude: {self.latitude}\n"
            f"    depth: {self.depth}\n"
            f"    sensor_name (slug): {self.slug_name}\n"
            f"    unit_of_measurement: {self.get_units()}\n",
            ascii_encode=False
            )
        units=self.get_units()
        self.sensor_utils = MQTTSensorUtils(self)
        self.sensor_utils.create_sensor(
            self.device_id,
            self.slug_name,
            self.slug_name.capitalize(), 
                {
                     "device_class":"TEMPERATURE", 
                     "state_class":"MEASUREMENT",
                     "manufacturer":self.manufacturer,
                     "units":units
                }
            ) 
        
    def get_units(self):
        # Scan Variables for temperature units
        if self.unit_of_measurement:
            units = self.unit_of_measurement
        else:
            service_data ={"method": "GET", "headers": {"User-agent": "Home Assistant", "Content-type": "application/xml"}}
            response = requests.get(HavvarselRest.havvarsel_variables_url, headers = service_data.get('headers') )
            value_json =response.json()
            variables = value_json['row']
            metadata_temperature = next((sub for sub in variables if sub['variableName'] == "temperature"), None).get('metadata')
            units_dict = next((sub for sub in metadata_temperature if sub['key'] == "units"), None)
            units = units_dict['value']
        return units
        
    def poll_havvarsel(self, kwargs=None):
        self.log(f"HavvarselRest {datetime.now(self.local_tz).isoformat()}", level="DEBUG")

        headers = {'Content-Type': 'application/xml'}
        response = requests.get(self.service_url, headers=headers)
        value_json = response.json()
        data = value_json['variables'][0]['data']
        
        # Find projected temperature nearest to current UTC time.
        n = datetime.now(dtUTC).timestamp()*1000
        nearest = min(data, key=lambda x:abs(x["rawTime"] - n))
        ts = nearest.get('rawTime')/1000
        nearestTime = datetime.fromtimestamp(ts, self.local_tz).isoformat()
        currentTemp = nearest.get("value")
        
        self.log(f"poll_havvarsel nearest timestamp: {nearestTime}", level="DEBUG")
        self.log(f"poll_havvarsel nearest value: {currentTemp}", level="DEBUG")

        # Gather temperature forecast to pass up to HA
        # Timestamps in ISO format
        forecast =[]
        for projection in data:
            dt = datetime.fromtimestamp(projection.get('rawTime')/1000, self.local_tz)
            d = dt.isoformat()
            forecast.append({"timestamp": d, "temperature": projection.get('value')})
        if len(forecast) >= 1:
            forecast.sort(reverse=False, key=sortByTimestamp)
        
        closest = value_json.get('closestGridPointWithData', {'lat': self.latitude, 'lon': self.longitude})
        self.log(f"poll_havvarsel nearest grid point: {closest}", level = "DEBUG")

        attributes = {
            'longitude' : self.longitude,
            'latitude' : self.latitude,
            'nearest_grid_lon' : closest.get('lon'),
            'nearest_grid_lat' : closest.get('lat'),
            'timestamp' : nearestTime,
            'forecast' : forecast
        }
        self.sensor_utils.update_sensor(self.slug_name, currentTemp, attributes)

