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
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'X-Requested-With, Content-type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/clients':
            self.handle_list_clients()
        elif self.path.startswith('/contacts/') and self.path.endswith('/clients'):
            self.handle_list_linked_clients_for_contact()
        elif self.path.startswith('/clients/') and self.path.endswith('/contacts'):
            self.handle_list_linked_contacts()
        elif self.path.startswith('/contacts/') and len(self.path.split('/')) == 3:
            self.handle_list_linked_clients()
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

    def do_DELETE(self):
        if self.path.startswith('/unlink_contact_from_client/'):
            self.handle_unlink_contact_from_client()
        elif self.path.startswith('/unlink_client_from_contact/'):
            self.handle_unlink_client_from_contact()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Not found'}).encode())

    def handle_unlink_client_from_contact(self):
        # Extract contact_email and client_code from the URL
        parts = self.path.split('/')
        if len(parts) != 4:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid URL format'}).encode())
            return

        contact_email = parts[2]
        client_code = parts[3]

        # Get contact and client information
        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Contact not found'}).encode())
            return

        client = self.client_controller.get_by_code(client_code)
        if not client:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Client not found'}).encode())
            return

        try:
            self.contact_controller.unlink_client_from_contact(contact['id'], client['id'])
            self._set_headers(200)
            self.wfile.write(json.dumps(
                {'message': f"Client '{client_code}' unlinked from contact '{contact_email}'"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    def handle_unlink_contact_from_client(self):
        # Extract client_code and contact_email from the URL
        parts = self.path.split('/')
        if len(parts) != 4:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid URL format'}).encode())
            return

        client_code = parts[2]
        contact_email = parts[3]

        # Get client and contact information
        client = self.client_controller.get_by_code(client_code)
        if not client:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Client not found'}).encode())
            return

        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Contact not found'}).encode())
            return

        try:
            self.contact_controller.unlink_contact_from_client(client['id'], contact['id'])
            self._set_headers(200)
            self.wfile.write(json.dumps(
                {'message': f"Contact '{contact_email}' unlinked from client '{client_code}'"}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

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

    def handle_list_linked_contacts(self):
        client_id = self.path.split('/')[2]  # Assuming path like /clients/{client_id}/contacts
        try:
            linked_contacts = self.contact_controller.list_linked_contacts(client_id)
            self._set_headers()
            self.wfile.write(json.dumps(linked_contacts).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

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

    def handle_list_linked_clients(self):
        # Extract contact_email from the URL
        parts = self.path.split('/')
        if len(parts) != 3:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid URL format'}).encode())
            return

        contact_email = parts[2]

        # Get contact information
        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Contact not found'}).encode())
            return

        try:
            linked_clients = self.client_controller.list_linked_clients(contact['id'])
            self._set_headers()
            self.wfile.write(json.dumps(linked_clients).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def handle_list_linked_clients_for_contact(self):
        # Extract contact email from the URL
        parts = self.path.split('/')
        if len(parts) != 4:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid URL format'}).encode())
            return

        contact_email = parts[2]

        # Get contact information
        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            self._set_headers(404)
            self.wfile.write(json.dumps({'error': 'Contact not found'}).encode())
            return

        # List linked clients for the contact
        clients = self.client_controller.list_linked_clients(contact['id'])
        self._set_headers()
        self.wfile.write(json.dumps(clients).encode())

# #
# # //Routes.client...contacts..etc,polymofysms....controlle rconnect response from model to req...router...endpoint to front end.database helpeer...data laye
# deepedndeny injections.....solid..principel
#
#
# OOP
# Abstraction
# Encapsulation
# inheritance
# polymorphism
# SOLID-> models
# Single Responsibility Principle
# Open/Closed Principle
# dry Principle->routes
# Dependencyinjection->routes
#
# algorithms
#         data structures
#
#         OOP
#         =============
#         Abstraction
#         Inheritance
#         encapsulation
#         polymorphism
#
#         Design Principle
#         ==================
#         SOLID Principles => models
#         Dry Principle => routes
#
#         Design Patterns
#         ================
#         Dependency Injection => routes
#         Factory Design Pattern =>
#
#
#
# Improvements
# I would recommend a bulk import of clients and contacts
# I would allow soft deletion of
# Improvements
# I would recommend a bulk import of clients and contacts
# I would allow soft deletion of clients and contacts so that if the user delete person by mistake they have an oppurtunity to retrieve that data (Because of POPPIA we should have an expiry date of how long we can store the deleted data before hard delete)
# Multiple delete of clients and contacts
# //rename database to Relationshi|
# cascading relationsSHip
