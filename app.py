import base64
import json
import sys
from functools import wraps
from io import BytesIO
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for
from tensorflow import keras
from werkzeug.security import check_password_hash, generate_password_hash

from config import Config
from database import get_db_connection, init_db


app = Flask(__name__)
app.config.from_object(Config)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

model = None
index_to_class = None
preprocess_info = None
pesticide_recommendations = None
responsible_insects = None
display_names = None

#ye sub .env file sey ayega 
def validate_startup():
    required_env = {
        "SECRET_KEY": Config.SECRET_KEY,
        "DB_HOST": Config.DB_HOST,
        "DB_USER": Config.DB_USER,
        "DB_PASSWORD": Config.DB_PASSWORD,
        "DB_NAME": Config.DB_NAME,
    }
    missing_env = [key for key, value in required_env.items() if not value]
    if missing_env:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing_env)}")

    required_paths = [
        Path("class_indices.json"),
        Path("preprocess_info.json"),
        Path("responsible_insects.json"),
        Path("pesticide_recommendations.json"),
        Path("display_names.json"),
    ]
    missing_paths = [str(path) for path in required_paths if not path.exists()]
    if missing_paths:
        raise RuntimeError(f"Missing required startup files: {', '.join(missing_paths)}")

    # Model artifacts are large and may be delivered separately (e.g. LFS/S3).
    # Don't crash the whole service if they're missing; predictions will be disabled.
    model_dir = Path("tomato_leaf_hybrid_eff_final_disease")
    weights_file = model_dir / "model.weights.h5"
    if not model_dir.exists() or not weights_file.exists():
        print(
            "WARNING: Model artifacts missing; service will start but /predict will not work. "
            f"Expected: {weights_file}",
            file=sys.stderr,
        )


#ye model ko load karta hai aur uskey sathmetadata bhi load karta hai 
def load_model_and_metadata():

    global model, index_to_class, preprocess_info, pesticide_recommendations, responsible_insects, display_names

    try:
        with open("class_indices.json", "r", encoding="utf-8") as f:
            class_indices = json.load(f)
        index_to_class = {v: k for k, v in class_indices.items()}

        with open("preprocess_info.json", "r", encoding="utf-8") as f:
            preprocess_info = json.load(f)

        try:
            model_dir = Path("tomato_leaf_hybrid_eff_final_disease")
            weights_file = model_dir / "model.weights.h5"
            if model_dir.exists() and weights_file.exists():
                model = keras.models.load_model(str(model_dir))
            else:
                model = None
        except Exception as e:
            model = None
            print(f"WARNING: Failed to load model; predictions disabled: {e}", file=sys.stderr)

        try:
            with open("responsible_insects.json", "r", encoding="utf-8") as f:
                responsible_insects = json.load(f)
        except Exception:
            responsible_insects = {}

        try:
            with open("pesticide_recommendations.json", "r", encoding="utf-8") as f:
                pesticide_recommendations = json.load(f)
        except Exception:
            pesticide_recommendations = {}

        try:
            with open("display_names.json", "r", encoding="utf-8") as f:
                display_names = json.load(f)
        except Exception:
            display_names = {}

    except Exception as e:
        raise e


##Ismey image processing ki jaati hai 
def preprocess_image(image):
    """
    Uploaded image ko model ke input format me convert karta hai.
    """

    if model is not None and getattr(model, "input_shape", None):
        target_size = tuple(model.input_shape[1:3])
    else:
        target_size = tuple(preprocess_info["input_size"])

    image = image.resize(target_size)
    img_array = np.array(image)

    if img_array.shape[-1] == 4:
        img_array = img_array[:, :, :3]
    elif len(img_array.shape) == 2:
        img_array = np.stack([img_array] * 3, axis=-1)

    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.xception.preprocess_input(img_array)

    return img_array


#ye ensure karta hai ki bina login key kisi bhi route ka access na de
def login_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))

        return f(*args, **kwargs)

    return decorated_function


#Ye lading page key liye use kiya jata hai 
@app.route("/")
def landing():
    return render_template("landing.html")


#ye health check karney key liye 
@app.route("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}, 200


#ye login karmey key liye
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        conn = get_db_connection()

        if conn:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user and check_password_hash(user["password"], password):
                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["user_email"] = user["email"]
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))

            flash("Invalid email or password", "error")
        else:
            flash("Database connection error", "error")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("All fields are required", "error")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters long", "error")
            return render_template("register.html")

        conn = get_db_connection()

        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()

                if existing_user:
                    flash("Email already registered", "error")
                else:
                    hashed_password = generate_password_hash(password)
                    cursor.execute(
                        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                        (name, email, hashed_password),
                    )
                    conn.commit()
                    flash("Registration successful! Please login.", "success")
                    cursor.close()
                    conn.close()
                    return redirect(url_for("login"))

                cursor.close()
                conn.close()

            except Exception:
                flash("Registration failed", "error")
        else:
            flash("Database connection error", "error")

    return render_template("register.html")


#ismey dashbard.html ko render kiya jata hai jise ki uplad feature aur prediction result dikhaya jata hai
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", classes=sorted(index_to_class.values()))


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully", "success")
    return redirect(url_for("landing"))


@app.route("/predict", methods=["POST"])
@login_required
def predict():

    try:
        if model is None:
            return jsonify({"success": False, "error": "Model not available on server"}), 503

        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"success": False, "error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"success": False, "error": "Invalid file type"}), 400

        image = Image.open(file.stream)

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        processed_image = preprocess_image(image)

        predictions = model.predict(processed_image, verbose=0)

        predicted_class_idx = np.argmax(predictions[0])
        predicted_class = index_to_class[predicted_class_idx]
        confidence = float(predictions[0][predicted_class_idx] * 100)

        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO predictions (user_id, predicted_class, confidence, image_name) VALUES (%s, %s, %s, %s)",
                    (session["user_id"], predicted_class, confidence, file.filename),
                )
                conn.commit()
                cursor.close()
                conn.close()
            except Exception:
                pass

        all_predictions = [
            {"class": index_to_class[i], "probability": float(predictions[0][i] * 100)}
            for i in range(len(predictions[0]))
        ]
        all_predictions.sort(key=lambda x: x["probability"], reverse=True)

        recommendations = []
        if pesticide_recommendations:
            recommendations = pesticide_recommendations.get(predicted_class, [])

        responsible_pest = None
        if responsible_insects:
            responsible_pest = responsible_insects.get(predicted_class, None)

        predicted_display_name = predicted_class
        if display_names:
            predicted_display_name = display_names.get(predicted_class, predicted_class)

        return jsonify(
            {
                "success": True,
                "image": f"data:image/png;base64,{img_str}",
                "predicted_class": predicted_class,
                "predicted_display_name": predicted_display_name,
                "confidence": confidence,
                "responsible_pest": responsible_pest,
                "top_3": all_predictions[:3],
                "all_predictions": all_predictions,
                "pesticide_recommendations": recommendations,
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": f"Server error: {str(e)}"}), 500


def allowed_file(filename):
    """
    Check karta hai ki uploaded file valid image hai ya nahi
    """
    allowed_extensions = {"png", "jpg", "jpeg"}
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


if __name__ == "__main__":
    validate_startup()
    init_db()
    load_model_and_metadata()
    app.run(debug=False, host="0.0.0.0", port=5000)
