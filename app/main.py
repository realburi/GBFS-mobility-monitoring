from flask import Flask, render_template, jsonify
import os 
import requests

app = Flask(__name__)

questDB_host = os.environ.get('QUESTDB_HOST', 'http://localhost:9000')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    sql_query = "select current_range_meters, is_disabled_count, is_reserved_count, city, timestamp from my_table; order by city, timestamp"
    response = requests.get(
        f'{questDB_host}/exec',
        params={'query': sql_query}
    )
    result = []
    keys = ['current_range_meters', 'is_disabled_count', 'is_reserved_count', 'city', 'timestamp']
    for data in response.json().get('dataset'):
        result.append(dict(zip(keys, data)))

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)