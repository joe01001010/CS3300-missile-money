# 🚀 Missile Money

A Django-based personal finance management web application designed to help users track, analyze, and optimize their money with an intuitive interface.

## 📋 Project Overview

**Missile Money** addresses the complexity of modern personal finance management by providing key capabilities that other similar apps often lack. Our platform helps users manage their finances, track subscriptions, budget effectively, and make informed financial decisions.

### Key Differentiators
- Proper "split the bill" functionality that doesn't count shared payments as income
- Comprehensive transaction categorization
- Intuitive user interface for everyday financial tracking
- Secure data encryption and privacy-first approach

## 👥 Team

- **Joe Weibel** - Scrum Master & Tester
- **Jakob West** - Software Architect

## 🛠️ Technology Stack

- **Language**: Python 3.10+
- **Framework**: Django (web framework)
- **Database**: PostgreSQL (SQLite3 for development)
- **Frontend**: HTML, CSS, JavaScript/TypeScript
- **Version Control**: GitHub
- **CI/CD**: GitHub Actions
- **Testing**: Django's built-in test framework, Selenium
- **Project Management**: GitHub Projects

## ✨ Features

### Current Features
- ✅ User authentication (register, login, logout)
- ✅ Auto-logout after 15 minutes of inactivity
- ✅ Financial dashboard with balance overview
- ✅ Add income and expense transactions
- ✅ Edit and delete transactions
- ✅ Monthly income and expense tracking
- ✅ Dark mode theme toggle
- ✅ User feedback system
- ✅ Responsive UI design
- ✅ Savings goals tracking
- ✅ Spending categorization and budgeting
- ✅ Financial analytics and reports
- ✅ Peer-to-peer payments

### Planned Features
- 🔄 Currency conversation
- 🔄 Recurring payments management
- 🔄 Split the bill functionality
- 🔄 Export transaction data (CSV/Excel)
- 🔄 Multiple account support

## 🏗️ Architecture

Missile Money follows Django's MVT (Model-View-Template) architecture:

- **Models**: User, Transaction, Profile, Account, Subscription, etc.
- **Views**: Handle business logic and user interactions
- **Templates**: HTML templates with responsive design
- **Static Files**: CSS, JavaScript for frontend functionality

See our [Project Architecture Diagram](docs/architecture.md) for detailed system design.

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

---

### Installation for Linux/WSL/Mac

#### 1. Clone the repository
```bash
git clone https://github.com/your-org/CS3300-missile-money.git
cd CS3300-missile-money
```

#### 2. Create a virtual environment
```bash
python3 -m venv venv
```

#### 3. Activate the virtual environment
```bash
source venv/bin/activate
```

#### 4. Install dependencies
```bash
pip install -r requirements.txt
```

#### 5. Navigate to the Django project directory
```bash
cd missile_money
```

#### 6. Run database migrations
```bash
python manage.py migrate
```

#### 7. (Optional) Create a superuser for admin access
```bash
python manage.py createsuperuser
```

#### 8. Run the development server
```bash
python manage.py runserver
```

#### 9. Access the application
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

### Installation for Windows (PowerShell)

#### 1. Clone the repository
```powershell
git clone https://github.com/your-org/CS3300-missile-money.git
cd CS3300-missile-money
```

#### 2. Create a virtual environment
```powershell
python -m venv venv
```

#### 3. Activate the virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

**Note:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### 4. Install dependencies
```powershell
pip install -r requirements.txt
```

#### 5. Navigate to the Django project directory
```powershell
cd missile_money
```

#### 6. Run database migrations
```powershell
python manage.py migrate
```

#### 7. (Optional) Create a superuser for admin access
```powershell
python manage.py createsuperuser
```

#### 8. Run the development server
```powershell
python manage.py runserver
```

#### 9. Access the application
- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

---

## 🧪 Testing

### Run all tests
```bash
python manage.py test
```

### Run specific test class (example)
```bash
python manage.py test main.tests.TransactionEditDeleteTestCase
```

### Run tests with verbose output
```bash
python manage.py test --verbosity=2
```

## 📊 Automated Testing

Our CI/CD pipeline runs automatically on every push and pull request to the `main` branch. We currently have **18 automated tests** covering:

1. Home page accessibility
2. About page accessibility
3. Dashboard authentication
4. Profile page authentication
5. User registration
6. User login
7. User logout
8. Auto-logout after inactivity
9. Feedback submission
10. Transaction tracking by month
11. Edit transaction page loads
12. Edit transaction updates data
13. Delete transaction page loads
14. Delete transaction removes data
15. Security: users cannot edit others' transactions
16. Security: users cannot delete others' transactions
17. Login required for edit
18. Login required for delete

Tests run across Python versions 3.10, 3.11, 3.12, and 3.13.

## 🔒 Security & Ethics

- **Data Encryption**: All sensitive data encrypted at rest using AES-256
- **Secure Authentication**: Django's built-in authentication with session management
- **User Privacy**: Users have full control over their data
- **GDPR Compliance**: Financial data protection regulations followed
- **Audit Logging**: All transactions logged for security

## 📈 Development Methodology

We follow **Agile/Scrum** methodology with:
- **Sprint Duration**: 2 weeks
- **Sprint Planning**: At the start of each sprint
- **Daily Standups**: Regular team check-ins
- **Sprint Reviews**: Demo completed features
- **Retrospectives**: Continuous improvement


## 🤝 Contributing

### Branching Strategy
1. Create a feature branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```
3. Push your branch
   ```bash
   git push origin feature/your-feature-name
   ```
4. Create a Pull Request on GitHub
5. Wait for code review and approval
6. Merge into `main` after approval

### Commit Message Guidelines
- `Add:` for new features
- `Fix:` for bug fixes
- `Update:` for changes to existing features
- `Remove:` for deleted features
- `Test:` for adding/updating tests

## 📝 Project Requirements

View our complete [Requirements Document](docs/requirements.md) for detailed functional and non-functional requirements.

## 📅 Project Timeline

- **Initial Requirements**: Sep 16 - Sep 25, 2025
- **Architecture Design**: Sep 26 - Sep 28, 2025
- **Software Design**: Sep 29 - Oct 5, 2025
- **Mid-term Presentation**: Oct 7, 2025
- **Development & Testing**: Oct 8 - Dec 1, 2025
- **Final Presentation**: Dec 1, 2025

## 📞 Support

For questions or issues, please:
1. Check existing [GitHub Issues](https://github.com/your-org/CS3300-missile-money/issues)
2. Create a new issue if needed
3. Contact the team via our feedback form in the application