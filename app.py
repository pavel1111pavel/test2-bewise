
from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import uuid
import psycopg2
import ffmpeg


# ...

def create_tables():
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(36) PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            access_token VARCHAR(36) NOT NULL
        )
    """)

    # Создание таблицы аудиозаписей
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audios (
            audio_id VARCHAR(36) PRIMARY KEY,
            user_id VARCHAR(36) NOT NULL,
            audio_file VARCHAR(255) NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = {
    'host': 'db',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'mysecretpassword'
}

def create_user(username):
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()
    user_id = str(uuid.uuid4())
    access_token = str(uuid.uuid4())
    cursor.execute("INSERT INTO users (user_id, username, access_token) VALUES (%s, %s, %s)", (user_id, username, access_token))
    conn.commit()
    cursor.close()
    conn.close()
    return user_id, access_token

def save_audio(user_id, audio_file):
    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()
    audio_id = str(uuid.uuid4())
    audio_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(audio_file.filename))
    audio_file.save(audio_file_path)

    # Convert audio to mp3
    mp3_file_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_id + '.mp3')
    ffmpeg.input(audio_file_path).output(mp3_file_path).run()

    cursor.execute("INSERT INTO audios (audio_id, user_id, audio_file) VALUES (%s, %s, %s)", (audio_id, user_id, mp3_file_path))
    conn.commit()
    cursor.close()
    conn.close()
    return audio_id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user', methods=['POST'])
def create_user_route():
    username = request.form['username']
    user_id, access_token = create_user(username)
    return jsonify({'user_id': user_id, 'access_token': access_token})

@app.route('/record', methods=['POST'])
def upload_audio():
    user_id = request.form['user_id']
    access_token = request.form['access_token']
    audio_file = request.files['audio']

    # Validate user_id and access_token

    audio_id = save_audio(user_id, audio_file)
    download_url = f"http://host:port/record?id={audio_id}&user={user_id}"
    return jsonify({'download_url': download_url})

@app.route('/record', methods=['GET'])
def download_audio():
    audio_id = request.args.get('id')
    user_id = request.args.get('user')

    # Validate audio_id and user_id

    conn = psycopg2.connect(**DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT audio_file FROM audios WHERE audio_id = %s AND user_id = %s", (audio_id, user_id))
    audio_file = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return send_from_directory(app.config['UPLOAD_FOLDER'], audio_file, as_attachment=True)

@app.route('/')
def hello():
    return 'Hello, world!'

if __name__ == '__main__':

    create_tables()
    app.run(host='0.0.0.0', port=8000)

