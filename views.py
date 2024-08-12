import json
from http.server import BaseHTTPRequestHandler
from controllers import ClientController, ContactController


class RequestHandler(BaseHTTPRequestHandler):
    client_controller = ClientController()
    contact_controller = ContactController()

    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
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

        self.contact_controller.create_contact(name, surname, email)
        self._set_headers(201)
        self.wfile.write(json.dumps({'message': f"Contact '{name} {surname}' created"}).encode())

    def handle_link_contact_to_client(self, data):
        client_code = data.get('client_code')
        contact_email = data.get('contact_email')

        try:
            self.contact_controller.link_contact_to_client(client_code, contact_email)
            self._set_headers(200)
            self.wfile.write(
                json.dumps({'message': f"Contact '{contact_email}' linked to client '{client_code}'"}).encode())
        except Exception as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
