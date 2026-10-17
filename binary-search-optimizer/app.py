"""Backend API (Flask) + SQLite storage."""
import json
import os
import sqlite3

from flask import Flask, jsonify, render_template, request

from solver import solve
from validation import validate

app = Flask(__name__)
DB_sPATH = os.environ.get("BSO_DB", os.path.join(os.path.dirname(__file__), "history.db"))


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS runs (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               created TEXT DEFAULT CURRENT_TIMESTAMP,
               problem TEXT, input_values TEXT, param INTEGER,
               answer INTEGER, bs_checks INTEGER, lin_checks INTEGER,
               bs_ms REAL, lin_ms REAL)"""
    )
    return conn


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/solve")
def api_solve():
    clean, errors = validate(request.get_json(silent=True))
    if errors:
        return jsonify({"ok": False, "errors": errors}), 400
    problem, values, param = clean
    result = solve(problem, values, param)

    bl = result["baseline"]
    with db() as conn:
        conn.execute(
            "INSERT INTO runs (problem,input_values,param,answer,bs_checks,lin_checks,bs_ms,lin_ms)"
            " VALUES (?,?,?,?,?,?,?,?)",
            (
                problem, json.dumps(values), param, result["answer"],
                result["binary_search"]["checks"],
                None if bl["skipped"] else bl["checks"],
                result["binary_search"]["time_ms"],
                None if bl["skipped"] else bl["time_ms"],
            ),
        )
    return jsonify({"ok": True, "result": result})


@app.get("/api/history")
def api_history():
    with db() as conn:
        rows = conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT 20").fetchall()
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    app.run(debug=True)
