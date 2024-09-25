# Hexaware Hackathon

## Project Name

This project is built using Django and integrates OpenAI's API.

## Installation

1. **Clone the repository:**
    ```bash
    git clone "https://github.com/Nithishkumar2004/Hexaware-hackathon"
    cd "Hexaware-hackathon"
    ```

2. **Set up a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    ```
    - On Mac:
      ```bash
      source venv/bin/activate 
      ```
    - On Windows:
      ```bash
      venv\Scripts\activate.bat
      ```

3. **Install required dependencies:**
    ```bash
    pip install django python-decouple python-dotenv openai==0.28 pymongo pytz djongo
    pip install --upgrade djongo

    ```

4. **Configure environment variables:**
   - On Mac/Linux:
     ```bash
     touch .env
     ```
   - On Windows:
     ```bash
     echo. > .env
     ```

5. **Open the `.env` file and add the following:**
    ```env
    # Django settings
    SECRET_KEY='your_django_secret_key'
    DEBUG=True

    # OpenAI API key
    OPENAI_API_KEY='your_openai_api_key'

    # Email settings
    EMAIL_HOST_USER='your_email@example.com'
    EMAIL_HOST_PASSWORD='your_email_password'

    # MongoDB connection settings
    MONGO_URI='your_mongodb_connection_uri'
    DB_NAME='your_database_name'
    DB_HOST='your_mongodb_host'
    DB_USER='your_mongodb_username'
    DB_PASSWORD='your_mongodb_password'
    DB_AUTH_SOURCE='your_auth_source'
    ```

6. **Run the application:**
    ```bash
    python manage.py runserver
    ```

## Common Django Commands

- **Create migrations for your models:**
    ```bash
    python manage.py makemigrations
    ```

- **Apply migrations to the database:**
    ```bash
    python manage.py migrate
    ```

- **Access the Django admin panel at:**
    ```
    http://127.0.0.1:8000/admin
    ```

- **Stop the server (in the terminal):**
    ```
    Ctrl + C
    ```


## Acknowledgments

- [Django](https://www.djangoproject.com/)
- [OpenAI](https://openai.com/)
