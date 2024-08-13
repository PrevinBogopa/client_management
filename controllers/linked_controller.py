# linked_controller.py
class LinkedController:
    def __init__(self, client_controller, contact_controller):
        self.client_controller = client_controller
        self.contact_controller = contact_controller

    def list_linked_contacts(self, path, set_headers, write_response):
        client_id = path.split('/')[2]  # Extract client_id from the URL
        try:
            linked_contacts = self.contact_controller.list_linked_contacts(client_id)
            set_headers()
            write_response(linked_contacts)
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})

    def list_linked_clients(self, path, set_headers, write_response):
        parts = path.split('/')
        if len(parts) != 3:
            set_headers(400)
            write_response({'error': 'Invalid URL format'})
            return

        contact_email = parts[2]
        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            set_headers(404)
            write_response({'error': 'Contact not found'})
            return

        try:
            linked_clients = self.client_controller.list_linked_clients(contact['id'])
            set_headers()
            write_response(linked_clients)
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

    def list_linked_clients_for_contact(self, path, set_headers, write_response):
        # Extract contact email from the URL
        parts = path.split('/')
        if len(parts) != 4:
            set_headers(400)
            write_response({'error': 'Invalid URL format'})
            return

        contact_email = parts[2]

        # Get contact information
        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            set_headers(404)
            write_response({'error': 'Contact not found'})
            return

        # List linked clients for the contact
        try:
            clients = self.client_controller.list_linked_clients(contact['id'])
            set_headers()
            write_response(clients)
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})
