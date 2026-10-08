from database import get_db_connection
from schemas import StudentCreate, StudentUpdate


def create_student(student: StudentCreate):
    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO students
            (student_id, name, date_of_birth, email, phone, course, address, enrollment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                student.student_id,
                student.name,
                student.date_of_birth,
                student.email,
                student.phone,
                student.course,
                student.address,
                student.enrollment_date,
            ),
        )

        connection.commit()

    finally:
        connection.close()

    return get_student(student.student_id)


def get_students():
    connection = get_db_connection()

    students = connection.execute(
        "SELECT * FROM students ORDER BY student_id"
    ).fetchall()

    connection.close()

    return [dict(student) for student in students]


def get_student(student_id: str):
    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()

    connection.close()

    if student:
        return dict(student)

    return None


def update_student(student_id: str, student: StudentUpdate):
    connection = get_db_connection()

    existing_student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()

    if not existing_student:
        connection.close()
        return None

    update_data = student.model_dump(exclude_unset=True)

    if not update_data:
        connection.close()
        return dict(existing_student)

    fields = []
    values = []

    for field, value in update_data.items():
        fields.append(f"{field} = ?")
        values.append(value)

    values.append(student_id)

    query = f"""
        UPDATE students
        SET {", ".join(fields)}
        WHERE student_id = ?
    """

    connection.execute(query, values)
    connection.commit()
    connection.close()

    return get_student(student_id)


def delete_student(student_id: str):
    connection = get_db_connection()

    existing_student = connection.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,),
    ).fetchone()

    if not existing_student:
        connection.close()
        return False

    connection.execute(
        "DELETE FROM students WHERE student_id = ?",
        (student_id,),
    )

    connection.commit()
    connection.close()

    return True