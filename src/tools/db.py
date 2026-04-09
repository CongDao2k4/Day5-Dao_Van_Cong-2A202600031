from langchain_core.tools import tool


class DatabaseManager:
    def execute(self, db_id: str, sql: str) -> object: ...


db_manager = DatabaseManager()

DB_REGISTRY = [
    {
        'id': 'sis_db',
        'description': 'Student Information System. The primary source for administrative, demographic, and financial student data.',
        'dialect': 'sqlite3',
        'keywords': [
            'gpa',
            'tuition',
            'enrollment',
            'student profile',
            'transcripts',
            'billing',
        ],
    },
    {
        'id': 'lms_db',
        'description': 'Learning Management System. The primary source for academic content, assignments, and student engagement data.',
        'dialect': 'postgres',
        'keywords': [
            'assignments',
            'quizzes',
            'course materials',
            'submissions',
            'module content',
        ],
    },
]


@tool
def get_db_list() -> str:
    """Retrieve available Databases."""
    header = '## AVAILABLE DATABASE REGISTRY\n'
    entries = []

    for db in DB_REGISTRY:
        entry = (
            f'### ID: {db["id"]}\n'
            f'- **Description**: {db["description"]}\n'
            f'- **Dialect**: {db['dialect']}\n'
            f'- **Keywords**: {", ".join(db["keywords"])}\n'
        )
        entries.append(entry)

    return header + '\n---\n'.join(entries)


def get_db_schema(db_id: str) -> str:
    """Returns a semantically enriched schema summary.

    Designed for high-accuracy SQL generation by providing table/column intent.
    """
    mock_schemas = {
        'sis_db': """
### DATABASE: STUDENT_INFORMATION_SYSTEM (SIS)
Description: Primary system of record for student administrative data.

#### TABLE: students
- Description: Core demographics for all registered students.
- Columns:
    - student_id (INT, PRIMARY KEY): Unique identifier for a student.
    - name (TEXT): Full legal name of the student.
    - enrollment_date (DATE): The date the student first joined the institution.
    - status (TEXT): Current standing. Values: ['Enrolled', 'Graduated', 'Withdrawn', 'On-Leave'].

#### TABLE: grades
- Description: Historical academic performance across all semesters.
- Columns:
    - student_id (INT, FOREIGN KEY): References students.student_id.
    - course_id (INT): Unique ID for the specific course module.
    - grade (FLOAT): Numerical score (0.0 to 4.0).
    - semester (TEXT): Format 'YYYY-S1/S2' (e.g., '2026-S1').

#### TABLE: billing
- Description: Financial accounts and tuition status.
- Columns:
    - student_id (INT, FOREIGN KEY): References students.student_id.
    - total_due (FLOAT): Total outstanding balance in USD.
    - amount_paid (FLOAT): Total credits/payments applied.
    - overdue (BOOLEAN): True if the 'total_due' is past the payment deadline.
""",
        'lms_db': """
### DATABASE: LEARNING_MANAGEMENT_SYSTEM (LMS)
Description: Digital classroom environment for content and interaction.

#### TABLE: courses
- Description: Catalog of active and archived course modules.
- Columns:
    - course_id (INT, PRIMARY KEY): Unique identifier for the course.
    - title (TEXT): Human-readable name of the module (e.g., 'Intro to ML').
    - instructor_id (INT): ID of the staff member assigned to lead the course.

#### TABLE: assignments
- Description: Specific tasks or homework assigned within a course.
- Columns:
    - assignment_id (INT, PRIMARY KEY): Unique ID for the task.
    - course_id (INT, FOREIGN KEY): References courses.course_id.
    - title (TEXT): Title of the assignment (e.g., 'Lab 1: Robot Control').
    - due_date (DATE): Submission deadline.

#### TABLE: submissions
- Description: Student-uploaded work and the resulting scores.
- Columns:
    - student_id (INT): Identifier for the student who submitted. Note: Joins with SIS_DB.students.
    - assignment_id (INT, FOREIGN KEY): References assignments.assignment_id.
    - score (FLOAT): The grade awarded for this specific submission.
    - submitted_at (TIMESTAMP): Exact time of upload.
""",
    }

    return mock_schemas.get(db_id, f"Error: Database ID '{db_id}' not found.")

def execute_sql(db_id: str, sql: str) -> list:
    """Simulates executing a SQL query on a specific database and returns mock data.

    Returns a list of dictionaries (rows).
    """
    print(f"--- [MOCK EXECUTION] on {db_id} ---\nSQL: {sql}\n")

    # Mock data based on the target database
    mock_data = {
        "sis_db": [
            {"student_id": 101, "name": "Nguyen An", "status": "Enrolled", "total_due": 1200.0, "overdue": False},
            {"student_id": 102, "name": "Tran Binh", "status": "Enrolled", "total_due": 500.0, "overdue": True},
            {"student_id": 103, "name": "Le Chi", "status": "Graduated", "total_due": 0.0, "overdue": False},
        ],
        "lms_db": [
            {"course_id": 501, "title": "Intro to AI", "avg_score": 88.5},
            {"course_id": 502, "title": "Advanced Robotics", "avg_score": 92.0},
            {"course_id": 503, "title": "Data Structures", "avg_score": 75.2},
        ],
    }

    # In a real mock, you might filter the data based on 'sql' keywords,
    # but for a simple prototype, returning the whole set is fine.
    return mock_data.get(db_id, [{"error": "Invalid DB ID"}])
