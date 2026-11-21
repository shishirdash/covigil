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

The repo has a `.replit` file, so the run command, port and model are already set.

1. Import the GitHub repo into a new Repl (Create Repl → Import from GitHub).
2. Put `ANTHROPIC_API_KEY` in Secrets, never in a file. It must be a Console API key (`sk-ant-api03-…`), not a Claude login token.
3. Press Run. Dependencies install on boot; the page opens in the web preview.
4. To get a public link, Deploy → **Reserved VM** (already chosen in `.replit`). Decisions are saved in `out/state.json`, and Autoscale can run several instances that do not share that file. Add the same secret to the deployment.

`COVIGIL_MODEL` is set to `claude-opus-5-5` in `.replit`. Change it there to try another model.

Pages: `/` medicines (med rec), `/flags` issues to review, `/patient` patient screen.

Whichever you use, generate the brief once before the demo so a saved result exists if the live call stalls.
