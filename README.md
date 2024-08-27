
# SecureSkyScholars

Student Management App in Django and Mysql

  

![Build Status](https://github.com/chandrima0503/SecureSkyScholars/actions/workflows/django.yml/badge.svg)

  

## Installation Steps

  

### 1. Clone the Repository

  

First, clone the repository to your local machine:

  

```bash

git  clone  https://github.com/chandrima0503/SecureSkyScholars.git

cd  SecureSkyScholars
```

### 2. Project Dependency :

To  install  the  project  dependencies,  run  the  following  command:

```bash

pip install -r requirements.txt
```
  
### 3. Create MySQL Database:

Create the database in MySQL. You can do this using a MySQL client or command line tool.

```bash
create database studentManagementSystem
```

### 4. Configure Database Settings:

Update the `settings.py` file in your Django project to configure the database settings. Replace the default settings with the following configuration for MySQL:

```bash
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'studentManagementSystem',
        'USER': 'your_mysql_user',
        'PASSWORD': 'your_mysql_password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```
Replace `'your_mysql_user'` and `'your_mysql_password'` with your actual MySQL username and password.

### 5.  Run Migration Commands

Apply the migrations to set up your database schema:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6.  Run the Project

Start the Django development server:

```bash
python manage.py runserver
```
Navigate to `http://127.0.0.1:8000/` in your web browser to see the application in action.

###   Continuous Integration

This project uses GitHub Actions for Continuous Integration (CI). The CI pipeline automatically builds and tests the project on every push or pull request to the `main` branch. The current build status is displayed by the badge above.

###   Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request. Make sure to follow the project's coding standards and write tests for new features or bug fixes.

###   License

This project is licensed under the MIT License - see the [LICENSE](http://ionden.com/a/plugins/licence-en.html) file for details.


This file includes:
- **Clone the Repository**: Step to clone and navigate to the project directory.
- **Project Dependency**: Instructions for installing dependencies.
- **Create MySQL Database**: SQL command to create the database.
- **Configure Database Settings**: Configuration for `settings.py`.
- **Run Migration Commands**: Commands for setting up the database schema.
- **Run the Project**: Command to start the Django development server.
- **Continuous Integration**: Information about the CI setup.
- **Contributing**: Guidelines for contributing to the project.
- **License**: Licensing information.

This comprehensive `README.md` provides all necessary instructions for setting up and running your Django project.

