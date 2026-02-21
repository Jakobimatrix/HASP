from utilities.removeFromDB import removeMqttForDevice, deleteDevice
from db.device_data import updateDeviceId
from mqtt.client import subscribe
from db.mqtt import addTopic, addTopicSchema, getTopicsForDevice


def storeMqttInfo(device_id, mqtt_offers):
    """
    Expects a list of MQTT offers
    Each offer is a dict with the following format:
    {
        "topic": "<string>",     # must not contain '/'
        "endpoints": ["set", "state"],
        "keys": [
            {
                "key_name": "<string>",
                "value_type": "int|float|string|bool|enum",
                "min_value": <number>,    # optional, for int/float
                "max_value": <number>,    # optional, for int/float
                "enum_values": [<string>] # optional, for enum
            },
            ...
        ]
    }
    1. unsubscribe all current subscriptions to device_id
    2. remove database entries of old mqtt offers
    3. add new mqtt offerst to db
    4. subscribe to offers
    """
    removeMqttForDevice(device_id)

    for offer in mqtt_offers:
        topic_name = offer.get("topic")
        endpoints = offer.get("endpoints")
        keys = offer.get("keys")
        if not topic_name:
            return f"Invalid MQTT offer format: missing topic name in {offer}"
        if not endpoints or not isinstance(endpoints, list):
            return f"Invalid MQTT offer format: missing or invalid endpoints in {offer}"
        if not keys or not isinstance(keys, list) or len(keys) == 0:
            return f"Invalid MQTT offer format: missing or invalid keys in {offer}"
        if topic_name.find('/') != -1:
            return f"Invalid MQTT offer format: topic_name: '{topic_name}' must not contain '/'"
        
        has_set = "set" in endpoints
        has_state = "state" in endpoints
        topic_id = addTopic(device_id, topic_name, has_set, has_state)

        for key in keys:     
            key_name = key.get("key_name")
            value_type = key.get("value_type")
            min_value = key.get("min_value")
            max_value = key.get("max_value")
            enum_values = key.get("enum_values")

            if not key_name or not value_type:
                return f"Invalid MQTT offer format: missing key_name or value_type in {key} of topic {topic_name}"
            
            addTopicSchema(
                topic_id,
                key_name=key_name,
                value_type=value_type,
                min_value=min_value,
                max_value=max_value,
                enum_values=str(enum_values) if enum_values else None
            )   

        if has_set:
            subscribe(f"{device_id}/{topic_name}/set")
        if has_state:
            subscribe(f"{device_id}/{topic_name}/state")

    return None

def storeOffers(device_id, offers):
    """
    offers: list of dicts, each dict has offer type as key and list of offer details as values
    """
    if not offers:
        return None

    parse_errors = []
    for offer in offers:
        if "MQTT" in offer:
            error = storeMqttInfo(device_id, offer["MQTT"])
            if error:
                parse_errors.append(error)
            continue
        # Future offer types can be handled here
    
    if parse_errors:
        return "; ".join(parse_errors)
    return None

def addDevice(device_id, name, info, device, offer):
    addNewDevice(device_id, name, info, device)
    error = storeOffers(device_id, offers)
    if error:
        deleteDevice(device_id)
        return error
    return None