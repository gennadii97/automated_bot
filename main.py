import random
import lorem
import requests
import json
import numpy as np
import os

from utils import flatten_comprehension, get_auth_header, get_random_users, save_user_to_file

from dotenv import load_dotenv

load_dotenv()

NUMBER_OF_USERS = 10
MAX_NUMBER_OF_POSTS_PER_USER = 5
MAX_LIKES_PER_USER = 5
BASE_URL = os.getenv('BASE_URL')
TOKEN_URL = os.getenv('TOKEN_URL')
USERS_URL = os.getenv('USERS_URL')
POSTS_URL = os.getenv('POSTS_URL')
LIKES_URL = os.getenv('LIKES_URL')


def get_token(username, password):
    url = f'{BASE_URL}{TOKEN_URL}'

    payload = {'username': username, 'password': password}

    headers = {}

    response = requests.request('POST', url, headers=headers, data=payload)

    return response.json()


def create_user(username, password):
    url = f'{BASE_URL}{USERS_URL}'

    payload = json.dumps({
        'username': username,
        'password': password
    })

    response = requests.request('POST', url, data=payload, headers={'Content-Type': 'application/json', })

    return response


def create_users(users=[]):
    results = {'successful': [], 'failed': []}
    for user in users:
        try:
            response = create_user(username=user['username'],
                                   password=user['password'])
            if response.status_code == 201:
                results['successful'].append(user)
            else:
                results['failed'].append(user)
        except BaseException as e:
            print(e)
    save_user_to_file(results['successful'])

    return results


def create_posts(user, posts_limit):
    token = get_token(username=user['username'], password=user['password'])
    url = f'{BASE_URL}{POSTS_URL}'
    posts = []
    for i in range(random.randint(1, posts_limit)):
        payload = json.dumps({
            'title': lorem.sentence(),
            'content': lorem.paragraph()
        })
        headers = get_auth_header(token)

        response = requests.request('POST', url, headers=headers, data=payload)
        if response.status_code == 201:
            posts.append(response.json())
    return posts


def create_posts_for_users(userslist, posts_limit):
    for user in userslist:
        posts = create_posts(user, posts_limit)
        user['posts'] = posts
    save_user_to_file(userslist)
    return userslist


def batch_add_likes(users, likes_limit):
    posts = flatten_comprehension([user['posts'] for user in users])
    for user in users:
        selected_posts = np.random.choice(posts, size=random.randint(1, likes_limit))
        like_posts(user, selected_posts)


def like_posts(user, posts):
    results = {'successful': 0, 'failed': 0}
    token = get_token(username=user['username'], password=user['password'])
    for post in posts:
        headers = get_auth_header(token)
        url = f'{BASE_URL}{POSTS_URL}{post["id"]}{LIKES_URL}'
        response = requests.request('GET', url, headers=headers)
        if response.status_code == 200:
            results['successful'] += 1
        else:
            results['failed'] += 1


if __name__ == '__main__':
    users = get_random_users(NUMBER_OF_USERS)
    results = create_users(users)
    users = create_posts_for_users(results['successful'], MAX_NUMBER_OF_POSTS_PER_USER)
    likes_results = batch_add_likes(users, MAX_LIKES_PER_USER)

