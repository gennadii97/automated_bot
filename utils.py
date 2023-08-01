from datetime import datetime
import json
import os
import random
import requests


def save_user_to_file(users):
    if os.path.isfile('users.json'):
        with open('users.json', 'r', encoding='utf-8') as file:
            users_from_file = json.loads(file.read())
    else:
        users_from_file = []
    for user in users:
        tom_index = next((index for (index, u) in enumerate(users_from_file) if u["username"] == user["username"]),
                         None)
        if tom_index is not None:
            users_from_file[tom_index] = user
        else:
            users_from_file.append(user)

    with open('users.json', 'w', encoding='utf-8') as file:
        json.dump(users_from_file, file)


def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]


def get_random_users(count=1):
    url = f'https://randomuser.me/api/?results={count}'
    try:
        response = requests.request('GET', url)
        with open(f'new_users{datetime.utcnow()}.json', 'w', encoding='utf-8') as file:
            file.write(response.text)
    except BaseException as e:
        print(e)

    users = response.json()['results']
    users = [{'username': user['login']['username'], 'password': user['login']['password'] + user['login']['salt'],
              'email': user['email']} for user in users]
    return users


def get_auth_header(token):
    return {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token["access"]}'
    }
