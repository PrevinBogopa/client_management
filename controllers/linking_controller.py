
from .controllers import ClientController, ContactController


class LinkingController:
    def __init__(self, client_controller: ClientController, contact_controller: ContactController):
        self.client_controller = client_controller
        self.contact_controller = contact_controller

    def unlink_client_from_contact(self, path, set_headers, write_response):
        parts = path.split('/')
        if len(parts) != 4:
            set_headers(400)
            write_response({'error': 'Invalid URL format'})
            return

        contact_email = parts[2]
        client_code = parts[3]

        contact = self.contact_controller.get_by_email(contact_email)
        if self.handle_not_found(contact, 'Contact', set_headers, write_response):
            return

        client = self.client_controller.get_by_code(client_code)
        if self.handle_not_found(client, 'Client', set_headers, write_response):
            return

        try:
            self.contact_controller.unlink_client_from_contact(contact['id'], client['id'])
            set_headers(200)
            write_response({'message': f"Client '{client_code}' unlinked from contact '{contact_email}'"})
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})

    def unlink_contact_from_client(self, path, set_headers, write_response):
        parts = path.split('/')
        if len(parts) != 4:
            set_headers(400)
            write_response({'error': 'Invalid URL format'})
            return

        client_code = parts[2]
        contact_email = parts[3]

        client = self.client_controller.get_by_code(client_code)
        if self.handle_not_found(client, 'Client', set_headers, write_response):
            return

        contact = self.contact_controller.get_by_email(contact_email)
        if self.handle_not_found(contact, 'Contact', set_headers, write_response):
            return

        try:
            self.contact_controller.unlink_contact_from_client(client['id'], contact['id'])
            set_headers(200)
            write_response({'message': f"Contact '{contact_email}' unlinked from client '{client_code}'"})
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})

    def link_contact_to_client(self, data, set_headers, write_response):
        client_codes = data.get('client_code')
        contact_emails = data.get('contact_email')

        if not client_codes or not contact_emails:
            set_headers(400)
            write_response({'error': 'Client code(s) and contact email(s) are required'})
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

        set_headers(200 if not errors else 207)  # 207 Multi-Status for partial success
        write_response(response)

    def handle_not_found(self, resource, resource_name, set_headers, write_response):
        if not resource:
            set_headers(404)
            write_response({'error': f'{resource_name} not found'})
            return True
        return False
