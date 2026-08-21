# Roshan Singh - Ocean Engineering Portfolio & Tools

A Flask portfolio for Roshan Singh, Senior Engineering Analyst, with working engineering utilities for RAO/PDF table extraction and OrcaFlex model preparation.

## What is included

- Responsive ocean-engineering portfolio based on Roshan's current resume
- RAO & PDF Table Extractor with Excel output
- OrcaFlex Toolkit: vessel corners, stiffness and drag coefficient utilities
- Downloadable PDF resume
- Render Blueprint and health check for straightforward deployment

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

Open `http://127.0.0.1:5000`.

## Deploy on Render

The repository includes `render.yaml`, so it can be deployed as a Blueprint:

1. Sign in to Render and connect GitHub.
2. Choose **New > Blueprint**.
3. Select this repository and approve the detected service.
4. Deploy. Future commits to the linked branch deploy automatically.

The same settings can be entered manually as a Web Service:

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 180 app:app`
- Health check: `/health`

## Main routes

- `/` - portfolio
- `/rao-extractor` - RAO/PDF extraction tool
- `/orcaflex-toolkit` - engineering calculator collection
- `/knowledge-graph/` - interactive fatigue, VIV and interference knowledge graph
- `/health` - deployment health check
