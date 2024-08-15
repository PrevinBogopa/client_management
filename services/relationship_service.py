from models.database_model import Database
from services.contact_services import ContactService


class RelationshipService:
    def __init__(self, client_controller, contact_controller):
        self.db = Database()
        self.client_controller = client_controller
        self.contact_controller = contact_controller

    def list_linked_contacts(self, client_id):
        return self.contact_controller.list_linked_contacts(client_id)

    def list_linked_clients(self, contact_email):
        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            raise ValueError('Contact not found')
        return self.client_controller.list_linked_clients(contact['id'])

    def link_contact_to_client(self, client_codes, contact_emails):
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

        return {
            'linked_contacts': linked_contacts,
            'errors': errors
        }

    def unlink_client_from_contact(self, client_code, contact_email):
        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            raise ValueError('Contact not found')

        client = self.client_controller.get_by_code(client_code)
        if not client:
            raise ValueError('Client not found')

        # Accessing dictionary values rather than attributes
        self.contact_controller.unlink_client_from_contact(contact['id'], client.id)

    def unlink_contact_from_client(self, client_code, contact_email):
        client = self.client_controller.get_by_code(client_code)
        if not client:
            raise ValueError('Client not found')

        contact = self.contact_controller.get_by_email(contact_email)
        if not contact:
            raise ValueError('Contact not found')

        self.contact_controller.unlink_contact_from_client(client.id, contact['id'])
