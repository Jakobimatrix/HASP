# Speedtest client for Home Assistant MQTT

This folder contains a small client-side example for a speedtest sensor.

- register one device
- collect download, upload, and ping values
- publish discovery so HA creates three sensor entities
- support enable/disable state via a control topic

## File list

- config.py: central configuration values
- mqtt_client.py: MQTT helpers and Home Assistant discovery publishing
- state_manager.py: local enabled/disabled state helpers
- speedtest_client.py: speedtest execution and payload formatting
- run_speedtest.py: main cron entrypoint
- set_state.py: local toggle helper for enable/disable state

## 1) Set up the speedtest environment

Create the shared virtual environment:

```bash
bash /root/HASP/scripts/create_venv.sh
```

Then edit the config before running the script:

```python
DEVICE_ID = "device123"
MQTT_BROKER = "192.168.178.106"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt2HA"
MQTT_PASSWORD = "*******"
```

If your Mosquitto broker is anonymous, set:

```python
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
```

If you want the device to stay enabled by default (IF HA is not reachable):

```python
DEFAULT_ENABLED = True
```

## 2) Set up MQTT on Home Assistant

1. Open Home Assistant.
2. Go to Settings > Devices & Services.
3. Add Integration > MQTT.
4. Enter the broker host and port:
   - Host: `192.168.178.106`
   - Port: `1883`
5. If the broker requires credentials, use the same username/password as the Mosquitto add-on.
6. If you do not want a second login layer, configure Mosquitto as anonymous:

```json
{
  "logins": [],
  "anonymous": true
}
```

7. Save and reload the MQTT integration if needed.

The discovery topics published by the client will create the sensors automatically once MQTT is active.

## 3) Set up the speedtest cron job

Use the Python binary from the venv:

```cron
*/20 * * * * /root/HASP/scripts/.venv/bin/python /root/HASP/scripts/speedtest/run_speedtest.py >> /var/log/speedtest.log 2>&1
```

The cron script runs the speedtest and publishes:
- download value
- upload value
- ping value
- attributes
- discovery messages for HA

## 4) Set up the HA switch

### UI method

1. Open Home Assistant.
2. Go to Settings > Devices & Services.
3. Click Helpers.
4. Click Create Helper.
5. Choose Toggle.
6. Name it: `Speedtest device123 enabled`.
7. Set the entity ID to: `input_boolean.speedtest_device123_enabled`.
8. Save.

### YAML method

```yaml
input_boolean:
  speedtest_device123_enabled:
    name: Speedtest device123 enabled
    initial: true
    icon: mdi:toggle-switch
```

Then create an automation that publishes the state to the MQTT control topic:
1. Open Home Assistant.
2. Go to Settings > Automations & Scenes.
4. Create Automation > Create new automation > 3dots > Edit in YAML

```yaml
alias: Speedtest Crontab MQTT control
triggers:
  - trigger: state
    entity_id: input_boolean.speedtest_device123_enabled
actions:
  - choose:
      - conditions:
          - condition: state
            entity_id: input_boolean.speedtest_device123_enabled
            state: "on"
        sequence:
          - action: mqtt.publish
            data:
              topic: devices/device123/control
              payload: '{"enabled": true}'
              retain: true
      - conditions:
          - condition: state
            entity_id: input_boolean.speedtest_device123_enabled
            state: "off"
        sequence:
          - action: mqtt.publish
            data:
              topic: devices/device123/control
              payload: '{"enabled": false}'
              retain: true
```

The control topic is:

```text
devices/device123/control
```

Example payloads:

```json
{"enabled": true}
```

```json
{"enabled": false}
```

## 5) Explain the local switch script

The script `set_state.py` gives you a local way to toggle the speedtest from the server itself.

Use it like this:

```bash
/root/HASP/scripts/.venv/bin/python /root/HASP/scripts/speedtest/set_state.py --enabled true
```

or:

```bash
/root/HASP/scripts/.venv/bin/python /root/HASP/scripts/speedtest/set_state.py --enabled false
```

This updates the local state file and publishes the same value to the HA MQTT control topic.

The script reads the same control topic so HA and the local server stay in sync.

## Result

After setup, Home Assistant will show three entities for your device:
- `sensor.speedtest_download_device123`
- `sensor.speedtest_upload_device123`
- `sensor.speedtest_ping_device123`

Add them to a dashboard with an Entities card or History Graph card.
