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
            # Split the path to extract parameters
            parts = path.strip('/').split('/')

            # Validate URL format
            if len(parts) < 3:
                set_headers(400)
                write_response({'error': 'Invalid URL format'})
                return

            # Extract client_code and contact_email
            contact_email = parts[1]  # Corrected index
            client_code = parts[2]  # Corrected index

            # Call the service method to perform the unlinking
            self.relationship_service.unlink_client_from_contact(client_code, contact_email)

            # Send success response
            set_headers(200)
            write_response({'message': f"Client '{client_code}' unlinked from contact '{contact_email}'"})
        except ValueError as ve:
            # Handle specific ValueErrors
            print(f"Error: {str(ve)}")
            set_headers(400)
            write_response({'error': str(ve)})
        except Exception as e:
            # Handle other exceptions
            print(f"Error: {str(e)}")
            set_headers(500)
            write_response({'error': 'Internal Server Error'})

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
