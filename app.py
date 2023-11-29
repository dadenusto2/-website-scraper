from flask import render_template, Response, request  # Remove: import Flask
import connexion

from db_conn import conn

app = connexion.App(__name__, specification_dir="./")

@app.route("/")
def home():
    with conn.cursor() as cursor:
        conn.autocommit = True

        postgreSQL_select_Query = "select * from articles"
        cursor.execute(postgreSQL_select_Query)
        print("Selecting rows from mobile table using cursor.fetchall")
        records = cursor.fetchall()
        print("Print each row and it's columns values")
    return render_template("home.html", records=records)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4565)

