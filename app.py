from flask import Flask, render_template, send_from_directory, jsonify, request, redirect, url_for
from flask_mysqldb import MySQL
import os

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sensor_data'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Variables para almacenar los valores de temperatura
sensor1_temp = None
sensor2_temp = None
sensor3_temp = None
sensor4_temp = None
sensor5_temp = None
sensor6_temp = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/login.html', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        details = request.form
        username = details['username']
        clave = details['clave']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM alumnos WHERE username=%s AND clave=%s", (username, clave,))
        user = cur.fetchone()
        if user:
            return render_template('../index.html')
        else:
            return render_template('../index.html')
    return render_template('/static/login.html')

@app.route('/static/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        details = request.form
        username = details['username']
        nombre = details['nombre']
        apellidos = details['apellidos']
        clave = details['clave']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO alumnos(username, nombre, apellidos, clave) VALUES (%s, %s, %s, %s)", (username, nombre, apellidos, clave,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template({{url_for('static',filename='register.html')}})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    global sensor1_temp, sensor2_temp, sensor3_temp, sensor4_temp, sensor5_temp, sensor6_temp

    # Obtener los datos del sensor de la solicitud POST
    data = request.get_json()
    temperature = data['temperature']

    # Actualizar los valores de temperatura
    sensor1_temp = temperature

    # Insertar los datos en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO temperature_records (temperature) VALUES (%s)", (temperature,))
    mysql.connection.commit()
    cur.close()

    # Devolver una respuesta exitosa
    return jsonify({'message': 'Sensor data received successfully'})

@app.route('/temperature-values')
def temperature_values():
    # Obtener los últimos valores de temperatura de la base de datos
    cur = mysql.connection.cursor()
    cur.execute("SELECT temperature, DATE_FORMAT(timestamp, '%H:%i') AS time FROM temperature_records ORDER BY timestamp DESC LIMIT 1")
    result = cur.fetchone()
    cur.close()

    if result:
        temperature = result['temperature']
        timestamp = result['time']
    else:
        temperature = 'N/A'
        timestamp = 'N/A'

    # Crear un diccionario con los valores de temperatura
    temperature_values = {
        'sensor1': sensor1_temp,
        'sensor2': sensor2_temp,
        'sensor3': sensor3_temp,
        'sensor4': sensor4_temp,
        'sensor5': sensor5_temp,
        'sensor6': sensor6_temp,
        'database': temperature,
        'timestamp': timestamp
    }

    # Devolver los valores de temperatura en formato JSON
    return jsonify(temperature_values)

# Ruta para obtener los datos de temperatura y tiempo
@app.route('/datos_temperatura')
def obtener_datos_temperatura():
    # Establecer la conexión con la base de datos
    cur = mysql.connection.cursor()

    # Consultar los datos de temperatura y tiempo desde la base de datos
    cur.execute("SELECT DATE_FORMAT(timestamp, '%H:%i') AS time, temperature FROM temperature_records")
    datos = cur.fetchall()
    cur.close()

    # Extraer tiempo y temperatura de los datos
    tiempo = [dato['time'] for dato in datos]
    temperatura = [dato['temperature'] for dato in datos]

    # Crear un diccionario con los datos
    datos_temperatura = {
        'tiempo': tiempo,
        'temperatura': temperatura
    }

    # Devolver los datos en formato JSON
    return jsonify(datos_temperatura)


# Ruta para obtener los datos de humedad y tiempo
@app.route('/datos_humedad')
def obtener_datos_humedad():
    # Establecer la conexión con la base de datos
    cur = mysql.connection.cursor()

    # Consultar los datos de humedad y tiempo desde la base de datos
    cur.execute("SELECT DATE_FORMAT(timestamp, '%H:%i') AS time, humidity FROM humidity_records")
    datos = cur.fetchall()
    cur.close()

    # Extraer tiempo y humedad de los datos
    tiempo = [dato['time'] for dato in datos]
    humedad = [dato['humidity'] for dato in datos]

    # Crear un diccionario con los datos
    datos_humedad = {
        'tiempo': tiempo,
        'humedad': humedad
    }

    # Devolver los datos en formato JSON
    return jsonify(datos_humedad)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3003)
