import configparser
import os
import random
from requests import get, post

from email_hunter import EmailHunterClient
from faker import Faker
from faker.providers import internet

import automated_bot


class BotService:
    def __init__(self):
        config = configparser.ConfigParser()
        cwd = os.path.abspath(automated_bot.__path__[0])
        file_path = os.path.join(cwd, 'settings.ini')
        config.read(file_path)
        self._config = config

        fake = Faker()
        fake.add_provider(internet)

        self._fake = fake
        self._email_hunter_client = EmailHunterClient(config.get('bot', 'EMAIL_HUNTER_KEY'))

    @property
    def config(self):
        return self._config

    @property
    def email_hunter_client(self):
        return self._email_hunter_client

    @property
    def fake(self):
        return self._fake

    def process(self):
        print('Bot [initialization]')
        number_of_users = self.config.getint('bot', 'NUMBER_OF_USERS')
        max_posts_per_user = self.config.getint('bot', 'MAX_POSTS_PER_USER')
        max_likes_per_user = self.config.getint('bot', 'MAX_LIKES_PER_USER')
        need_iterate = True

        print('Bot [started]')

        users_list = self.signup(number_of_users)
        tokens_list = self.login(users_list)

        self.create_posts(tokens_list, max_posts_per_user)

        users = self.get_users()['results']
        posts = self.get_posts(tokens_list[0])['results']

        # start liking posts
        while users and need_iterate:
            # sorting by user posts quantity to get index of User with maximum posts
            user_with_max_posts_index = users.index(max(users, key=lambda user: len(user['posts'])))
            user = users.pop(user_with_max_posts_index)
            token = tokens_list.pop(user_with_max_posts_index)
            counter = 0
            likes_rndm = []

            while counter < max_likes_per_user:
                r = random.randint(0, len(posts) - 1)
                while r in likes_rndm:
                    r = random.randint(0, len(posts) - 1)

                post_id_rndm = r

                user_rndm = self.get_user(posts[post_id_rndm])
                post_with_zero_likes_exists = min(
                    self.get_likes_counter(p['id'], token) for p in user_rndm['posts']) == 0

                if user_rndm['id'] != user['id'] and post_with_zero_likes_exists:
                    # self.like(posts[post_id_rndm], token)
                    likes_rndm.append(post_id_rndm)
                    counter += 1

            # getting fresh list of posts and checking if there any post with zero likes
            for p in self.get_posts(token):
                if p['likes_counter'] == 0:
                    need_iterate = True
                    break

        for post in self.get_posts(tokens_list[0]):
            print(f"Post with ID {post['id']} has {post['likes_counter']} likes")

        print("Bot [finished]")

    def signup(self, number_of_users):
        """
        Users registration(sign-up).
        """
        print("Bot [signup users (number provided in config)]")
        new_users = []
        emails = self.email_hunter_client.search('microsoft.com')

        for i in range(number_of_users):
            user = {
                'username': self.fake.user_name(),
                'password': self.fake.password(),
            }

            print({
                    'username': user['username'],
                    'password': user['password'],
                    'email': emails[i]['value']
                })

            response = post(
                f"{self.config['api']['BASE_URL']}users/",
                data={
                    'username': user['username'],
                    'password': user['password'],
                    'email': emails[i]['value']
                }
            )

            if response.status_code != 201:
                raise RuntimeError("User create error.")

            new_users.append(user)

        return new_users

    def login(self, users):
        """
        Users token obtain.
        """
        print("Bot [users login]")
        data = []

        for u in users:
            response = post(
                f"{self.config['api']['BASE_URL']}token/",
                data={
                    'username': u['username'],
                    'password': u['password']
                }
            )

            if response.status_code != 200:
                raise RuntimeError("User login error.")

            data.append(response.json())

        return data

    def create_posts(self, tokens_list, max_posts_per_user):
        """
        Create random number of posts for users.
        """
        print("Bot [each user creates random number of posts with any content (up to max_posts_per_user)]")
        data = []

        for token in tokens_list:
            for i in range(random.randrange(1, max_posts_per_user)):
                response = post(
                    f"{self.config['api']['BASE_URL']}posts/",
                    headers={'Authorization': f"Bearer {token['access']}"},
                    data={
                        'title': self.fake.text(),
                        'body': self.fake.text()
                    }
                )

                if response.status_code != 201:
                    raise RuntimeError("Create post error.")

                data.append(response.json())

        return data

    def get_posts(self, token):
        """
        Get list of posts.
        """
        print("Bot [getting posts list]")
        response = get(
            f"{self.config['api']['BASE_URL']}posts/",
            headers={'Authorization': f"Bearer {token['access']}"}
        )

        if response.status_code != 200:
            raise RuntimeError("Posts list error.")

        return response.json()

    def get_user(self, params):
        """
        Get single user.
        """
        print("Bot [get single user]")
        response = get(
            f"{self.config['api']['BASE_URL']}users/{str(params['user']['id'])}/"
        )

        if response.status_code != 200:
            raise RuntimeError("Get user error.")

        return response.json()

    def get_users(self):
        """
        Get list of users.
        """
        print("Bot [get list of users]")
        response = get(
            f"{self.config['api']['BASE_URL']}users/",
        )

        if response.status_code != 200:
            raise RuntimeError("Get users list error.")

        return response.json()

    def get_likes_counter(self, post_id, token):
        """
        Get number for given post
        """
        response = get(
            f"{self.config['api']['BASE_URL']}posts/{str(post_id)}/",
            headers={'Authorization': f"Bearer {token['access']}"}
        )

        if response.status_code != 200:
            raise RuntimeError("Post likes get failed.")

        return response.json()['likes_counter']

    def like(self, post, token):
        response = post(
            f"{self.config['api']['BASE_URL']}posts/{str(post['id'])}/like/",
            headers={'Authorization': "Bearer " + token['access']}
        )

        if response.status_code != 200:
            raise RuntimeError("Post like action failed.")

        return response.json()
