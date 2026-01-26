# main.py
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pickle
import numpy as np
import os

# Sklearn models and preprocessing
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer

# ------------------------------------------------------------
# 🧾 Request Schemas
# ------------------------------------------------------------
class LinearInput(BaseModel):
    hours_studied: float

class LogisticInput(BaseModel):
    email_text: str

# ------------------------------------------------------------
# 📦 Load Pickle Models (trained offline and saved as .pkl)
# ------------------------------------------------------------
# Get the base directory of the project (where main.py is located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

try:
    linear_model = pickle.load(open(os.path.join(MODELS_DIR, "simple_linear_regression.pkl"), "rb"))
    logistic_model = pickle.load(open(os.path.join(MODELS_DIR, "logistic_regression_spam.pkl"), "rb"))
    logistic_vectorizer = pickle.load(open(os.path.join(MODELS_DIR, "logistic_vectorizer.pkl"), "rb"))
except Exception as e:
    raise RuntimeError(f"Error loading model files: {e}")



# ---------------------------------------------------------
# 📘 Step 1: Create the FastAPI application
# ---------------------------------------------------------
app = FastAPI(
    title="FastAPI Crash Course - Student API",
    description=" Student Management API demonstrating all major HTTP methods.",
    version="1.0.0",
)

# ---------------------------------------------------------
# 🌐 Step 2: Enable CORS (so frontend apps can call this API)
# ---------------------------------------------------------
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,                # 1️⃣ Add CORS middleware to our FastAPI app
    allow_origins=["*"],           # 2️⃣ Allow requests from ANY origin (any website can call our API)
                                   #    - "*" means all domains
                                   #    - In production, you'd list only trusted URLs
    allow_credentials=True,        # 3️⃣ Allow cookies, authorization headers, or credentials to be sent
                                   #    - Needed if frontend needs authentication
    allow_methods=["*"],           # 4️⃣ Allow all HTTP methods (GET, POST, PUT, DELETE, PATCH, etc.)
                                   #    - Can also specify a list like ["GET", "POST"]
    allow_headers=["*"],           # 5️⃣ Allow all custom headers in requests
                                   #    - Lets frontend send headers like Authorization, Content-Type, etc.
)

# ---------------------------------------------------------
# 📚 Step 3: Define a Pydantic model for request validation
# ---------------------------------------------------------
class Student(BaseModel):
    id: Optional[int] = None
    name: str
    age: int
    course: str

# ---------------------------------------------------------
# 📊 Step 4: Create a mock database (in-memory list)
# ---------------------------------------------------------
students_db = [
    {"id": 1, "name": "Alice", "age": 20, "course": "AI"},
    {"id": 2, "name": "Bob", "age": 22, "course": "Data Science"},
]

# ---------------------------------------------------------
# 📍 GET - Retrieve all students
# ---------------------------------------------------------
@app.get("/students", summary="Get all students", tags=["CRUD"])
def get_students():
    return {"students": students_db}

# ---------------------------------------------------------
# 📍 GET (by ID) - Retrieve a single student
# ---------------------------------------------------------
@app.get("/students/{student_id}", summary="Get student by ID", tags=["CRUD"])
def get_student(student_id: int):
    for student in students_db:
        if student["id"] == student_id:
            return {"student": student}
    raise HTTPException(status_code=404, detail="Student not found")

# ---------------------------------------------------------
# 📍 POST - Add a new student
# ---------------------------------------------------------
@app.post("/students", summary="Add new student", tags=["CRUD"])
def create_student(student: Student):
    new_id = max([s["id"] for s in students_db]) + 1 if students_db else 1
    new_student = student.dict()
    new_student["id"] = new_id
    students_db.append(new_student)
    return {"message": "Student added successfully", "student": new_student}

# ---------------------------------------------------------
# 📍 PUT - Update a student completely
# ---------------------------------------------------------
@app.put("/students/{student_id}", summary="Update student (full)", tags=["CRUD"])
def update_student(student_id: int, updated_student: Student):
    for student in students_db:
        if student["id"] == student_id:
            student.update(updated_student.dict())
            student["id"] = student_id
            return {"message": "Student updated successfully", "student": student}
    raise HTTPException(status_code=404, detail="Student not found")

# ---------------------------------------------------------
# 📍 PATCH - Update student partially
# ---------------------------------------------------------
@app.patch("/students/{student_id}", summary="Update student (partial)", tags=["Advanced"])
def patch_student(student_id: int, student_update: dict):
    for student in students_db:
        if student["id"] == student_id:
            student.update(student_update)
            return {"message": "Student partially updated", "student": student}
    raise HTTPException(status_code=404, detail="Student not found")

# ---------------------------------------------------------
# 📍 DELETE - Remove a student
# ---------------------------------------------------------
@app.delete("/students/{student_id}", summary="Delete a student", tags=["CRUD"])
def delete_student(student_id: int):
    for student in students_db:
        if student["id"] == student_id:
            students_db.remove(student)
            return {"message": "Student deleted successfully"}
    raise HTTPException(status_code=404, detail="Student not found")


# ---------------------------------------------------------
# 📍HEAD - Check if any students exist (metadata only)
# ---------------------------------------------------------
@app.head("/students")
def head_students(response: Response):
    total = len(students_db)
    # Set custom header
    response.headers["X-Total-Students"] = str(total)
    # Return None (FastAPI keeps the headers)
    return

# ---------------------------------------------------------
# 📍 OPTIONS - Show allowed methods for /students
# ---------------------------------------------------------
@app.options("/students", summary="Allowed HTTP methods", tags=["Advanced"])
def options_students():
    return {"allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]}

# ----- Linear Regression -----
@app.post("/predict/linear", summary="Predict exam score using Linear Regression.", tags=["ML"])
def predict_linear(data: LinearInput):
    """
    Predict exam score using Linear Regression.
    Input: hours studied
    """
    try:
        features = np.array([[data.hours_studied]])
        prediction = linear_model.predict(features)[0]
        return {"prediction": float(prediction)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ----- Logistic Regression -----
@app.post("/predict/logistic", summary="Classify email as Spam or Not Spam using Logistic Regression.", tags=["ML"])
def predict_logistic(data: LogisticInput):
    """
    Classify email as Spam or Not Spam using Logistic Regression.
    Input: raw email text
    """
    try:
        # ✅ Step 1: Convert raw text → numeric features using vectorizer
        features = logistic_vectorizer.transform([data.email_text])

        # ✅ Step 2: Predict using trained logistic regression model
        prediction = logistic_model.predict(features)[0]

        return {
            "prediction": int(prediction),
            "label": "Spam" if prediction == 1 else "Not Spam"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ---------------------------------------------------------
# 🚀 Run the app (only when executing this file directly)
# ---------------------------------------------------------
# Run using: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5566, reload=True)
