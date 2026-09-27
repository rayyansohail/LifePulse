from flask import Flask, render_template
import psycopg2

app = Flask(__name__)

@app.route('/')
def index():
    conn = psycopg2.connect(host="localhost", database="lifepulse_khi", user="postgres", password="admin")
    cur = conn.cursor()
    cur.execute("SELECT hospital_id, hospital_name, region, city, available_beds, icu_beds, ventilators, oxygen_cylinders, blood_units_o_neg, surgical_masks, status FROM hospital_inventory ORDER BY hospital_id;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', inventory=rows)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
