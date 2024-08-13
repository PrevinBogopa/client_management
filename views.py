import json
from http.server import BaseHTTPRequestHandler

import mysql

from controllers import ClientController, ContactController


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.client_controller = ClientController()
        self.contact_controller = ContactController(self.client_controller)  # Pass the instance
        super().__init__(*args, **kwargs)

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/clients':
            self.handle_list_clients()
        elif self.path == '/contacts':
            self.handle_list_contacts()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))

        if self.path == '/clients':
            self.handle_create_client(post_data)
        elif self.path == '/contacts':
            self.handle_create_contact(post_data)
        elif self.path == '/link_contact_to_client':
            self.handle_link_contact_to_client(post_data)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def handle_list_clients(self):
        clients = self.client_controller.list_clients()
        self._set_headers()
        self.wfile.write(json.dumps(clients).encode())

    def handle_list_contacts(self):
        contacts = self.contact_controller.list_contacts()
        self._set_headers()
        self.wfile.write(json.dumps(contacts).encode())

    def handle_create_client(self, data):
        name = data.get('name')
        if not name:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Name is required'}).encode())
            return

        client_code = self.client_controller.create_client(name)
        self._set_headers(201)
        self.wfile.write(json.dumps({'message': f"Client '{name}' created", 'client_code': client_code}).encode())

    def handle_create_contact(self, data):
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')

        if not all([name, surname, email]):
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Name, surname, and email are required'}).encode())
            return

        try:
            self.contact_controller.create_contact(name, surname, email)
            self._set_headers(201)
            self.wfile.write(json.dumps({'message': f"Contact '{name} {surname}' created"}).encode())
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:  # Duplicate entry error
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Email already exists'}).encode())
            else:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'Internal Server Error'}).encode())

    # views.py

    def handle_link_contact_to_client(self, data):
        client_codes = data.get('client_code')
        contact_emails = data.get('contact_email')

        if not client_codes or not contact_emails:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Client code(s) and contact email(s) are required'}).encode())
            return

        if isinstance(client_codes, str):
            client_codes = [client_codes]
        if isinstance(contact_emails, str):
            contact_emails = [contact_emails]

        linked_contacts = []
        errors = []

        for client_code in client_codes:
            for contact_email in contact_emails:
                try:
                    self.contact_controller.link_contact_to_client(client_code, contact_email)
                    linked_contacts.append({
                        'client_code': client_code,
                        'contact_email': contact_email,
                        'status': 'linked'
                    })
                except Exception as e:
                    errors.append({
                        'client_code': client_code,
                        'contact_email': contact_email,
                        'error': str(e)
                    })

        response = {
            'linked_contacts': linked_contacts,
            'errors': errors
        }

        self._set_headers(200 if not errors else 207)  # 207 Multi-Status for partial success
        self.wfile.write(json.dumps(response).encode())
