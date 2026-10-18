import os
from http.server import BaseHTTPRequestHandler
import json
from pydantic import ValidationError
from core import Advisor, Session, TripPreferences, Metrics, Itinerary

MAX_BODY = 65000

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.split('?')[0] != '/api/chat':
            return self.respond(404, {'error': 'Not found'})
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > MAX_BODY:
                return self.respond(413, {'error': 'Request body too large or empty'})
            payload = json.loads(self.rfile.read(size))
            message = payload.get('message', '')
            if not isinstance(message, str) or not 0 < len(message.strip()) <= 2500:
                return self.respond(400, {'error': 'Message must be 1–2500 characters'})
            saved = payload.get('session') or {}
            if not isinstance(saved, dict):
                return self.respond(400, {'error': 'Invalid session'})
            history = saved.get('history', [])
            if not isinstance(history, list) or len(history) > 24:
                return self.respond(400, {'error': 'Invalid conversation history'})
            history = [h for h in history if isinstance(h,dict) and h.get('role') in ('user','assistant') and isinstance(h.get('content'),str) and len(h['content'])<=3000]
            session = Session(history=history, summary=str(saved.get('summary',''))[:5000],
                preferences=TripPreferences.model_validate(saved.get('preferences') or {}),
                metrics=Metrics(**{k: saved.get('metrics',{}).get(k,0) for k in ('input_tokens','output_tokens','calls','latency_seconds')}))
            reply, plan = Advisor().chat(session, message)
            state = {'history': session.history[-24:], 'summary': session.summary,
                     'preferences': session.preferences.model_dump(), 'metrics': vars(session.metrics)}
            return self.respond(200, {'reply': reply, 'itinerary': plan.model_dump() if plan else None, 'session': state})
        except (ValueError, ValidationError, TypeError, KeyError):
            return self.respond(400, {'error': 'Invalid request or itinerary. Please retry.'})
        except Exception:
            return self.respond(500, {'error': 'The travel service could not complete the request. Please retry.'})

    def respond(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
