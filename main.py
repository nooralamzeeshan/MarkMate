# Import FastAPI and related libraries
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# Import SQLAlchemy & database config
from sqlalchemy import Table, Column, Integer, String, Float
from database import database, metadata, engine

# Create FastAPI app
app = FastAPI()

# Create students table structure
students = Table(
    "students",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("roll_no", Integer, unique=True),
    Column("marks", String),  # Store as "85,90,70"
    Column("percentage", Float),
    Column("grade", String),
)

# Create table in DB (first time only)
metadata.create_all(engine)

# Connect DB on startup
@app.on_event("startup")
async def startup():
    await database.connect()

# Disconnect DB on shutdown
@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Input model for student data
class Student(BaseModel):
    name: str
    roll_no: int
    marks: List[int]

# Logic for percentage & grade
def calculate_result(marks):
    total = sum(marks)
    percentage = total / len(marks)
    if percentage >= 80:
        grade = "A"
    elif percentage >= 60:
        grade = "B"
    elif percentage >= 40:
        grade = "C"
    else:
        grade = "Fail"
    return percentage, grade

# API to add student
@app.post("/add-student")
async def add_student(student: Student):
    percentage, grade = calculate_result(student.marks)
    marks_str = ",".join(map(str, student.marks))  # Convert list to "85,70,90"

    query = students.insert().values(
        name=student.name,
        roll_no=student.roll_no,
        marks=marks_str,
        percentage=percentage,
        grade=grade
    )
    await database.execute(query)

    return {
        "name": student.name,
        "roll_no": student.roll_no,
        "marks": student.marks,
        "percentage": percentage,
        "grade": grade
    }

# API to get student report
@app.get("/get-student/{roll_no}")
async def get_student(roll_no: int):
    query = students.select().where(students.c.roll_no == roll_no)
    student = await database.fetch_one(query)

    if student:
        marks_list = list(map(int, student["marks"].split(",")))
        return {
            "name": student["name"],
            "roll_no": student["roll_no"],
            "marks": marks_list,
            "percentage": student["percentage"],
            "grade": student["grade"]
        }
    return {"error": "Student not found"}
