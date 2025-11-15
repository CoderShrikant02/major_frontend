# Tomato Disease Classification App

A modern web-based application for classifying tomato plant diseases using a hybrid deep learning model (EfficientNetB0 + Xception) with user authentication and MySQL database integration.

## Features

- 🍅 AI-Powered tomato leaf disease classification
- � User authentication (Login/Register)
- 📊 Prediction history tracking
- 🎨 Modern dark-themed UI with animated effects
- 📱 Fully responsive design
- �️ MySQL database for secure user management

## Prerequisites

- Python 3.11
- MySQL Server installed and running
- Virtual environment (recommended)

## Installation

1. **Clone or navigate to the project directory**

2. **Create and activate virtual environment** (Python 3.11):
```bash
py -3.11 -m venv venv
.\venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure MySQL Database**:
   - Open `config.py`
   - Update MySQL credentials:
     ```python
     MYSQL_HOST = 'localhost'
     MYSQL_USER = 'root'
     MYSQL_PASSWORD = 'your_mysql_password'  # Change this
     MYSQL_DB = 'tomato_disease_db'
     ```

5. **Initialize the database**:
```bash
python database.py
```

## Usage

1. **Start the Flask application**:
```bash
python app.py
```

2. **Open your browser** and navigate to:
```
http://localhost:5000
```

3. **Register a new account** or **Login** with existing credentials

4. **Upload tomato leaf images** for disease detection

## Application Structure

```
├── app.py                          # Main Flask application
├── config.py                       # Configuration settings
├── database.py                     # Database initialization
├── brain_hybrid_effb0_xcep.keras  # Trained model
├── class_indices.json             # Class labels
├── preprocess_info.json           # Preprocessing config
├── requirements.txt               # Dependencies
└── templates/
    ├── landing.html               # Landing page
    ├── login.html                 # Login page
    ├── register.html              # Registration page
    └── dashboard.html             # Main classification interface
```

## Model Information

- **Architecture**: Hybrid model combining EfficientNetB0 and Xception
- **Input Size**: 299x299 pixels
- **Number of Classes**: 12

## Detectable Conditions

1. Leaf Miner
2. Spotted Wilt Virus
3. Bacterial Spot
4. Early Blight
5. Late Blight
6. Leaf Mold
7. Septoria Leaf Spot
8. Spider Mites (Two-spotted spider mite)
9. Target Spot
10. Yellow Leaf Curl Virus
11. Tomato Mosaic Virus
12. Healthy

## Files

- `app.py` - Main Flask application with authentication
- `config.py` - Application configuration
- `database.py` - Database setup and connection
- `brain_hybrid_effb0_xcep.keras` - Trained model
- `class_indices.json` - Class labels mapping
- `preprocess_info.json` - Preprocessing configuration
- `requirements.txt` - Python dependencies

## Database Schema

### Users Table
- `id` (INT, Primary Key)
- `name` (VARCHAR)
- `email` (VARCHAR, Unique)
- `password` (VARCHAR, Hashed)
- `created_at` (TIMESTAMP)

### Predictions Table
- `id` (INT, Primary Key)
- `user_id` (INT, Foreign Key)
- `predicted_class` (VARCHAR)
- `confidence` (FLOAT)
- `image_name` (VARCHAR)
- `created_at` (TIMESTAMP)

## Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Login required for predictions
- SQL injection protection
- Secure database connections

## Technologies Used

- **Backend**: Flask 3.0.0
- **Database**: MySQL 8.0
- **ML Framework**: TensorFlow 2.20.0
- **Image Processing**: Pillow
- **Authentication**: Werkzeug Security
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
