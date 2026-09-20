
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# =========================================================
# APP CONFIGURATION
# =========================================================

app.secret_key = "quizmaster_change_this_secret_key"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "quiz_game"
}


# =========================================================
# DATABASE FUNCTIONS
# =========================================================

def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def fetchone(sql, params=()):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(sql, params)
        return cursor.fetchone()

    finally:
        cursor.close()
        db.close()


def fetchall(sql, params=()):
    db = get_db()
    cursor = db.cursor(dictionary=True)

    try:
        cursor.execute(sql, params)
        return cursor.fetchall()

    finally:
        cursor.close()
        db.close()


def execute(sql, params=()):
    db = get_db()
    cursor = db.cursor()

    try:
        cursor.execute(sql, params)
        db.commit()
        return cursor.lastrowid

    finally:
        cursor.close()
        db.close()


# =========================================================
# LOGIN PROTECTION
# =========================================================

def user_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "user_id" not in session:
            flash("Please login to continue.", "warning")
            return redirect(url_for("login"))

        return view(*args, **kwargs)

    return wrapped


def admin_required(view):

    @wraps(view)
    def wrapped(*args, **kwargs):

        if "admin_id" not in session:
            return redirect(url_for("admin_login"))

        return view(*args, **kwargs)

    return wrapped


# =========================================================
# GLOBAL TEMPLATE VARIABLES
# =========================================================

@app.context_processor
def inject_globals():

    return {
        "logged_user": session.get("user_name"),
        "is_user": "user_id" in session,
        "is_admin": "admin_id" in session
    }


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    categories = fetchall("""
        SELECT *
        FROM categories
        ORDER BY id
    """)

    return render_template(
        "index.html",
        categories=categories
    )


# =========================================================
# USER REGISTRATION
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not name or not email or not password:

            flash(
                "All fields are required.",
                "danger"
            )

            return redirect(url_for("register"))

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(url_for("register"))

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "danger"
            )

            return redirect(url_for("register"))

        # Check existing user
        existing_user = fetchone(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        if existing_user:

            flash(
                "An account with this email already exists.",
                "warning"
            )

            return redirect(url_for("login"))

        # Hash password
        hashed_password = generate_password_hash(password)

        # Insert user
        execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (%s, %s, %s)
            """,
            (
                name,
                email,
                hashed_password
            )
        )

        flash(
            "Account created successfully. Please login.",
            "success"
        )

        return redirect(url_for("login"))

    return render_template("register.html")


# =========================================================
# USER LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        user = fetchone(
            """
            SELECT *
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        if not user:

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(url_for("login"))

        if not check_password_hash(
            user["password"],
            password
        ):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(url_for("login"))

        # Clear old session
        session.clear()

        # Create user session
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        flash(
            f"Welcome back, {user['name']}!",
            "success"
        )

        return redirect(url_for("home"))

    return render_template("login.html")


# =========================================================
# USER LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(url_for("home"))


# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route(
    "/change-password",
    methods=["GET", "POST"]
)
@user_required
def change_password():

    if request.method == "POST":

        current_password = request.form.get(
            "current_password",
            ""
        )

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        user = fetchone(
            """
            SELECT *
            FROM users
            WHERE id = %s
            """,
            (session["user_id"],)
        )

        if not user:

            flash(
                "User account not found.",
                "danger"
            )

            return redirect(url_for("logout"))

        # Check current password
        if not check_password_hash(
            user["password"],
            current_password
        ):

            flash(
                "Current password is incorrect.",
                "danger"
            )

            return redirect(
                url_for("change_password")
            )

        if len(new_password) < 6:

            flash(
                "New password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("change_password")
            )

        if new_password != confirm_password:

            flash(
                "New passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("change_password")
            )

        hashed_password = generate_password_hash(
            new_password
        )

        execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (
                hashed_password,
                session["user_id"]
            )
        )

        flash(
            "Password changed successfully.",
            "success"
        )

        return redirect(
            url_for("profile")
        )

    return render_template(
        "change_password.html"
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================
# Simple college-project recovery:
# Name + Email + New Password
# No OTP / Email verification
# =========================================================

@app.route(
    "/forgot-password",
    methods=["GET", "POST"]
)
def forgot_password():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        user = fetchone(
            """
            SELECT *
            FROM users
            WHERE email = %s
            AND name = %s
            """,
            (
                email,
                name
            )
        )

        if not user:

            flash(
                "No matching account found.",
                "danger"
            )

            return redirect(
                url_for("forgot_password")
            )

        if len(new_password) < 6:

            flash(
                "New password must contain at least 6 characters.",
                "danger"
            )

            return redirect(
                url_for("forgot_password")
            )

        if new_password != confirm_password:

            flash(
                "Passwords do not match.",
                "danger"
            )

            return redirect(
                url_for("forgot_password")
            )

        hashed_password = generate_password_hash(
            new_password
        )

        execute(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (
                hashed_password,
                user["id"]
            )
        )

        flash(
            "Password reset successfully. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "forgot_password.html"
    )


# =========================================================
# USER PROFILE
# =========================================================

@app.route("/profile")
@user_required
def profile():

    user = fetchone(
        """
        SELECT
            id,
            name,
            email,
            created_at
        FROM users
        WHERE id = %s
        """,
        (session["user_id"],)
    )

    results = fetchall(
        """
        SELECT
            r.*,
            t.test_name,
            c.name AS category_name
        FROM results r
        JOIN tests t
            ON t.id = r.test_id
        JOIN categories c
            ON c.id = t.category_id
        WHERE r.user_id = %s
        ORDER BY r.created_at DESC
        """,
        (session["user_id"],)
    )

    return render_template(
        "profile.html",
        user=user,
        results=results
    )


# =========================================================
# CATEGORY / TEST LIST
# =========================================================

@app.route(
    "/category/<int:category_id>"
)
@user_required
def category(category_id):

    category_data = fetchone(
        """
        SELECT *
        FROM categories
        WHERE id = %s
        """,
        (category_id,)
    )

    if not category_data:

        return "Category not found", 404

    tests = fetchall(
        """
        SELECT
            t.id,
            t.test_name,
            COUNT(q.id) AS question_count
        FROM tests t
        LEFT JOIN questions q
            ON q.test_id = t.id
        WHERE t.category_id = %s
        GROUP BY
            t.id,
            t.test_name
        ORDER BY t.id
        """,
        (category_id,)
    )

    return render_template(
        "tests.html",
        category=category_id,
        category_name=category_data["name"],
        tests=tests
    )


# =========================================================
# START QUIZ
# =========================================================

@app.route(
    "/test/<int:category_id>/<int:test_id>"
)
@user_required
def test(category_id, test_id):

    category_data = fetchone(
        """
        SELECT *
        FROM categories
        WHERE id = %s
        """,
        (category_id,)
    )

    test_data = fetchone(
        """
        SELECT *
        FROM tests
        WHERE id = %s
        AND category_id = %s
        """,
        (
            test_id,
            category_id
        )
    )

    if not category_data or not test_data:

        return "Test not found", 404

    questions = fetchall(
        """
        SELECT
            id,
            question,
            option_a,
            option_b,
            option_c,
            option_d
        FROM questions
        WHERE test_id = %s
        ORDER BY id
        """,
        (test_id,)
    )

    if not questions:

        flash(
            "This test has no questions yet.",
            "warning"
        )

        return redirect(
            url_for(
                "category",
                category_id=category_id
            )
        )

    formatted_questions = []

    for question in questions:

        formatted_questions.append(
            {
                "id": question["id"],

                "question": question["question"],

                "options": {
                    "A": question["option_a"],
                    "B": question["option_b"],
                    "C": question["option_c"],
                    "D": question["option_d"]
                }
            }
        )

    return render_template(
        "quiz.html",
        category=category_id,
        test_id=test_id,
        category_name=category_data["name"],
        test_name=test_data["test_name"],
        questions=formatted_questions
    )


# =========================================================
# QUIZ RESULT
# =========================================================

@app.route(
    "/result/<int:category_id>/<int:test_id>",
    methods=["POST"]
)
@user_required
def result(category_id, test_id):

    category_data = fetchone(
        """
        SELECT *
        FROM categories
        WHERE id = %s
        """,
        (category_id,)
    )

    test_data = fetchone(
        """
        SELECT *
        FROM tests
        WHERE id = %s
        AND category_id = %s
        """,
        (
            test_id,
            category_id
        )
    )

    if not category_data or not test_data:

        return "Test not found", 404

    questions = fetchall(
        """
        SELECT
            id,
            correct_answer
        FROM questions
        WHERE test_id = %s
        ORDER BY id
        """,
        (test_id,)
    )

    if not questions:

        return "No questions found.", 404

    score = 0

    for index, question in enumerate(questions):

        user_answer = request.form.get(
            "question" + str(index)
        )

        correct_answer = question[
            "correct_answer"
        ]

        if user_answer == correct_answer:

            score += 1

    total = len(questions)

    if total > 0:

        percentage = round(
            (score / total) * 100,
            2
        )

    else:

        percentage = 0

    # Save result
    execute(
        """
        INSERT INTO results
        (
            user_id,
            test_id,
            score,
            total,
            percentage
        )
        VALUES
        (%s, %s, %s, %s, %s)
        """,
        (
            session["user_id"],
            test_id,
            score,
            total,
            percentage
        )
    )

    return render_template(
        "result.html",
        category=category_id,
        test_id=test_id,
        category_name=category_data["name"],
        test_name=test_data["test_name"],
        score=score,
        total=total,
        percentage=percentage
    )


# =========================================================
# ADMIN LOGIN
# =========================================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        admin = fetchone(
            """
            SELECT *
            FROM admins
            WHERE username = %s
            """,
            (username,)
        )

        if not admin:

            flash(
                "Invalid admin credentials.",
                "danger"
            )

            return redirect(
                url_for("admin_login")
            )

        if not check_password_hash(
            admin["password"],
            password
        ):

            flash(
                "Invalid admin credentials.",
                "danger"
            )

            return redirect(
                url_for("admin_login")
            )

        session.clear()

        session["admin_id"] = admin["id"]
        session["admin_username"] = admin["username"]

        return redirect(
            url_for("admin_dashboard")
        )

    return render_template(
        "admin_login.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect(
        url_for("admin_login")
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@app.route("/admin")
@admin_required
def admin_dashboard():

    stats = {

        "users": fetchone(
            "SELECT COUNT(*) AS n FROM users"
        )["n"],

        "categories": fetchone(
            "SELECT COUNT(*) AS n FROM categories"
        )["n"],

        "tests": fetchone(
            "SELECT COUNT(*) AS n FROM tests"
        )["n"],

        "questions": fetchone(
            "SELECT COUNT(*) AS n FROM questions"
        )["n"],

        "attempts": fetchone(
            "SELECT COUNT(*) AS n FROM results"
        )["n"]
    }

    return render_template(
        "admin_dashboard.html",
        stats=stats
    )


# =========================================================
# ADMIN - CATEGORIES
# =========================================================

@app.route(
    "/admin/categories",
    methods=["GET", "POST"]
)
@admin_required
def admin_categories():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        if not name:

            flash(
                "Category name is required.",
                "danger"
            )

            return redirect(
                url_for("admin_categories")
            )

        try:

            execute(
                """
                INSERT INTO categories
                (name)
                VALUES (%s)
                """,
                (name,)
            )

            flash(
                "Category added successfully.",
                "success"
            )

        except Error:

            flash(
                "Category already exists or could not be added.",
                "danger"
            )

        return redirect(
            url_for("admin_categories")
        )

    categories = fetchall(
        """
        SELECT
            c.id,
            c.name,
            COUNT(t.id) AS test_count
        FROM categories c
        LEFT JOIN tests t
            ON t.category_id = c.id
        GROUP BY
            c.id,
            c.name
        ORDER BY c.id
        """
    )

    return render_template(
        "admin_categories.html",
        categories=categories
    )


# =========================================================
# ADMIN - DELETE CATEGORY
# =========================================================

@app.post(
    "/admin/categories/delete/<int:category_id>"
)
@admin_required
def delete_category(category_id):

    execute(
        """
        DELETE FROM categories
        WHERE id = %s
        """,
        (category_id,)
    )

    flash(
        "Category deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_categories")
    )


# =========================================================
# ADMIN - TESTS
# =========================================================

@app.route(
    "/admin/tests",
    methods=["GET", "POST"]
)
@admin_required
def admin_tests():

    if request.method == "POST":

        category_id = request.form.get(
            "category_id"
        )

        test_name = request.form.get(
            "test_name",
            ""
        ).strip()

        if not category_id or not test_name:

            flash(
                "Please fill all fields.",
                "danger"
            )

            return redirect(
                url_for("admin_tests")
            )

        execute(
            """
            INSERT INTO tests
            (
                category_id,
                test_name
            )
            VALUES
            (%s, %s)
            """,
            (
                category_id,
                test_name
            )
        )

        flash(
            "Test added successfully.",
            "success"
        )

        return redirect(
            url_for("admin_tests")
        )

    categories = fetchall(
        """
        SELECT *
        FROM categories
        ORDER BY name
        """
    )

    tests = fetchall(
        """
        SELECT
            t.id,
            t.test_name,
            c.name AS category_name,
            COUNT(q.id) AS question_count
        FROM tests t
        JOIN categories c
            ON c.id = t.category_id
        LEFT JOIN questions q
            ON q.test_id = t.id
        GROUP BY
            t.id,
            t.test_name,
            c.name
        ORDER BY t.id
        """
    )

    return render_template(
        "admin_tests.html",
        categories=categories,
        tests=tests
    )


# =========================================================
# ADMIN - DELETE TEST
# =========================================================

@app.post(
    "/admin/tests/delete/<int:test_id>"
)
@admin_required
def delete_test(test_id):

    execute(
        """
        DELETE FROM tests
        WHERE id = %s
        """,
        (test_id,)
    )

    flash(
        "Test and its questions deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_tests")
    )


# =========================================================
# ADMIN - ADD QUESTION
# =========================================================

@app.route(
    "/admin/questions",
    methods=["GET", "POST"]
)
@admin_required
def admin_questions():

    tests = fetchall(
        """
        SELECT
            t.id,
            t.test_name,
            c.name AS category_name
        FROM tests t
        JOIN categories c
            ON c.id = t.category_id
        ORDER BY
            c.id,
            t.id
        """
    )

    if request.method == "POST":

        test_id = request.form.get(
            "test_id"
        )

        question = request.form.get(
            "question",
            ""
        ).strip()

        option_a = request.form.get(
            "option_a",
            ""
        ).strip()

        option_b = request.form.get(
            "option_b",
            ""
        ).strip()

        option_c = request.form.get(
            "option_c",
            ""
        ).strip()

        option_d = request.form.get(
            "option_d",
            ""
        ).strip()

        correct_answer = request.form.get(
            "correct_answer",
            ""
        ).strip().upper()

        # Validation
        if (
            not test_id
            or not question
            or not option_a
            or not option_b
            or not option_c
            or not option_d
            or correct_answer not in ["A", "B", "C", "D"]
        ):

            flash(
                "Please fill every field correctly.",
                "danger"
            )

            return redirect(
                url_for("admin_questions")
            )

        execute(
            """
            INSERT INTO questions
            (
                test_id,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            )
            VALUES
            (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                test_id,
                question,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer
            )
        )

        flash(
            "Question added successfully.",
            "success"
        )

        return redirect(
            url_for("admin_questions")
        )

    return render_template(
        "admin_questions.html",
        tests=tests
    )


# =========================================================
# ADMIN - MANAGE QUESTIONS
# =========================================================

@app.route("/admin/manage-questions")
@admin_required
def admin_manage_questions():

    questions = fetchall(
        """
        SELECT
            q.id,
            q.question,
            q.option_a,
            q.option_b,
            q.option_c,
            q.option_d,
            q.correct_answer,
            t.test_name,
            c.name AS category_name
        FROM questions q
        JOIN tests t
            ON t.id = q.test_id
        JOIN categories c
            ON c.id = t.category_id
        ORDER BY q.id DESC
        """
    )

    return render_template(
        "admin_manage_questions.html",
        questions=questions
    )


# =========================================================
# ADMIN - EDIT QUESTION
# =========================================================

@app.route(
    "/admin/questions/edit/<int:question_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_question(question_id):

    question = fetchone(
        """
        SELECT *
        FROM questions
        WHERE id = %s
        """,
        (question_id,)
    )

    if not question:

        return "Question not found", 404

    tests = fetchall(
        """
        SELECT
            t.id,
            t.test_name,
            c.name AS category_name
        FROM tests t
        JOIN categories c
            ON c.id = t.category_id
        ORDER BY
            c.id,
            t.id
        """
    )

    if request.method == "POST":

        test_id = request.form.get(
            "test_id"
        )

        question_text = request.form.get(
            "question",
            ""
        ).strip()

        option_a = request.form.get(
            "option_a",
            ""
        ).strip()

        option_b = request.form.get(
            "option_b",
            ""
        ).strip()

        option_c = request.form.get(
            "option_c",
            ""
        ).strip()

        option_d = request.form.get(
            "option_d",
            ""
        ).strip()

        correct_answer = request.form.get(
            "correct_answer",
            ""
        ).strip().upper()

        if (
            not test_id
            or not question_text
            or not option_a
            or not option_b
            or not option_c
            or not option_d
            or correct_answer not in ["A", "B", "C", "D"]
        ):

            flash(
                "Please fill every field correctly.",
                "danger"
            )

            return redirect(
                url_for(
                    "edit_question",
                    question_id=question_id
                )
            )

        execute(
            """
            UPDATE questions
            SET
                test_id = %s,
                question = %s,
                option_a = %s,
                option_b = %s,
                option_c = %s,
                option_d = %s,
                correct_answer = %s
            WHERE id = %s
            """,
            (
                test_id,
                question_text,
                option_a,
                option_b,
                option_c,
                option_d,
                correct_answer,
                question_id
            )
        )

        flash(
            "Question updated successfully.",
            "success"
        )

        return redirect(
            url_for("admin_manage_questions")
        )

    return render_template(
        "admin_edit_question.html",
        question=question,
        tests=tests
    )


# =========================================================
# ADMIN - DELETE QUESTION
# =========================================================

@app.post(
    "/admin/questions/delete/<int:question_id>"
)
@admin_required
def delete_question(question_id):

    execute(
        """
        DELETE FROM questions
        WHERE id = %s
        """,
        (question_id,)
    )

    flash(
        "Question deleted successfully.",
        "success"
    )

    return redirect(
        url_for("admin_manage_questions")
    )


# =========================================================
# ADMIN - USERS
# =========================================================

@app.route("/admin/users")
@admin_required
def admin_users():

    users = fetchall(
        """
        SELECT
            u.id,
            u.name,
            u.email,
            u.created_at,
            COUNT(r.id) AS attempts
        FROM users u
        LEFT JOIN results r
            ON r.user_id = u.id
        GROUP BY
            u.id,
            u.name,
            u.email,
            u.created_at
        ORDER BY u.id DESC
        """
    )

    return render_template(
        "admin_users.html",
        users=users
    )


# =========================================================
# ADMIN - RESULTS
# =========================================================

@app.route("/admin/results")
@admin_required
def admin_results():

    results = fetchall(
        """
        SELECT
            r.*,
            u.name,
            u.email,
            t.test_name,
            c.name AS category_name
        FROM results r
        JOIN users u
            ON u.id = r.user_id
        JOIN tests t
            ON t.id = r.test_id
        JOIN categories c
            ON c.id = t.category_id
        ORDER BY r.created_at DESC
        """
    )

    return render_template(
        "admin_results.html",
        results=results
    )


# =========================================================
# DATABASE TEST
# =========================================================

@app.route("/db-test")
def db_test():

    try:

        categories = fetchall(
            """
            SELECT *
            FROM categories
            ORDER BY id
            """
        )

        return {
            "status": "connected",
            "categories": categories
        }

    except Error as error:

        return {
            "status": "error",
            "message": str(error)
        }, 500


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

