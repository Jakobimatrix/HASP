# Speedtest client for Home Assistant MQTT

This folder contains a small client-side example for a speed test sensor:

- register one device
- collect download, upload, and ping values
- send values to Home Assistant over MQTT
- publish discovery so HA creates three sensor entities
- support enable/disable state via a control topic

## File list

- config.py: central configuration values
- mqtt_client.py: MQTT helpers and HA discovery publishing
- state_manager.py: local enabled/disabled state helpers
- speedtest_client.py: speedtest execution and payload formatting
- run_speedtest.py: main cron entrypoint
- set_state.py: local toggle helper for enable/disable state

## What to change in config.py

Edit these values before running the script:

```python
DEVICE_ID = "device123"
MQTT_BROKER = "192.168.178.106"
MQTT_PORT = 1883
MQTT_USERNAME = "mqtt2HA"
MQTT_PASSWORD = "*******"
```

If your broker uses anonymous access, set:

```python
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
```

If you want the device to stay enabled by default:

```python
DEFAULT_ENABLED = True
```

## Dependencies

Use the shared venv

```bash
bash /root/HASP/scripts/create_venv.sh
```



## Cron job

Install the script in a folder like `/root/speedtest` and use a venv for the dependencies.

Example cron entry:

```cron
*/20 * * * * /root/speedtest/.venv/bin/python /root/speedtest/run_speedtest.py >> /var/log/speedtest.log 2>&1
```

If you keep the system Python and no venv, use:

```cron
*/20 * * * * /usr/bin/python3 /root/speedtest/run_speedtest.py >> /var/log/speedtest.log 2>&1
```



## Home Assistant GUI steps

1. Open Home Assistant.
2. Go to Settings > Devices & Services.
3. Add Integration > MQTT.
4. Enter the same broker host and port: `192.168.178.106:1883`.
5. Restart or reload MQTT if needed.
6. The discovery payload from the script creates sensors automatically.
7. Go to Settings > Devices & Services > Devices and look for the device called `HASPSpeedTest device123`.
8. Open the device and check entities:
   - `sensor.speedtest_download_device123`
   - `sensor.speedtest_upload_device123`
   - `sensor.speedtest_ping_device123`
9. Add them to a dashboard with a History Graph or Entities card.
10. Optional: create a helper toggle in HA for the enabled state and publish the state to the control topic.

For the enabled/disabled flow, the script supports a local state file and a control topic. The control topic is:

```text
devices/device123/control
```

Example payload:

```json
{"enabled": true}
```

or

```json
{"enabled": false}
```

## How to enable or disable the script locally

Use the local helper:

```bash
python3 /root/speedtest/set_state.py --enabled true
```

or

```bash
python3 /root/speedtest/set_state.py --enabled false
```

This updates the local state file and also publishes the same value to the HA MQTT control topic.
