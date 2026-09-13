# Speedtest client for Home Assistant MQTT

This folder contains a small client-side example for a speedtest sensor but can be used for any other subfolder.

- register one device
- collect download, upload, and ping values
- publish discovery so HA creates three sensor entities
- support enable/disable state via a control topic

## File list

- template_config.py: template configuration values
- ../MQTT/mqtt_client.py: shared MQTT and Home Assistant discovery helpers
- speedtest_client.py: speedtest execution and payload formatting
- run_speedtest.py: main cron entrypoint
- set_state.py: local toggle helper for enable/disable state

## 1) Set up the speedtest environment

Create the shared virtual environment:

```bash
bash /root/HASP/scripts/create_venv.sh
```
copy `template_config.py` to `config.py`
Then edit the config.py before running the script. It is copied from template_config.py:

```python
DEVICE_ID = "device123"
MQTT_BROKER = "192.168.178.106"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt2HA"
MQTT_PASSWORD = "*******"
```

The shared MQTT module derives control, state, attributes, acknowledgement, and
Home Assistant discovery topics from `DEVICE_ID`, `SENSOR_NAME`, and
`TOPIC_PREFIX`. A new sensor only needs its own config and cron entrypoint.

If your Mosquitto broker is anonymous, set:

```python
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
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

### Restart safety: retained MQTT state

MQTT `retain: true` keeps the last message on the topic. This is the important part for restart safety.

If the broker restarts and clears retained state, the last MQTT value is lost. In that case, the cron job will default to enabled only if no retained message exists.

For a durable restart-safe setup, use one of these options in Home Assistant:

1. Keep the toggle helper as the source of truth and re-publish it on HA startup.
2. Use an automation triggered by HA startup to publish the current toggle state again:

```yaml
alias: Speedtest control republish on startup
triggers:
  - trigger: homeassistant
    event: start
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

3. If your broker is configured to clear retained messages at restart, this startup automation is the simplest HA-side fix.

This ensures that the last toggle state is restored immediately after Home Assistant comes back online.

## Result

After setup, Home Assistant will show three entities for your device:
- `sensor.speedtest_download_device123`
- `sensor.speedtest_upload_device123`
- `sensor.speedtest_ping_device123`

Add them to a dashboard with an Entities card or History Graph card.


