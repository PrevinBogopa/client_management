from models import Client, Contact, Database


class ClientController:
    def __init__(self):
        self.db = Database()
        self.client_model = Client(self.db)

    def create_client(self, name):
        client_code = self.generate_client_code(name)
        self.client_model.create(name, client_code)
        return client_code

    def list_clients(self):
        return self.client_model.list()

    def generate_client_code(self, name):
        code = ''.join([c for c in name[:3].upper() if c.isalpha()]).ljust(3, 'A')
        counter = 1
        generated_code = f"{code}{counter:03d}"

        while self.client_model.get_by_code(generated_code):
            counter += 1
            generated_code = f"{code}{counter:03d}"

        return generated_code


class ContactController:
    def __init__(self):
        self.db = Database()
        self.contact_model = Contact(self.db)

    def create_contact(self, name, surname, email):
        self.contact_model.create(name, surname, email)

    def list_contacts(self):
        return self.contact_model.list()

    def link_contact_to_client(self, client_code, contact_email):
        client = self.client_model.get_by_code(client_code)
        contact = self.contact_model.get_by_email(contact_email)

        if not client or not contact:
            raise Exception("Client or Contact not found")

        self.contact_model.link_to_client(client['id'], contact['id'])
