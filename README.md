# CycleShop

## Project Overview
CycleShop is an e-commerce application for cycling products. Built using Django, it integrates Stripe for payments and provides a user-friendly, full-stack solution for managing an online store.

## Setup Instructions
1. Clone the repository.
2. Create and activate a virtual environment.
3. Run `python manage.py runserver` to start the application.

# Features

## Current Features:

**Product Listing**: Users can view a list of products, including product names, descriptions, prices, and stock availability.

**Product Details**: Users can click on individual products to view more detailed information.

**Admin Panel**: Site administrators can add, edit, and delete products from the catalog using Django's admin interface.

**Responsive Design**: The site is fully responsive, built using Bootstrap for an optimal experience on all devices.

**Product Categories**: Products are categorized into Mountain Bikes, Electric Bikes, Kids Bikes, Clothing, and Accessories.

**Shopping Cart**: Add items to a cart (toast notification) and track them throughout the session.

**User Authentication**: Users can register, log in, and manage their accounts.

**Search Functionality**: Users can search for products using the search bar.

**Wishlist**: Users can save items to their wishlist for future purchase consideration.

**Responsive Design**: Fully responsive layout using Bootstrap.

**Image Uploads**: Product images are uploaded and managed through Django’s `ImageField`.

**Free Delivery Banner**: Offers free delivery for orders over €500.

**Newsletter Subscription**: Users can subscribe to the newsletter.


## Technologies Used

- **Frontend**: 
  - HTML, CSS (Bootstrap 5)
  - JavaScript
- **Backend**:
  - Django 5.1.1 (Python)
  - SQLite (Development)
  - PostgresSQL
  - Django AllAuth (User Authentication)
  - Django Forms
- **Database**: 
  - SQLite for development
  - PostgresSQL
  **Payment Gateway**: Stripe API
- **Media Handling**: Django's `ImageField` for handling image uploads.

## Setup Instructions

### The Repository

### Create and Activate a Environment:

### Set up Environment Variables:

Create an env.py file with the following contents:

import os

os.environ['SECRET_KEY'] = 'your_secret_key'
os.environ['DATABASE_URL'] = 'your_database_url'
os.environ['STRIPE_PUBLIC_KEY'] = 'your_stripe_public_key'
os.environ['STRIPE_SECRET_KEY'] = 'your_stripe_secret_key'

### Run Migrations:

python manage.py migrate


### Create a Superuser:

python manage.py createsuperuser

### Run the Application:

python manage.py runserver

## Credits

Accordian - https://djangosnippets.org/snippets/10658/

Wishlist - https://pythongeeks.org/python-django-wishlist-project/

