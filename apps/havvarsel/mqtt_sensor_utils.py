from string import Template
import json

class MQTTSensorUtils():
    configTemplate = ("{ "
                  "\"name\": \"$name\", "
                  "\"device_class\" : \"$device_class\", "
                  "\"state_class\": \"$state_class\", "
                  "\"state_topic\": \"$state_topic\", "
                  "\"unique_id\": \"$unique_id\", "
                  "\"unit_of_measurement\": \"$unit\", "
                  "\"device\":{"
                    "\"identifiers\": [ \"$id\" ], "
                    "\"name\": \"$device_name\","
                    "\"manufacturer\": \"$manufacturer\" "
                  "},  "
                  "\"json_attributes_topic\": \"$state_topic/attr$name\", "
                  "\"json_attributes_template\": \"{{ value_json.attr | tojson }}\" "
                  "} ")
                  
    def __init__(self, hassobj):
        self.hassobj=hassobj
    
    def create_sensor(self, device, id, name, kwargs=None):
        template = Template(MQTTSensorUtils.configTemplate)
        config_topic = f"homeassistant/sensor/{name}/config"
        if kwargs:
            device_class = kwargs.get('device_class', None)
            state_class = kwargs.get('state_class', None)
            manufacturer = kwargs.get('manufacturer', None)
            units = kwargs.get('units', None)
        else:
            device_class=""
            manufacturer=""
            units=""
            state_class=""

        cfg_str = template.substitute(
            name=name,
            device_class=device_class,
            state_class=state_class,
            state_topic=f"homeassistant/sensor/{name}/state",
            unique_id=id,
            unit=units,
            id=device,
            device_name=device,
            manufacturer=manufacturer
        )
        self.hassobj.log(f"publishing to {config_topic} : {cfg_str}", level="DEBUG")
        # self.call_service("mqtt/publish", topic=config_topic, payload=cfg_str, retain=True, qos=2)
        self.hassobj.call_service("mqtt/publish", topic=config_topic, payload=cfg_str, retain=True, qos=2)
    
    def update_sensor(self, name, value, attr):
        payload = value
        state_topic = f"homeassistant/sensor/{name}/state"
        self.hassobj.log(f"publishing to {state_topic} : {payload}", level="DEBUG")
        self.hassobj.call_service("mqtt/publish", topic=state_topic, payload=payload, retain=True, qos=2)
        
        if attr:
          attr_str = '{{ \"attr\": {attr} }}'.format(attr=json.dumps(attr))
          attr_topic = f"homeassistant/sensor/{name}/state/attr{name}"
          self.hassobj.call_service("mqtt/publish", topic=attr_topic, payload=attr_str, retain=True, qos=2)