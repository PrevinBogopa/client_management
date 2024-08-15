
from services.contact_services import ContactService
class ContactController:
    def __init__(self, client_controller):
        self.contact_service = ContactService(client_controller)
    def create(self, data):
        return self.contact_service.create_contact(data)

    def get_by_email(self, email):
        return self.contact_service.get_by_email(email)

    def unlink_client_from_contact(self, contact_id, client_id):
        self.contact_service.unlink_client_from_contact(contact_id, client_id)

    def list_linked_contacts(self, client_code):
        return self.contact_service.list_linked_contacts(client_code)

    def unlink_contact_from_client(self, client_id, contact_id):
        self.contact_service.unlink_contact_from_client(client_id, contact_id)


    def list(self):
        return self.contact_service.list_contacts()

    def link_contact_to_client(self, client_code, contact_email):
        self.contact_service.link_contact_to_client(client_code, contact_email)

