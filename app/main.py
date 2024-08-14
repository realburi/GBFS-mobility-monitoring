from flask import Flask, render_template
import os 
import requests

app = Flask(__name__)

questDB_host = os.environ.get('QUESTDB_HOST', 'http://localhost:9000')

@app.route('/')
def index():
    sql_query = "select * from my_table; order by timestamp"
    response = requests.get(
        f'{questDB_host}/exec',
        params={'query': sql_query}
    )
    result = [] 
    keys = ['current_range_meters', 'is_disabled_count', 'is_reserved_count', 'city', 'timestamp']
    for data in response.json().get('dataset'):
        result.append(dict(zip(keys, data)))

    breda = [x for x in result if x.get('city') == 'breda']
    almere = [x for x in result if x.get('city') == 'almere']
    delft = [x for x in result if x.get('city') == 'delft']

    return render_template('index.html', breda=breda, almere=almere, delft=delft)


# @app.route('/api/data')
# def get_data():
#     sql_query = "select * from my_table; order by  timestamp"
#     response = requests.get(
#         f'{questDB_host}/exec',
#         params={'query': sql_query}
#     )
#     result = []
#     keys = ['current_range_meters', 'is_disabled_count', 'is_reserved_count', 'city', 'timestamp']
#     for data in response.json().get('dataset'):
#         result.append(dict(zip(keys, data)))

#     return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)