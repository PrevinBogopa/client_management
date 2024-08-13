class Contact:
    def __init__(self, db):
        self.db = db

    def count_linked_contacts(self, client_id):
        query = """
        SELECT COUNT(DISTINCT contact_id) AS count 
        FROM client_contacts 
        WHERE client_id = %s
        """
        result = self.db.fetch_one(query, (client_id,))
        return result['count'] if result else 0

    def create(self, name, surname, email):
        query = "INSERT INTO contacts (name, surname, email) VALUES (%s, %s, %s)"
        self.db.execute_query(query, (name, surname, email))

    def list(self):
        query = """
        SELECT 
            c.id, c.name, c.surname, c.email,
            COUNT(cc.client_id) AS linked_clients_count
        FROM 
            contacts c
            LEFT JOIN client_contacts cc ON c.id = cc.contact_id
        GROUP BY 
            c.id, c.name, c.surname, c.email
        ORDER BY 
            c.surname ASC, c.name ASC
        """
        return self.db.fetch_all(query)

    def get_by_email(self, email):
        query = "SELECT id FROM contacts WHERE email = %s"
        return self.db.fetch_one(query, (email,))

    def list_linked_to_client(self, client_id):
        query = """
        SELECT 
            c.id, c.name, c.surname, c.email
        FROM 
            contacts c
            JOIN client_contacts cc ON c.id = cc.contact_id
        WHERE 
            cc.client_id = %s
        ORDER BY 
            c.surname ASC, c.name ASC
        """
        return self.db.fetch_all(query, (client_id,))

    def unlink_from_client(self, client_id, contact_id):
        query = "DELETE FROM client_contacts WHERE client_id = %s AND contact_id = %s"
        self.db.execute_query(query, (client_id, contact_id))

    def link_to_client(self, client_id, contact_id):
        query = "INSERT INTO client_contacts (client_id, contact_id) VALUES (%s, %s)"
        self.db.execute_query(query, (client_id, contact_id))