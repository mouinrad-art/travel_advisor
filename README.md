# AI Travel Advisor — Vercel Edition

A stateless, serverless deployment of the original Python OpenAI Responses API travel advisor. Includes a responsive HTML/JavaScript frontend and Python API endpoint.

## Vercel deployment

1. Create a GitHub repository and push the contents of **this directory** to the repository root. Never commit `.env` or API keys.
2. Open https://vercel.com/new and import the repository.
3. Select **Other** as the framework preset if asked. Set the root directory to the directory containing `vercel.json` (normally `./`). Do not configure a build command.
4. Under **Environment Variables**, add `OPENAI_API_KEY` (required), `CHAT_MODEL=gpt-4.1-mini` and `PLANNER_MODEL=gpt-4.1` (optional). Add these for the Production environment (and Preview if needed).
5. Click **Deploy**, then visit your generated `.vercel.app` URL. Send a message to test the `/api/chat` function.
6. After changing environment variables, redeploy the project.

## Local testing

Install Vercel CLI (`npm i -g vercel`) and dependencies (`pip install -r requirements.txt`), then:

```bash
vercel login
vercel link
vercel env pull .env.local
vercel dev
```

Open the URL printed by Vercel CLI (typically http://localhost:3000). You can also add the environment variables in the Vercel dashboard before pulling them.

## Features

- Follow-up questions until destination, duration and interests are present
- Contradiction clarification, trip constraints, budget and travel pace
- Structured itinerary with day plans, budget, tips and assumptions
- Separate configurable intake and planner models
- Token usage and latency metrics returned by API
- JSON itinerary export, responsive interface, new-trip reset
- No server-side session persistence; session state is sent with each request

## Important deployment considerations

- Serverless execution has a maximum duration determined by the Vercel plan. Two sequential LLM calls may time out; choose fast models and check Function logs.
- The browser sends the conversation state with each request. This is convenient but **not tamper-proof**. For production, store state server-side in a database, validate state transitions, and add authentication.
- Add per-user rate limiting and spending caps before making this a public paid-API demo.
- Avoid logging personal trip details or API keys.
- Prices, opening hours and availability are not live-verified.
- A long chat may increase payload size and token cost; the original engine summarizes when history exceeds its threshold.
- The original Jupyter notebook and Streamlit UI are separate developer experiences; Vercel hosts this web UI instead.
