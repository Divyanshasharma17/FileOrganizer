📂 Smart File Organizer (Django Web App)
Smart File Organizer is a Django-based web application that allows users to upload multiple files and automatically organizes them into categories like Images, Documents, Videos, and Others.
The application also detects and removes duplicate files using hashing, making file management efficient and clean.

✨ Features
    📤 Upload multiple files via web interface
    📁 Automatically categorize files (Images, Videos, Documents, Others)
    🔁 Detect and remove duplicate files using hashing
    🏷️ Rename files to avoid overwriting
    📦 Store files in structured folders
    🌐 Simple and clean UI
🛠️ Tech Stack
  Backend: Django
  Frontend: HTML, CSS
  Language: Python
Libraries Used:
  os (file handling)
  shutil (file operations)
  hashlib (duplicate detection)
📁 Project Structure
file_organizer/
│── organizer_app/
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   │   └── index.html
│
│── media/        # Uploaded & organized files
│── manage.py
⚙️ How It Works
  User uploads files through the web interface
  Files are saved in the media folder
  Each file is categorized based on its extension
  Duplicate files are detected using hashing and removed
  Files are moved into their respective folders
▶️ Installation & Setup
    1. Clone the repository
    git clone https://github.com/your-username/smart-file-organizer.git
    cd smart-file-organizer
    2. Install dependencies
    pip install django
    3. Run migrations
    python manage.py migrate
    4. Run server
    python manage.py runserver
    5. Open in browser
    http://127.0.0.1:8000/
📌 Output
    Files are automatically organized inside the media/ folder:
    media/
     ├── Images/
     ├── Documents/
     ├── Videos/
     ├── Others/
