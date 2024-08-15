import mysql

from models.contacts_model import Contact
from models.database_model import Database


class ContactService:
    def __init__(self, client_controller):
        self.db = Database()
        self.contact_model = Contact(self.db)
        self.client_controller = client_controller

    def get_by_email(self, email):
        query = "SELECT id FROM contacts WHERE email = %s"
        return self.db.fetch_one(query, (email,))

    def unlink_client_from_contact(self, contact_id, client_id):
        query = "DELETE FROM relationships WHERE contact_id = %s AND client_id = %s"
        self.db.execute_query(query, (contact_id, client_id))

    def list_linked_contacts(self, client_code):
        client = self.client_controller.get_by_code(client_code)
        if not client:
            raise Exception(f"Client with code '{client_code}' not found")

        client_id = client.id  # Correct: Access attribute using dot notation
        return self.list_linked_to_client(client_id)

    def list_linked_to_client(self, client_id):
        query = """
        SELECT 
            c.id, c.name, c.surname, c.email
        FROM 
            contacts c
            JOIN relationships r ON c.id = r.contact_id
        WHERE 
            r.client_id = %s
        ORDER BY 
            c.surname ASC, c.name ASC
        """
        return self.db.fetch_all(query, (client_id,))

    def unlink_contact_from_client(self, client_id, contact_id):
        query = "DELETE FROM relationships WHERE client_id = %s AND contact_id = %s"
        self.db.execute_query(query, (client_id, contact_id))

    def create_contact(self, data):
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')

        if not all([name, surname, email]):
            raise ValueError("Name, surname, and email are required")

        try:
            self.create(name, surname, email)
            return {'message': f"Contact '{name} {surname}' created"}
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:  # Duplicate entry
                raise ValueError("Email already exists")
            else:
                raise Exception("Internal Server Error")

    def create(self, name, surname, email):
        query = "INSERT INTO contacts (name, surname, email) VALUES (%s, %s, %s)"
        self.db.execute_query(query, (name, surname, email))

    def list_contacts(self):
        query = """
        SELECT 
            c.id, c.name, c.surname, c.email,
            COUNT(r.client_id) AS linked_clients_count
        FROM 
            contacts c
            LEFT JOIN relationships r ON c.id = r.contact_id
        GROUP BY 
            c.id, c.name, c.surname, c.email
        ORDER BY 
            c.surname ASC, c.name ASC
        """
        return self.db.fetch_all(query)

    def get_by_code(self, client_code):
        query = "SELECT id FROM clients WHERE client_code = %s"
        return self.db.fetch_one(query, (client_code,))

    def link_contact_to_client(self, client_code, contact_email):
        client = self.client_controller.get_by_code(client_code)
        contact = self.get_by_email(contact_email)

        if not client:
            raise Exception(f"Client with code '{client_code}' not found")
        if not contact:
            raise Exception(f"Contact with email '{contact_email}' not found")

        client_id = client.id
        contact_id = contact['id']

        check_query = "SELECT * FROM relationships WHERE client_id = %s AND contact_id = %s"
        existing_link = self.db.fetch_one(check_query, (client_id, contact_id))

        if existing_link:
            raise Exception(f"Client '{client_code}' and Contact '{contact_email}' are already linked.")

        query = "INSERT INTO relationships (client_id, contact_id) VALUES (%s, %s)"

        try:
            self.db.execute_query(query, (client_id, contact_id))
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:
                raise Exception(f"Contact '{contact_email}' is already linked to Client '{client_code}'")
            else:
                raise Exception(f"Database error occurred: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {e}")
