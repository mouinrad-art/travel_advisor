# AI Travel Advisor v3 — Vercel Edition

Python OpenAI Responses API + static browser UI. Includes conversational intake, structured travel plans, memory, budgets, downloads, diagnostics and a Jupyter notebook.

## Repository layout

```text
api/chat.py                 Vercel Python endpoint
core.py                     Shared AI engine and Pydantic schemas
public/index.html           Chat UI
public/favicon.svg          Browser icon
vercel.json                  Vercel routing
requirements.txt            Production Python dependencies
Travel_Advisor_Notebook.ipynb  Experiment with core engine
.env.example                Local environment template
```

## Local setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env  # Windows: copy .env.example .env
```

Set `OPENAI_API_KEY` in `.env`. Never commit it. For notebook usage, the notebook loads `.env` locally. For local API testing, run `vercel dev` (requires Vercel CLI: `npm i -g vercel`).

## Deploy on Vercel

1. Extract ZIP, upload **contents** to the GitHub repository root (not a nested directory unless explicitly configured).
2. Ensure `vercel.json`, `api/`, `public/`, `core.py` and `requirements.txt` are all visible at the same GitHub root.
3. In Vercel, import your repository, Framework Preset **Other**.
4. **Root Directory**: leave default / repository root. Never enter `vercel.json` (it is a file).
5. **Build Command**: leave default. **Output Directory**: leave default.
6. In Project Settings → Environment Variables set `OPENAI_API_KEY`, `CHAT_MODEL=gpt-4.1-mini`, `PLANNER_MODEL=gpt-4.1` for **Production** and **Preview** if needed.
7. Save and **redeploy**. Test the **new** deployment URL, not an older preview.
8. Open `https://YOUR_DEPLOYMENT.vercel.app/api/chat` in a browser. It returns a status JSON with `api_key_configured` boolean but never the key itself.
9. Visit the site, enter `5 days in Tunisia, beaches and food`, then check the resulting itinerary.

## 401 locally works but Vercel fails

- A `401 Unauthorized` from OpenAI means the deployed function sent credentials that OpenAI rejected.
- Check `OPENAI_API_KEY` spelling, whitespace, correct project and environment scope.
- Check the deployment **Environment** (Production vs Preview) in Vercel.
- Redeploy after updating secrets. Old deployments can retain older environment configuration.
- Test `/api/chat` with GET to confirm the key exists (not that it is valid).
- Check Vercel → Logs for the full exception. This version returns an actionable `502` message rather than a generic `500` for authentication errors.
- Avoid exposing or logging API keys. Rotate a key if it was ever committed or disclosed.

## Testing

```bash
pytest -q
```

## Security and limitations

- OpenAI API calls happen on the server. The browser never receives the API key.
- Conversation state is sent from the browser and is **not authenticated or tamper-proof**. For public deployment use server-side session storage, authentication, rate limiting, bot protection and per-user spend limits.
- No live travel availability, weather or fares are queried. All budgets are estimates.
- Token usage is approximate across sessions and can be reset by clients. For billing, aggregate usage server-side.
- API key must be an OpenAI Platform API key with appropriate project permissions and billing.
