
# 📦 StockMaster – Inventory & Order Management System

StockMaster is a web-based inventory and order management application developed with Python and FastAPI.

The application helps businesses manage products, customers, stock levels, orders, and sales reports through a centralized dashboard.

## 🚀 Features

- **User Authentication:** User registration, login, and logout.
- **Multi-User Data Isolation:** Each user can access only their own data.
- **Product Management:** Add, update, and delete products.
- **Customer Management:** Manage customer information.
- **Order Management:** Create orders and calculate total amounts.
- **Stock Tracking:** Automatically decrease stock when an order is created.
- **Low Stock Monitoring:** Track products with low inventory.
- **Sales Reports:** View daily and monthly sales reports.
- **Dashboard:** Monitor products, customers, orders, and sales.

## 📸 Screenshots

### Dashboard
![StockMaster Dashboard](screenshots/dashboard.png)

### Product Management
![Product Management](screenshots/products.png)

### Customer Management
![Customer Management](screenshots/customers.png)

### Order Management
![Order Management](screenshots/orders.png)


## 🛠️ Technologies

- Python 3.9
- FastAPI
- SQLAlchemy
- SQLite
- Jinja2
- Uvicorn
- Passlib
- HTML / CSS / JavaScript

## 📁 Project Structure

```text
StockMaster/
├── app/
│   ├── core/
│   ├── models/
│   ├── routers/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── database.py
│   └── main.py
├── .gitignore
├── requirements.txt
└── README.md
```

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd StockMaster
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:

```powershell
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
SESSION_SECRET_KEY=your-secret-key
```

Use a unique, randomly generated secret key.

### 6. Run the application

```bash
uvicorn app.main:app --reload
```

Open the application:

http://127.0.0.1:8000

API documentation:

http://127.0.0.1:8000/docs

## 🔐 Security

- Passwords are stored as hashes.
- Session-based authentication is implemented.
- User-specific data access is enforced.
- Environment variables are used for session secrets.
- Local database and environment files are excluded from Git.

## 📌 Project Status

The project is under active development.

## 👨‍💻 Developer

Developed as a Python backend development and portfolio project.
