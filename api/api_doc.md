# API Documentation

## /api/getTime

**POST**

Receives a device_id in the request JSON, validates it, updates the device's last seen timestamp, and returns the current server time in seconds and nanoseconds.

**Request JSON:**
```json
{
    "device_id": "<string>"
}
```

**Example Input:**
```json
{
    "device_id": "device123"
}
```

**Successful Response (HTTP 200):**
```json
{
    "status": "ok",
    "s": 1717689600,      # Example: seconds since epoch
    "ns": 1717689600123456789  # Example: nanoseconds timestamp
}
```

**Error Response (HTTP 403):**
```json
{
    "error": "invalid device_id"
}
```

**Error Cases:**
- Missing "device_id" in the request JSON.
- "device_id" does not exist in the system.

---

## /api/ping

**POST**

Receives a device_id in the request JSON, validates it, updates the device's last seen timestamp, and returns a simple status response.

**Request JSON:**
```json
{
    "device_id": "<string>"
}
```

**Example Input:**
```json
{
    "device_id": "device123"
}
```

**Successful Response (HTTP 200):**
```json
{
    "status": "ok"
}
```

**Error Response (HTTP 403):**
```json
{
    "error": "invalid device_id"
}
```

**Error Cases:**
- Missing "device_id" in the request JSON.
- "device_id" does not exist in the system.

---

## /api/registerDevice

**POST**

Registers a new device with the provided name and definition. Optionally accepts a "hardcoded" device_id, otherwise generates one. Returns the device ID with which the device has to call other API functions from now on.

**Request JSON:**
```json
{
    "name": "<string>",
    "definition": "<string>",
    "device_id": "<string>"  # optional
}
```

**Example Input:**
```json
{
    "name": "Device Name",
    "definition": "Device Definition"
}
```

**Successful Response (HTTP 200):**
```json
{
    "device_id": "<string>"
}
```

**Error Response (HTTP 403):**
```json
{
    "error": "invalid device_id"
}
```

**Error Response (HTTP 400):**
```json
{
    "error": "name and definition required"
}
```

**Error Cases:**
- Missing "name" or "definition" in the request JSON.
- Provided "device_id" does not exist in the system.

---

## /api/reportValues

**POST**

Receives a device_id and key-value pairs in the request JSON, validates the device, updates the device's last seen timestamp, and stores the reported values with a timestamp. Optionally accepts a timestamp and report_id.

**Request JSON:**
```json
{
    "device_id": "<string>",
    "keyValues": {"key1": value1, ...},
    "s": <int>,         # optional, seconds since epoch
    "ns": <int>,        # optional, nanoseconds
    "report_id": "<string>"  # optional
}
```

**Example Input:**
```json
{
    "device_id": "device123",
    "keyValues": {"temperature": 22.5, "humidity": 60}
}
```

**Successful Response (HTTP 200):**
```json
{
    "status": "ok"
}
```

**Error Response (HTTP 403):**
```json
{
    "error": "invalid device_id"
}
```

**Error Response (HTTP 400):**
```json
{
    "error": "no keyValues"
}
```

**Error Cases:**
- Missing "device_id" in the request JSON.
- "device_id" does not exist in the system.
- Missing or invalid "keyValues" in the request JSON.
