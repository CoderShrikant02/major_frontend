from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import tensorflow as tf
from tensorflow import keras
from PIL import Image
import numpy as np
import json
import os
import base64
from io import BytesIO
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, init_db
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Load the model and metadata
model = None
index_to_class = None
preprocess_info = None
pesticide_recommendations = None
responsible_insects = None
display_names = None

def load_model_and_metadata():
    global model, index_to_class, preprocess_info, pesticide_recommendations, responsible_insects, display_names
    
    try:
        # Load model
        print("Loading model...")
        model = keras.models.load_model('brain_hybrid_effb0_xcep.keras')
        print("Model loaded successfully!")
        
        # Load class indices
        print("Loading class indices...")
        with open('class_indices.json', 'r') as f:
            class_indices = json.load(f)
        index_to_class = {v: k for k, v in class_indices.items()}
        print("Class indices loaded successfully!")
        
        # Load preprocess info
        print("Loading preprocess info...")
        with open('preprocess_info.json', 'r') as f:
            preprocess_info = json.load(f)
        print("Preprocess info loaded successfully!")
        
        # Load responsible insects mapping
        print("Loading responsible insects...")
        try:
            with open('responsible_insects.json', 'r', encoding='utf-8') as f:
                responsible_insects = json.load(f)
            print(f"Responsible insects loaded successfully! ({len(responsible_insects)} diseases)")
        except Exception as e:
            print(f"Warning: Could not load responsible insects: {e}")
            responsible_insects = {}
        
        # Load pesticide recommendations
        print("Loading pesticide recommendations...")
        try:
            with open('pesticide_recommendations.json', 'r', encoding='utf-8') as f:
                pesticide_recommendations = json.load(f)
            print(f"Pesticide recommendations loaded successfully! ({len(pesticide_recommendations)} diseases)")
        except FileNotFoundError:
            print("WARNING: pesticide_recommendations.json not found. Creating empty dict.")
            pesticide_recommendations = {}
        except json.JSONDecodeError as e:
            print(f"WARNING: Error parsing pesticide_recommendations.json: {e}")
            pesticide_recommendations = {}
        
        # Load display names
        print("Loading display names...")
        try:
            with open('display_names.json', 'r', encoding='utf-8') as f:
                display_names = json.load(f)
            print(f"Display names loaded successfully! ({len(display_names)} diseases)")
        except Exception as e:
            print(f"Warning: Could not load display names: {e}")
            display_names = {}
    except Exception as e:
        print(f"ERROR loading model/metadata: {e}")
        raise

def preprocess_image(image):
    # Get target size from preprocess info
    target_size = tuple(preprocess_info['input_size'])
    
    # Resize image
    image = image.resize(target_size)
    
    # Convert to array
    img_array = np.array(image)
    
    # Ensure RGB (in case of RGBA or grayscale)
    if img_array.shape[-1] == 4:  # RGBA
        img_array = img_array[:, :, :3]
    elif len(img_array.shape) == 2:  # Grayscale
        img_array = np.stack([img_array] * 3, axis=-1)
    
    # Expand dimensions to match batch shape
    img_array = np.expand_dims(img_array, axis=0)
    
    # Apply Xception preprocessing
    img_array = tf.keras.applications.xception.preprocess_input(img_array)
    
    return img_array

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_email'] = user['email']
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid email or password', 'error')
        else:
            flash('Database connection error', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not name or not email or not password or not confirm_password:
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'error')
            return render_template('register.html')
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Insert into database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                    (name, email, hashed_password)
                )
                conn.commit()
                cursor.close()
                conn.close()
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
            except Exception as e:
                flash('Email already exists', 'error')
                conn.close()
        else:
            flash('Database connection error', 'error')
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', classes=sorted(index_to_class.values()))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'success')
    return redirect(url_for('landing'))

@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only JPG, JPEG, and PNG are allowed'}), 400
        
        # Read and process image
        image = Image.open(file.stream)
        
        # Convert image to base64 for display
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Preprocess and predict
        processed_image = preprocess_image(image)
        predictions = model.predict(processed_image, verbose=0)
        
        # Get top prediction
        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = index_to_class[predicted_class_idx]
        confidence = float(predictions[0][predicted_class_idx] * 100)
        
        # Save prediction to database
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO predictions (user_id, predicted_class, confidence, image_name) VALUES (%s, %s, %s, %s)",
                    (session['user_id'], predicted_class, confidence, file.filename)
                )
                conn.commit()
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error saving prediction: {e}")
        
        # Get all predictions sorted
        all_predictions = [
            {
                'class': index_to_class[i],
                'probability': float(predictions[0][i] * 100)
            }
            for i in range(len(predictions[0]))
        ]
        all_predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        # Get pesticide recommendations for the predicted disease
        recommendations = []
        if pesticide_recommendations:
            recommendations = pesticide_recommendations.get(predicted_class, [])
        
        # Get responsible insect/pest for the predicted disease
        responsible_pest = None
        if responsible_insects:
            responsible_pest = responsible_insects.get(predicted_class, None)
        
        # Get user-friendly display name
        predicted_display_name = predicted_class
        if display_names:
            predicted_display_name = display_names.get(predicted_class, predicted_class)
        
        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_str}',
            'predicted_class': predicted_class,
            'predicted_display_name': predicted_display_name,
            'confidence': confidence,
            'responsible_pest': responsible_pest,
            'top_3': all_predictions[:3],
            'all_predictions': all_predictions,
            'pesticide_recommendations': recommendations
        })
        
    except Exception as e:
        print(f"Error in predict route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Server error: {str(e)}'}), 500

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == '__main__':
    print("Initializing database...")
    init_db()
    print("Loading model and metadata...")
    load_model_and_metadata()
    print("Model loaded successfully!")
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
