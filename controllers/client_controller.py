
from services.client_services import ClientService
class ClientController:
    def __init__(self):
        self.client_service = ClientService()

    def create(self, data):
        return self.client_service.create_client(data)

    def list(self):
        return self.client_service.list_clients()

    def list_linked_clients(self, contact_id):
        return self.client_service.list_linked_clients(contact_id)

    def get_by_code(self, client_code):
        return self.client_service.get_by_code(client_code)
