from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional

from database import create_table
from schemas import StudentCreate, StudentUpdate
from crud import (
    create_student,
    get_students,
    get_student,
    update_student,
    delete_student,
)


app = FastAPI(
    title="Student Database CRUD API",
    description="A FastAPI backend for managing student records using SQLite.",
    version="1.0.0",
)


# HTML templates
templates = Jinja2Templates(directory="templates")


# Create database table when application starts
create_table()


# Home page
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# Create Student
@app.post("/students", status_code=201)
def add_student(student: StudentCreate):

    if get_student(student.student_id):
        raise HTTPException(
            status_code=400,
            detail="Student ID already exists."
        )

    try:
        return create_student(student)

    except Exception as error:

        if "UNIQUE constraint failed: students.email" in str(error):
            raise HTTPException(
                status_code=400,
                detail="Email already exists."
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to create student."
        )


# Get All Students
@app.get("/students")
def list_students(
    name: Optional[str] = None,
    course: Optional[str] = None
):

    students = get_students()

    if name:
        students = [
            student
            for student in students
            if name.lower() in student["name"].lower()
        ]

    if course:
        students = [
            student
            for student in students
            if student["course"]
            and course.lower() in student["course"].lower()
        ]

    return {
        "count": len(students),
        "students": students
    }


# Get Student by ID
@app.get("/students/{student_id}")
def read_student(student_id: str):

    student = get_student(student_id)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return student


# Update Student
@app.put("/students/{student_id}")
def edit_student(
    student_id: str,
    student: StudentUpdate
):

    if not get_student(student_id):
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    try:
        return update_student(student_id, student)

    except Exception as error:

        if "UNIQUE constraint failed: students.email" in str(error):
            raise HTTPException(
                status_code=400,
                detail="Email already exists."
            )

        raise HTTPException(
            status_code=500,
            detail="Failed to update student."
        )


# Delete Student
@app.delete("/students/{student_id}")
def remove_student(student_id: str):

    if not delete_student(student_id):
        raise HTTPException(
            status_code=404,
            detail="Student not found."
        )

    return {
        "message": "Student deleted successfully.",
        "student_id": student_id
    }