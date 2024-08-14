Certainly! Here's a reformatted version of the README content with consistent styling:

---

# **DataCapture Backend**

## **Overview**

DataCapture is a Python-based backend application built using the Model-View-Controller (MVC) architectural pattern and Object-Oriented Programming (OOP) principles. This repository contains the backend logic, with a separate repository for the React-based frontend (link below).

## **Repository Structure**

The repository is organized into the following main directories:

- **app.py**  
  The main application entry point.

- **controllers/**  
  Contains the controller modules, responsible for handling business logic.
  - **controllers.py:**  
    Base controller class.
  - **creation_controller.py:**  
    Handles data creation logic.
  - **linked_controller.py:**  
    Handles linked data logic.
  - **linking_controller.py:**  
    Handles data linking logic.

- **models/**  
  Contains the model modules, representing the data structure and database interactions.
  - **clients_model.py:**  
    Represents the clients data model.
  - **contacts_model.py:**  
    Represents the contacts data model.
  - **database_model.py:**  
    Handles database interactions.

## **Features**

- Built using Python, with a focus on MVC and OOP principles.
- Utilizes MySQL as the database management system.
- Designed to work seamlessly with the React-based frontend (see link below).

## **Frontend Repository**

The frontend repository can be found at: [insert link to React frontend repo]

## **Getting Started**

To get started with the project, ensure you have Python and MySQL installed on your system. Clone the repository, navigate to the project directory, and install the required dependencies using pip:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory and add your environment variables (e.g., database credentials).

Run the application using:

```bash
python app.py
```

## **Application Structure**

The application uses the following modules:

- `http.server:`  
  Provides the HTTP server functionality.
- `router:`  
  Handles incoming requests and routes them to the appropriate controllers.
- `BaseHTTPRequestHandler:`  
  Handles basic HTTP requests.
- `json:`  
  Handles JSON data parsing and serialization.

### **Controllers**

The application uses the following controllers:

- `creation_controller.py:`  
  Handles data creation logic.
- `linked_controller.py:`  
  Handles linked data logic.
- `linking_controller.py:`  
  Handles data linking logic.

### **Models**

The application uses the following models:

- `clients_model.py:`  
  Represents the clients data model.
- `contacts_model.py:`  
  Represents the contacts data model.
- `database_model.py:`  
  Handles database interactions.

## **Server**

The application uses the following server setup:

```python
from http.server import HTTPServer
from router import RequestHandler
import json
from http.server import BaseHTTPRequestHandler
```

This setup enables the application to handle incoming HTTP requests and route them to the appropriate controllers.

---

Let me know if you need any further adjustments!