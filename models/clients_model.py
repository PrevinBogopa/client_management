class Client:
    def __init__(self, db):
        self.db = db

    def create(self, name, client_code):
        query = "INSERT INTO clients (name, client_code) VALUES (%s, %s)"
        self.db.execute_query(query, (name, client_code))

    def list(self):
        query = "SELECT id, name, client_code FROM clients ORDER BY name ASC"
        return self.db.fetch_all(query)

    def get_by_code(self, client_code):
        query = "SELECT id FROM clients WHERE client_code = %s"
        return self.db.fetch_one(query, (client_code,))
