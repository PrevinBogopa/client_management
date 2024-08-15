class Contact:
    def __init__(self, db, id=None, name='', email=''):
        self.db = db
        self.id = id
        self.name = name
        self.email = email