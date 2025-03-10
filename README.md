# Coderr-Backend

## Description / Characteristics
Coderr-Backend is a Django-based Offer Management System designed for the Coderr application. It facilitates the creation, retrieval, and management of offers, orders, and user profiles. Built with Django and Django REST Framework, it provides comprehensive backend functionality, including user authentication, filtering, pagination, validation, and APIs for offers, orders, and reviews.


### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL or SQLite (for development purposes)
- Pipenv or virtualenv (recommended)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/M-Nafi/Coderr-Backend.git
   cd coderr_backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv env
   source env/bin/activate # Linux/Mac
   env\Scripts\activate # Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- **POST /login/**: Log in and retrieve an authentication token.
- **POST /registration/**: Register a new user.

### User Profiles
- **GET /profile/{id}/**: Retrieve details of a user profile.
- **PATCH /profile/{id}/**: Update profile details (authenticated users only).
- **GET /profiles/business/**: Retrieve a list of all business profiles.
- **GET /profiles/customer/**: Retrieve a list of all customer profiles.

### Offers
- **GET /offers/**: Retrieve a list of all offers (supports filtering and pagination).
- **POST /offers/**: Create a new offer.
- **GET /offers/{id}/**: Retrieve details of a specific offer.
- **PATCH /offers/{id}/**: Update details of a specific offer.
- **DELETE /offers/{id}/**: Delete an offer.
- **GET /offerdetails/{id}/**: Retrieve details of a specific offer detail.

### Orders
- **GET /orders/**: List orders for the logged-in user.
- **POST /orders/**: Create a new order based on an offer.
- **GET /orders/{id}/**: Retrieve details of a specific order.
- **PATCH /orders/{id}/**: Update the status of a specific order.
- **DELETE /orders/{id}/**: Delete an order (admin only).

### Reviews
- **GET /reviews/**: Retrieve a list of all reviews.
- **POST /reviews/**: Create a new review (authenticated users only).
- **GET /reviews/{id}/**: Retrieve details of a specific review.
- **PATCH /reviews/{id}/**: Update a review (owner or admin only).
- **DELETE /reviews/{id}/**: Delete a review (owner or admin only).


### Guest Access

Two guest access accounts have been pre-configured for testing purposes:
    
    ```
    const GUEST_LOGINS = {
        customer: {
            username: "andrey",
            password: "asdasd",
        },
        business: {
            username: "kevin",
            password: "asdasd",
        },
    };
    ```

You can use these accounts to log in and test the application with pre-defined roles: Customer and Business. 

## Checklist
[Checklist](checklist_coderr.pdf)

## Endpoint Documentation
[Documentation](coderr_documentation_endpoints.pdf)


## License
This project is licensed under the MIT License.
