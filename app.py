from flask import Flask, render_template, send_from_directory, jsonify, request,redirect,session,url_for
from flask_mysqldb import MySQL
import json
from flask_session import Session
import os

app = Flask(__name__)

# Configure MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'sensor_data'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['SECRET_KEY'] = 'utec123'  # Establece una clave secreta para la sesión
app.config['SESSION_TYPE'] = 'filesystem'  # Almacena la sesión en el sistema de archivos
Session(app)
mysql = MySQL(app)

# Variables para almacenar los valores de temperatura
sensor1_temp = None
sensor2_temp = None
sensor3_temp = None
sensor4_temp = None
sensor5_temp = None
sensor6_temp = None

# Variables para almacenar los valores de humedad 
sensor1_hum = None
sensor2_hum = None
sensor3_hum = None
sensor4_hum = None
sensor5_hum = None
sensor6_hum = None

@app.route('/')
def index():
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        details = request.form
        username = details['username']
        email = details['email']
        password = details['password']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(username, email, password) VALUES (%s, %s, %s)", (username, email, password,))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# Ruta para el formulario de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        details = request.form
        username = details['username']
        password = details['password']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password,))
        user = cur.fetchone()
        if user:
            session['username'] = user['username'] 
            return render_template('index.html')
        
        else:
            return 'Error en el inicio de sesión'
    return render_template('login.html')

@app.route('/sensor-data', methods=['POST'])
def receive_sensor_data():
    global sensor1_temp, sensor2_temp, sensor3_temp, sensor4_temp, sensor5_temp, sensor6_temp
    global sensor1_hum, sensor2_hum, sensor3_hum, sensor4_hum, sensor5_hum, sensor6_hum
    # Obtener los datos del sensor de la solicitud POST
    data = request.get_json()
    temperature = data.get("temperature")
    humidity = data.get("humidity")
    

    if temperature is None or humidity is None:
        return jsonify({'error': 'Invalid data format'}), 400
    
    sensor1_temp = temperature
    sensor1_hum = humidity
    # Insertar los datos en la base de datos
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO temperature_records (temperature) VALUES (%s)", (temperature,))
    cur.execute("INSERT INTO humidity_records (humidity) VALUES (%s)", (humidity,))
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

@app.route('/humidity-values') 
def humidity_values():
    # Obtener los últimos valores de humedad de la base de datos
    cur = mysql.connection.cursor()
    cur.execute("SELECT humidity, DATE_FORMAT(timestamp, '%H:%i') AS time FROM humidity_records ORDER BY timestamp DESC LIMIT 1")
    result = cur.fetchone()
    cur.close()

    if result:
        humidity = result['humidity']
        timestamp = result['time']
    else:
        humidity = 'N/A'
        timestamp = 'N/A'

    # Crear un diccionario con los valores de temperatura
    humidity_values = {
        'sensor1': sensor1_hum,
        'sensor2': sensor2_hum,
        'sensor3': sensor3_hum,
        'sensor4': sensor4_hum,
        'sensor5': sensor5_hum,
        'sensor6': sensor6_hum,
        'database': humidity,
        'timestamp': timestamp
    }

    # Devolver los valores de temperatura en formato JSON
    return jsonify(humidity_values)

#FUNCIONES USADAS PARA MANDAR DATOS A LOS GRAFICOS

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

@app.route('/obtener-alertas')
def obtener_alertas():
    # Obtener los datos de temperatura y humedad desde las rutas existentes
    response_temperatura = app.test_client().get('/datos_temperatura')
    response_humedad = app.test_client().get('/datos_humedad')

    # Extraer los datos de temperatura y humedad de las respuestas
    datos_temperatura = json.loads(response_temperatura.data)
    datos_humedad = json.loads(response_humedad.data)

    # Obtener los últimos valores de temperatura y humedad
    ultima_temperatura = datos_temperatura['temperatura'][-1]
    ultima_humedad = datos_humedad['humedad'][-1]

    # Verificar las condiciones de alerta
    temperatura_alerta = ultima_temperatura > 30
    humedad_alerta = ultima_humedad < 70

    # Crear un diccionario con los resultados de alerta
    resultado_alertas = {
        'temperatura_alerta': temperatura_alerta,
        'humedad_alerta': humedad_alerta
    }

    # Devolver los resultados en formato JSON
    return jsonify(resultado_alertas)

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
