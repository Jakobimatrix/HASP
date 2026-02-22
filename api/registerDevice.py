from flask import request, jsonify
import uuid

from db.devices import addNewDevice, deviceExists, getDevice
from utilities.cache import getResetDevice, clearResetDevice
from utilities.db import removeMqttForDevice, deleteDevice, addDevice, updateDevice

def handleRegisterOrUpdateDevice(
    *,
    name=None,
    device_id=None,
    info=None,
    device=None,
    offers_string=None,
    allow_create=True
):
    # Parse offers
    offers = []
    if offers_string:
        try:
            offers = json.loads(offers_string)
        except Exception as e:
            raise ValueError(f"Failed to parse offers: {str(e)}")

    reset_id = getResetDevice()
    if reset_id:
        if not deviceExists(reset_id):
            raise RuntimeError("reset device not found")

        error = updateDevice(reset_id, info, offers)
        if error:
            raise ValueError(f"Failed to parse offers: {error}")

        clearResetDevice()
        return reset_id

    if device_id:
        if not deviceExists(device_id):
            raise ValueError("invalid device_id")

        error = updateDevice(device_id, info, offers)
        if error:
            raise ValueError(f"Failed to parse offers: {error}")

        return device_id

    if not allow_create:
        raise ValueError("device_id required")

    # Create new device
    new_device_id = device_id or str(uuid.uuid4())
    if deviceExists(new_device_id):
        raise ValueError("invalid device_id")

    error = addDevice(new_device_id, name, info, device, offers)
    if error:
        raise ValueError(f"Failed to parse offers: {error}")

    return new_device_id
    
def register(app):

    """
    API Endpoint:
        POST /api/registerDevice
        POST /api/updateDeviceInfo

    Description:
        Registers a new device with the provided name and definition. Optionally accepts a "hardcoded" device_id, otherwise generates one which the device has to remember for futur calls.
        Validates the device_id, name, and definition.

    Request JSON:
        {
            "name": "<string>",        # How the device is named in the GUI (can be renamed later, not unique, device can not rely on it)
            "info": "<string>",        # Info text shown in the GUI (optional)
            "device": "<string>",      # Device type shown in the GUI (optional)
            "device_id": "<string>"    # for hardcoded ids on bare metal. (optional for registerDevice ,mandatory for updateDeviceInfo)
            "offers": "<string>"       # List of offers (optional, can be updated later via updateDeviceInfo, must fit the defined schema, otherwise the offer is ignored.)
        }

    Successful Response (HTTP 200):
        {
            "device_id": "<string>"      # The registered device_id (either provided or generated) which the device should use for future interactions with the API.
                                         # Note: The device_id is the unique identifier for the device. If the device_id already exists in the system, the registration will fail with an error.
        }

    Error Response (HTTP 403):
        {
            "error": "invalid device_id / offer parsing failed"
        }

    Example Input_1:
        {
            "name": "Speedtest Server",
            "offers": [],
            "info": "Speedtest device reporting internet speed and response time.",
            "Device": "Server"
        }

    Example Input_2:
    {
    "name": "RGB Light",
    "offers": [
        {
        "MQTT": {
            "/wake": {
            "endpoints": ["set", "state"],
            "keys": [
                {
                "key_name": "state",
                "value_type": "enum",
                "enum_values": ["ON", "OFF"]
                }
            ]
            },
            "/brightness": {
            "endpoints": ["set", "state"],
            "keys": [
                {
                "key_name": "brightness",
                "value_type": "float",
                "min_value": 0,
                "max_value": 1
                }
            ]
            },
            "/rgb": {
            "endpoints": ["set", "state"],
            "keys": [
                { "key_name": "r", "value_type": "int", "min_value": 0, "max_value": 255 },
                { "key_name": "g", "value_type": "int", "min_value": 0, "max_value": 255 },
                { "key_name": "b", "value_type": "int", "min_value": 0, "max_value": 255 }
            ]
            },
            "/hsv": {
            "endpoints": ["set", "state"],
            "keys": [
                { "key_name": "h", "value_type": "float", "min_value": 0, "max_value": 360 },
                { "key_name": "s", "value_type": "float", "min_value": 0, "max_value": 1 },
                { "key_name": "v", "value_type": "float", "min_value": 0, "max_value": 1 }
            ]
            },
            "/effects": {
            "endpoints": ["set", "state"],
            "keys": [
                {
                "key_name": "effect",
                "value_type": "enum",
                "enum_values": ["WAVES", "RAINBOW", "PULSE"]
                }
            ]
            }
        }
        }
    ],
    "info": "RGB Light device.",
    "Device": "ESP32"
    }

    # Explaination of MQTT offer schema:
    - Each MQTT offer is a dict with topic names as keys and list of key definitions as values.
    - Each key definition is a dict that must contain "key_name" and "value_type". Depending on the value_type, it can optionally contain "min_value", "max_value", and "enum_values".
    - The "endpoints" field in the key definition specifies which endpoints should be created for this key (e.g., "set" for /api/setValue, "state" for /api/getValue). If "endpoints" is not provided, it defaults to both "set" and "state".
    - The device is expected to 
       - publish its state to "device_id/{topic_name}/state"
       - subscribe to "device_id/{topic_name}/set" for receiving commands.

    Error Cases:
        - Provided "device_id" does already exist in the system.
        - Failed to parse offers
    """

    @app.route("/api/registerDevice", methods=["POST"])
    def registerDevice():
        data = request.get_json(force=True)

        try:
            device_id = handleRegisterOrUpdateDevice(
                name=data.get("name"),
                device_id=data.get("device_id"),
                info=data.get("info"),
                device=data.get("device"),
                offers_string=data.get("offers"),
                allow_create=True
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 403
        except RuntimeError:
            return jsonify({"error": "Internal Server Error."}), 500

        return jsonify({"device_id": device_id}), 200

    @app.route("/api/updateDeviceInfo", methods=["POST"])
    def updateDeviceInfo():
        data = request.get_json(force=True)

        try:
            device_id = handleRegisterOrUpdateDevice(
                device_id=data.get("device_id"),
                info=data.get("info"),
                offers_string=data.get("offers"),
                allow_create=False
            )
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        return jsonify({"device_id": device_id}), 200

