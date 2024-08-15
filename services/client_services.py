from models.clients_model import Client
from models.contacts_model import Contact
from models.database_model import Database


class ClientService:
    def __init__(self):
        self.db = Database()
        self.client_model = Client(self.db)
        self.contact_model = Contact(self.db)

    def create_client(self, data):
        name = data.get('name')
        if not name:
            raise ValueError("Name is required")

        client_code = self.generate_client_code(name)
        self.create(name, client_code)

        return {'message': f"Client '{name}' created", 'client_code': client_code}

    def create(self, name, client_code):
        query = "INSERT INTO clients (name, client_code) VALUES (%s, %s)"
        self.db.execute_query(query, (name, client_code))

    def list(self):
        query = "SELECT id, name, client_code FROM clients ORDER BY name ASC"
        return self.db.fetch_all(query)

    def list_clients(self):
        clients = self.list()

        # Add the number of linked contacts to each client
        for client in clients:
            client['contact_count'] = self.count_linked_contacts(client['id'])

        return clients

    def count_linked_contacts(self, client_id):
        query = """
        SELECT COUNT(DISTINCT contact_id) AS count 
        FROM relationships 
        WHERE client_id = %s
        """
        result = self.db.fetch_one(query, (client_id,))
        return result['count'] if result else 0

    def list_linked_clients(self, contact_id):
        query = """
        SELECT 
            c.id, c.name, c.client_code
        FROM 
            clients c
            JOIN relationships cc ON c.id = cc.client_id
        WHERE 
            cc.contact_id = %s
        ORDER BY 
            c.name ASC
        """
        return self.db.fetch_all(query, (contact_id,))

    def generate_client_code(self, name):
        words = name.split()
        code = ''.join([word[0].upper() for word in words[:3]])

        if len(code) < 3:
            code = code.ljust(3, 'A')

        counter = 1
        generated_code = f"{code}{counter:03d}"

        while self.get_by_code(generated_code):
            counter += 1
            generated_code = f"{code}{counter:03d}"

        return generated_code



    def get_by_code(self, client_code):
        query = "SELECT id, name, client_code FROM clients WHERE client_code = %s"
        result = self.db.fetch_one(query, (client_code,))
        if result:
            return Client(id=result['id'], name=result['name'], client_code=result['client_code'])
        return None
