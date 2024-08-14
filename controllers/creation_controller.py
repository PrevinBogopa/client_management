import mysql


class CreationController:
    def __init__(self, client_controller, contact_controller):
        self.client_controller = client_controller
        self.contact_controller = contact_controller

    def create_client(self, data):
        name = data.get('name')
        if not name:
            raise ValueError("Name is required")

        client_code = self.client_controller.create_client(name)
        return {'message': f"Client '{name}' created", 'client_code': client_code}

    def create_contact(self, data):
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')

        if not all([name, surname, email]):
            raise ValueError("Name, surname, and email are required")

        try:
            self.contact_controller.create_contact(name, surname, email)
            return {'message': f"Contact '{name} {surname}' created"}
        except mysql.connector.errors.IntegrityError as e:
            if e.errno == 1062:  # Duplicate entry
                raise ValueError("Email already exists")
            else:
                raise Exception("Internal Server Error")
