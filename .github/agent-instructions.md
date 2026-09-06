**Repo Guide**

Quick map for agents — find things fast. No API internals here.

- **Root**: `server.py`, `gunicorn.conf.py` — main run / deploy entry.
- **api/**: endpoint modules (see register/report/ping/mqtt/getTime).
- **db/**: data layer + schemas. Look at schema_*.sql and `db/devices.py`.
- **mqtt/**: broker client glue in `mqtt/client.py` and related DB hooks.
- **gui/**: web UI controllers (device pages, user mgmt, viz).
- **templates/**: HTML templates for UI pages (`devices.html`, `manage_device.html`).
- **utilities/**: common helpers (`db.py`, `cache.py`, `password.py`, `time.py`).
- **scripts/**: ops & admin scripts (newUser, restart_server, renew_cert, server_status).
- **examples/**: sample integrations (speedtest example folder).
- **tests/**: unit/infra tests (start here when validating behavior).

Where device-related code lives (fast path):
- `db/devices.py` — device persistence
- `api/registerDevice.py` — registration endpoint
- `api/reportValues.py` — telemetry ingest
- `gui/deviceManagement.py` + templates `templates/devices.html`, `templates/manage_device.html`

Where MQTT touches flow:
- `mqtt/client.py` -> `api/mqtt.py` -> `db/mqtt.py` -> `db/schema_mqtt.sql`

Workflows & entry points:
- Runtime server: `server.py`
- Deploy config: `gunicorn.conf.py`
- Admin tasks: scripts in `scripts/`
- Discovery helper: see [.github/skills/caveman-discover/SKILL.md](.github/skills/caveman-discover/SKILL.md)

Usage notes for agents:
- Start at root to locate `server.py` when testing run flows.
- For device features, follow the "device-related code" fast path above.
- For DB schema checks, open `db/schema_*.sql` files.
- For UI work, inspect `gui/` then `templates/` for matching pages.
- Do NOT assume APIs are explained here — API details live in separate skill docs.

If unclear, run caveman-discover flow in [.github/skills/caveman-discover/SKILL.md](.github/skills/caveman-discover/SKILL.md) and return a compressed map.

— End of guide.
