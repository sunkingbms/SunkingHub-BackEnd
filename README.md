# Sunking Hub Django REST Auth + Google Login + RBAC API

### Overview

This project is a **production-grade Django REST API** implementing:
- Email/password authentication using **dj-rest-auth**
- Google login (token-based, no redirects)
- Role-Based Access Control (RBAC) with **Groups & Permissions**
- Admin user CRUD management
- Clean modular structure under `apps/`

## Installation and Setup

### 1️ Clone the Repository

```bash
    git clone https://github.com/<your-org>/<your-repo>.git
    cd SunkingHub-Backend
```

### 2 Activate skhubenv Virtual Environment
```bash
source skhubenv/bin/activate #(macos only)
```

### 3 Installing required packages
```bash
pip install -r requirements/dev.txt
```

### 4 Create an .env file and paste Django key shared from chat
```bash
# ensure you are in the project folder's root
touch .env
```

### 5 Apply migrations (For local development use the sqlite db)

```bash
python manage.py makemigrations #Please ensure you are in the project root
python manage.py migrate
```

### 6 Run development server
```bash
python manage.py runserver

```

## Endpoints overview(upcoming)


