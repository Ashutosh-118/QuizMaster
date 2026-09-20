
import mysql.connector
from getpass import getpass
from werkzeug.security import generate_password_hash


# =========================================================
# DATABASE CONNECTION
# =========================================================

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="quiz_game"
)

cursor = db.cursor()


# =========================================================
# ADMIN DETAILS
# =========================================================

username = input("Enter admin username: ").strip()

password = getpass("Enter admin password: ")

confirm = getpass("Confirm admin password: ")


# =========================================================
# VALIDATION
# =========================================================

if not username:

    print("Username cannot be empty.")


elif len(password) < 6:

    print("Password must contain at least 6 characters.")


elif password != confirm:

    print("Passwords do not match.")


else:

    try:

        hashed_password = generate_password_hash(password)

        cursor.execute(
            """
            INSERT INTO admins
            (username, password)
            VALUES (%s, %s)
            """,
            (
                username,
                hashed_password
            )
        )

        db.commit()

        print()
        print("===================================")
        print("Admin account created successfully!")
        print("Username:", username)
        print("===================================")

    except mysql.connector.Error as error:

        print()
        print("Could not create admin.")
        print("Error:", error)


# =========================================================
# CLOSE DATABASE
# =========================================================

cursor.close()
db.close()

