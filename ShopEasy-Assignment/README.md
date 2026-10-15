ShopEasy – E-commerce Application

Project Overview

ShopEasy is an e-commerce web application developed using Python and Flask. This project demonstrates two software architectures: Monolithic Architecture and Microservices Architecture.

Technologies Used

* Python
* Flask
* HTML
* CSS
* JavaScript
* REST APIs

1. Monolithic Architecture

In the monolithic version, product management and order management are handled within a single Flask application.

Port: 5003

2. Microservices Architecture

In the microservices version, the application is divided into three separate services:

* Main Application: Handles the website and communicates with other services.
* Product Service: Manages product information.
* Order Service: Handles customer orders.

Ports:

* Main Application: 5000
* Product Service: 5001
* Order Service: 5002

How to Run

Monolithic Application

1. Open the monolithic folder.
2. Install dependencies using python -m pip install -r requirements.txt.
3. Run python app.py.
4. Open http://127.0.0.1:5003 in a browser.

Microservices Application

1. Open the microservices folder.
2. Install dependencies using python -m pip install -r requirements.txt.
3. Run the main application, product service, and order service in separate terminals.
4. Open http://127.0.0.1:5000 in a browser.

Assignment Objective

To develop and compare an e-commerce application using Monolithic and Microservices architectures.

Screenshots

Screenshots of both applications are included in the screenshots folder.