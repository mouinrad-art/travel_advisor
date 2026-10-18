"""Vercel Python Function: POST /api/chat; no secrets sent to browser."""
import json
import logging
import os
from http.server import BaseHTTPRequestHandler
from openai import AuthenticationError, PermissionDeniedError, RateLimitError, APIConnectionError, APITimeoutError, BadRequestError
from pydantic import ValidationError
from core import Advisor, Session, TripPreferences, Metrics

log = logging.getLogger(__name__)
MAX_BODY = 65000

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split('?')[0] == '/api/chat':
            return self.respond(200, {'status': 'ok', 'service': 'travel-advisor', 'api_key_configured': bool(os.getenv('OPENAI_API_KEY', '').strip())})
        return self.respond(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path.split('?')[0] != '/api/chat':
            return self.respond(404, {'error': 'Not found'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if length < 1 or length > MAX_BODY:
                return self.respond(413, {'error': 'Request size must be 1–65000 bytes.'})
            payload = json.loads(self.rfile.read(length))
            if not isinstance(payload, dict):
                return self.respond(400, {'error': 'Expected a JSON object.'})
            message = payload.get('message')
            if not isinstance(message, str) or not 1 <= len(message.strip()) <= 2500:
                return self.respond(400, {'error': 'Message must be 1–2500 characters.'})
            saved = payload.get('session') or {}
            if not isinstance(saved, dict):
                return self.respond(400, {'error': 'Invalid session.'})
            history = saved.get('history', [])
            if not isinstance(history, list) or len(history) > 24:
                return self.respond(400, {'error': 'Invalid history length.'})
            history = [h for h in history if isinstance(h, dict) and h.get('role') in ('user', 'assistant') and isinstance(h.get('content'), str) and len(h['content']) <= 3000]
            raw_metrics = saved.get('metrics') or {}
            if not isinstance(raw_metrics, dict):
                raw_metrics = {}
            session = Advisor()
            if not os.getenv('OPENAI_API_KEY', '').strip():
                log.error('OPENAI_API_KEY missing in this Vercel deployment')
                return self.respond(503, {'error': 'Server API key is not configured. Check Vercel environment variables and redeploy.'})
            reply, plan = Advisor().chat(session, message)
            state = {'history': session.history[-24:], 'summary': session.summary,
                     'preferences': session.preferences.model_dump(), 'metrics': vars(session.metrics)}
            return self.respond(200, {'reply': reply, 'itinerary': plan.model_dump() if plan else None, 'session': state})
        except AuthenticationError:
            log.exception('OpenAI authentication rejected (401). Check Vercel OPENAI_API_KEY and deployment environment.')
            return self.respond(502, {'error': 'OpenAI authentication failed. Check the API key configured in Vercel, then redeploy.'})
        except PermissionDeniedError:
            log.exception('OpenAI API permission denied')
            return self.respond(502, {'error': 'OpenAI API access denied. Check API key permissions and project.'})
        except RateLimitError:
            log.exception('OpenAI rate limit or insufficient quota')
            return self.respond(503, {'error': 'OpenAI rate limit or quota reached. Check API billing and limits.'})
        except (APITimeoutError, APIConnectionError):
            log.exception('OpenAI connection or timeout failure')
            return self.respond(503, {'error': 'OpenAI is temporarily unreachable. Try again.'})
        except BadRequestError:
            log.exception('OpenAI rejected request or model')
            return self.respond(502, {'error': 'The AI model request was rejected. Check model names and API permissions.'})
        except (ValueError, ValidationError, TypeError, KeyError, json.JSONDecodeError):
            log.exception('Invalid input or model output')
            return self.respond(400, {'error': 'Invalid input or itinerary. Please revise your request.'})
        except Exception:
            log.exception('Unexpected backend error')
            return self.respond(500, {'error': 'Unexpected server error. Check Vercel function logs.'})

    def respond(self, status, body):
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)
