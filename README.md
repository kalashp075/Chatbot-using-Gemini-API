# Chatbot using Gemini API

A Django web application that provides user authentication and a chat interface powered by Google Gemini AI.

## Features

- User registration with email verification
- Secure login/logout
- Profile management
- Chat interface with Gemini AI responses
- Stores chat history per user
- Modern UI with custom templates and static files

## Technologies
- Django (Python)
- SQLite (default, can be changed)
- Google Gemini API (Generative AI)
- HTML/CSS for frontend


<img width="1680" height="1050" alt="Screenshot 2025-09-18 at 7 28 35 PM" src="https://github.com/user-attachments/assets/e2af73f0-1397-46b6-af1a-dc7614bb4267" />



## Setup
1. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   - Set your Gemini API key and email settings in `project/settings.py` or use a `.env` file.

4. **Apply migrations**
   ```bash
   python project/manage.py migrate
   ```

5. **Run the development server**
   ```bash
   python project/manage.py runserver
   ```

6. **Access the app**
   - Open `http://127.0.0.1:8000/` in your browser.

## Usage

- Register a new account and verify your email.
- Log in to access the chat interface.
- Send messages and receive AI-powered responses.
- View your chat history.
