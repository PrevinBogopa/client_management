import json
from http.server import BaseHTTPRequestHandler

import mysql

from controllers.controllers import ClientController, ContactController
from controllers.linking_controller import LinkingController
from controllers.linked_controller import LinkedController
# from utils import _set_headers, handle_not_found

def handle_not_found(self, resource, resource_name):
    if not resource:
        self._set_headers(404)
        self.wfile.write(json.dumps({'error': f'{resource_name} not found'}).encode())
        return True
    return False


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.client_controller = ClientController()
        self.contact_controller = ContactController(self.client_controller)
        self.linking_controller = LinkingController(self.client_controller, self.contact_controller)
        self.linked_controller = LinkedController(self.client_controller, self.contact_controller)
        super().__init__(*args, **kwargs)

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')

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
            self.linked_controller.list_linked_clients_for_contact(self.path, self._set_headers, self.write_response)
        elif self.path.startswith('/clients/') and self.path.endswith('/contacts'):
            self.linked_controller.list_linked_contacts(self.path, self._set_headers, self.write_response)
        elif self.path.startswith('/contacts/') and len(self.path.split('/')) == 3:
            self.linked_controller.list_linked_clients(self.path, self._set_headers, self.write_response)
        elif self.path == '/contacts':
            self.handle_list_contacts()
        else:
            self._set_headers(404)
            self.write_response({'error': 'Not found'})

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))

        if self.path == '/clients':
            self.handle_create_client(post_data)
        elif self.path == '/contacts':
            self.handle_create_contact(post_data)
        elif self.path == '/link_contact_to_client':
            self.linked_controller.link_contact_to_client(post_data, self._set_headers, self.write_response)
        else:
            self._set_headers(404)
            self.write_response({'error': 'Not found'})

    def write_response(self, data):
        self.wfile.write(json.dumps(data).encode())

    def do_DELETE(self):
        if self.path.startswith('/unlink_contact_from_client/'):
            self.linking_controller.unlink_contact_from_client(self.path, self._set_headers, self.write_response)
        elif self.path.startswith('/unlink_client_from_contact/'):
            self.linking_controller.unlink_client_from_contact(self.path, self._set_headers, self.write_response)
        else:
            self._set_headers(404)
            self.write_response({'error': 'Not found'})

    def handle_list(self, list_method, resource_name):
        resources = list_method()
        self._set_headers()
        self.wfile.write(json.dumps(resources).encode())

    def handle_list_clients(self):
        self.handle_list(self.client_controller.list_clients, 'Clients')

    def handle_list_contacts(self):
        self.handle_list(self.contact_controller.list_contacts, 'Contacts')

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
            if e.errno == 1062:  # Duplicate entry
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'Email already exists'}).encode())
            else:
                self._set_headers(500)
                self.wfile.write(json.dumps({'error': 'Internal Server Error'}).encode())



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
