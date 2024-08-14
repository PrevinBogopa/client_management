from services.relationship_service import RelationshipService


class RelationshipController:
    def __init__(self, relationship_service: RelationshipService):
        self.relationship_service = relationship_service

    def list_linked_contacts(self, path, set_headers, write_response):
        client_id = path.split('/')[2]
        try:
            linked_contacts = self.relationship_service.list_linked_contacts(client_id)
            set_headers()
            write_response(linked_contacts)
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})

    def list_linked_clients(self, path, set_headers, write_response):
        contact_email = path.split('/')[2]
        try:
            linked_clients = self.relationship_service.list_linked_clients(contact_email)
            set_headers()
            write_response(linked_clients)
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})

    def link_contact_to_client(self, data, set_headers, write_response):
        client_codes = data.get('client_code')
        contact_emails = data.get('contact_email')
        try:
            response = self.relationship_service.link_contact_to_client(client_codes, contact_emails)
            set_headers(200 if not response['errors'] else 207)
            write_response(response)
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})

    def unlink_client_from_contact(self, path, set_headers, write_response):
        try:

            parts = path.split('/')
            if len(parts) < 4:
                set_headers(400)
                write_response({'error': 'Invalid URL format'})
                return

            client_code = parts[3]
            contact_email = parts[2]

            self.relationship_service.unlink_client_from_contact(client_code, contact_email)

            set_headers(200)
            write_response({'message': f"Client '{client_code}' unlinked from contact '{contact_email}'"})
        except Exception as e:
            print(f"Error: {str(e)}")  # Log the error for debugging
            set_headers(500)
            write_response({'error': str(e)})

    def unlink_contact_from_client(self, path, set_headers, write_response):
        parts = path.split('/')
        client_code = parts[2]
        contact_email = parts[3]
        try:
            self.relationship_service.unlink_contact_from_client(client_code, contact_email)
            set_headers(200)
            write_response({'message': f"Contact '{contact_email}' unlinked from client '{client_code}'"})
        except Exception as e:
            set_headers(500)
            write_response({'error': str(e)})
