from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import requests

app = Flask(__name__)

def init_db():
    with sqlite3.connect("menu.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT NOT NULL,
                          description TEXT NOT NULL,
                          price TEXT NOT NULL)''')
        conn.commit()

init_db()

def get_menu_items():
    with sqlite3.connect("menu.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price FROM menu")
        return cursor.fetchall()

def add_menu_item(name, description, price):
    with sqlite3.connect("menu.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO menu (name, description, price) VALUES (?, ?, ?)", (name, description, price))
        conn.commit()

def update_menu_item(item_id, name, description, price):
    with sqlite3.connect("menu.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE menu SET name = ?, description = ?, price = ? WHERE id = ?",
                       (name, description, price, item_id))
        conn.commit()

def delete_menu_item(item_id):
    with sqlite3.connect("menu.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM menu WHERE id = ?", (item_id,))
        conn.commit()

def get_weather(city):
    api_key = "ENTER-API-KEY-HERE"
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric", "lang": "uk"}
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error = None
    if request.method == "POST":
        city = request.form.get("city")
        if city:
            weather_data = get_weather(city)
            if not weather_data:
                error = "Не вдалося знайти дані для цього міста."
    return render_template("index.html", weather_data=weather_data, error=error)

@app.route("/menu")
def menu():
    menu_items = get_menu_items()
    return render_template("menu.html", menu_items=menu_items)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        price = request.form["price"]
        add_menu_item(name, description, price)
        return redirect(url_for("menu"))
    return render_template("admin.html")

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["descriptio"]
        price = request.form["price"]
        update_menu_item(item_id, name, description, price)
        return redirect(url_for("menu"))

    with sqlite3.connect("menu.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price FROM menu WHERE id = ?", (item_id,))
        item = cursor.fetchone()
        
        return render_template("edit.html", item=item)

@app.route("/delete/<int:item_id>")
def delete(item_id):
    delete_menu_item(item_id)
    return redirect(url_for("menu"))



if __name__ == "__main__":
    app.run(debug=True)
