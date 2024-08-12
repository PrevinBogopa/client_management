import mysql.connector

class Database:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Aurelia@30',
            database='client_management'
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_all(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query, params=None):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def __del__(self):
        # Close the cursor and connection when the object is destroyed
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

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

class Contact:
    def __init__(self, db):
        self.db = db
    def count_linked_contacts(self, client_id):
        query = "SELECT COUNT(*) AS count FROM client_contacts WHERE client_id = %s"
        result = self.db.fetch_one(query, (client_id,))
        return result['count'] if result else 0
    def create(self, name, surname, email):
        query = "INSERT INTO contacts (name, surname, email) VALUES (%s, %s, %s)"
        self.db.execute_query(query, (name, surname, email))

    def list(self):
        query = "SELECT id, name, surname, email FROM contacts ORDER BY surname ASC, name ASC"
        return self.db.fetch_all(query)

    def get_by_email(self, email):
        query = "SELECT id FROM contacts WHERE email = %s"
        return self.db.fetch_one(query, (email,))

    def link_to_client(self, client_id, contact_id):
        query = "INSERT INTO client_contacts (client_id, contact_id) VALUES (%s, %s)"
        self.db.execute_query(query, (client_id, contact_id))
