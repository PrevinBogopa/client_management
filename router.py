import json
from http.server import BaseHTTPRequestHandler

from controllers.controllers import ClientController, ContactController
from controllers.creation_controller import CreationController
from controllers.linked_controller import LinkedController
from controllers.linking_controller import LinkingController


class RequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.client_controller = ClientController()
        self.contact_controller = ContactController(self.client_controller)
        self.linking_controller = LinkingController(self.client_controller, self.contact_controller)
        self.linked_controller = LinkedController(self.client_controller, self.contact_controller)
        self.creation_controller = CreationController(self.client_controller, self.contact_controller)
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
        try:
            response = self.creation_controller.create_client(data)
            self._set_headers(201)
            self.wfile.write(json.dumps(response).encode())
        except ValueError as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Internal Server Error'}).encode())

    def handle_create_contact(self, data):
        try:
            response = self.creation_controller.create_contact(data)
            self._set_headers(201)
            self.wfile.write(json.dumps(response).encode())
        except ValueError as e:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': str(e)}).encode())
        except Exception as e:
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': 'Internal Server Error'}).encode())


