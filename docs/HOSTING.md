# Hosting for the demo

The server is plain FastAPI with JSON files in `out/`. No database and no build step.

## Laptop (the safe option)

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...
uvicorn app.server:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`. A phone on the same Wi-Fi can open `http://<laptop-ip>:8000`. Venue Wi-Fi often blocks device-to-device traffic, so test this before relying on it.

## Replit (for a public link a phone can open)

Not tested by us. The steps as we understand them:

1. Import the GitHub repo into a new Repl.
2. Put `ANTHROPIC_API_KEY` in Secrets, never in a file.
3. Set the run command to `uvicorn app.server:app --host 0.0.0.0 --port 8000`.
4. Use the Repl's own web preview link. A separate Deployment may not keep files in `out/` between restarts.

Whichever you use, generate the brief once before the demo so a saved result exists if the live call stalls.
