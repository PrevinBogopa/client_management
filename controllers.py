import mysql

from models import Client, Contact, Database

class ClientController:
    def __init__(self):
        self.db = Database()
        self.client_model = Client(self.db)
        self.contact_model = Contact(self.db)  # Add Contact model for counting linked contacts


    def create_client(self, name):
        client_code = self.generate_client_code(name)
        self.client_model.create(name, client_code)
        return client_code

    def list_clients(self):
        clients = self.client_model.list()

        # Add the number of linked contacts to each client
        for client in clients:
            client['contact_count'] = self.contact_model.count_linked_contacts(client['id'])

        return clients

    def generate_client_code(self, name):
        code = ''.join([c for c in name[:3].upper() if c.isalpha()]).ljust(3, 'A')
        counter = 1
        generated_code = f"{code}{counter:03d}"

        while self.client_model.get_by_code(generated_code):
            counter += 1
            generated_code = f"{code}{counter:03d}"

        return generated_code

    def get_by_code(self, client_code):
        return self.client_model.get_by_code(client_code)  # Ensure this method is present


class ContactController:
    def __init__(self, client_controller):
        self.db = Database()
        self.contact_model = Contact(self.db)
        self.client_controller = client_controller  # Inject ClientController instance

    def create_contact(self, name, surname, email):
        self.contact_model.create(name, surname, email)

    def list_contacts(self):
        return self.contact_model.list()

    def link_contact_to_client(self, client_code, contact_email):
        # Retrieve client and contact based on provided code and email
        client = self.client_controller.get_by_code(client_code)
        contact = self.contact_model.get_by_email(contact_email)

        # Check if both client and contact exist
        if not client:
            raise Exception(f"Client with code '{client_code}' not found")
        if not contact:
            raise Exception(f"Contact with email '{contact_email}' not found")

        client_id = client['id']
        contact_id = contact['id']

        # Log the IDs that will be linked
        print(f"Checking link status for client ID: {client_id} and contact ID: {contact_id}")

        # Check if the link already exists
        check_query = "SELECT * FROM client_contacts WHERE client_id = %s AND contact_id = %s"
        existing_link = self.db.fetch_one(check_query, (client_id, contact_id))

        if existing_link:
            print(f"Client '{client_code}' and Contact '{contact_email}' are already linked.")
            raise Exception(f"Client '{client_code}' and Contact '{contact_email}' are already linked.")

        # Prepare the SQL query to link client and contact
        query = "INSERT INTO client_contacts (client_id, contact_id) VALUES (%s, %s)"

        try:
            self.db.execute_query(query, (client_id, contact_id))
            print(f"Successfully linked contact {contact_email} to client {client_code}")
        except mysql.connector.errors.IntegrityError as e:
            # Handle duplicate entry error (although it shouldn't reach here due to the earlier check)
            if e.errno == 1062:
                print(f"Duplicate entry: Client {client_code} is already linked to Contact {contact_email}")
                raise Exception(f"Contact '{contact_email}' is already linked to Client '{client_code}'")
            else:
                # Handle other potential database errors
                raise Exception(f"Database error occurred: {e}")
        except Exception as e:
            # General error handling
            raise Exception(f"An unexpected error occurred: {e}")
