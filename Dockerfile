# Usa la imagen base de Python
FROM python:3.9

# Establece el directorio de trabajo en /app
WORKDIR /app

# Copia el archivo requirements.txt al contenedor
COPY requeriments.txt .

# Instala las dependencias especificadas en el archivo requirements.txt
RUN pip install --no-cache-dir -r requeriments.txt

# Copia el resto de los archivos de la aplicación al contenedor
COPY . .

# Expone el puerto 5000 para acceder a la aplicación Flask
EXPOSE 5000

# Establece la variable de entorno FLASK_APP en el nombre del archivo principal de la aplicación
ENV FLASK_APP=app.py

# Comando para ejecutar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0"]
