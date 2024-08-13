# utils.py

import json

def _set_headers(handler, status_code=200):
    handler.send_response(status_code)
    handler.send_header('Content-type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
    handler.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-type')
    handler.end_headers()

def handle_not_found(handler, resource, resource_name):
    if not resource:
        _set_headers(handler, 404)
        handler.wfile.write(json.dumps({'error': f'{resource_name} not found'}).encode())
        return True
    return False
