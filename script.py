import requests

# URL веб-сервиса
base_url = 'http://localhost:5000'

# Создание пользователя
def create_user(name):
    url = f'{base_url}/users'
    data = {'name': name}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data['user_id']
        token = user_data['token']
        print('Пользователь создан:')
        print('ID:', user_id)
        print('Токен:', token)
    else:
        print('Ошибка при создании пользователя:', response.text)

# Добавление аудиозаписи
def add_audio(user_id, token, audio_file):
    url = f'{base_url}/audios'
    files = {'audio': open(audio_file, 'rb')}
    data = {'user_id': user_id, 'token': token}
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        download_url = response.json()['url']
        print('Аудиозапись добавлена:')
        print('URL для скачивания:', download_url)
    else:
        print('Ошибка при добавлении аудиозаписи:', response.text)

# Получение аудиозаписи
def download_audio(url):
    response = requests.get(url)
    if response.status_code == 200:
        filename = url.split('=')[-1] + '.mp3'
        with open(filename, 'wb') as file:
            file.write(response.content)
        print('Аудиозапись успешно скачана:', filename)
    else:
        print('Ошибка при скачивании аудиозаписи:', response.text)


# Пример использования

# Создание пользователя
create_user('John Doe')

# Добавление аудиозаписи
user_id = '<вставьте сюда ID пользователя>'
token = '<вставьте сюда токен пользователя>'
audio_file = 'audio.wav'
add_audio(user_id, token, audio_file)

# Получение аудиозаписи
audio_id = '<вставьте сюда ID аудиозаписи>'
url = f'{base_url}/record?id={audio_id}&user={user_id}'
download_audio(url)
