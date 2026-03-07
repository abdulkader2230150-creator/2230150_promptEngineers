# MarsOps: Habitat Automation Platform

Distributed, event-driven automation platform for the Mars IoT simulator. It ingests REST + telemetry data, normalizes events, evaluates automation rules, and provides a real-time dashboard.

## Quick Start
1. Load simulator image (once):
   ```bash
   docker load -i mars-iot-simulator-oci.tar
   ```
2. Start the stack:
   ```bash
   docker compose up --build
   ```

## URLs
- Simulator: http://localhost:8080
- Backend API: http://localhost:8000
- Frontend: http://localhost:8081
- RabbitMQ UI: http://localhost:15672

## Repo Structure
```
.
├── input.md
├── Student_doc.md
├── booklets/
└── source/
```

## Notes
- Rules are stored in SQLite (`/data/rules.db`) via a shared Docker volume.
- Latest sensor state is kept in memory and exposed via the backend API.
