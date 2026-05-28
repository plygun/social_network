"""Synthetic-traffic bot: signs up N users, creates posts, and likes them via the public API."""
import logging
import random

import requests
from decouple import config
from faker import Faker
from faker.providers import internet

logger = logging.getLogger(__name__)


class BotService:
    def __init__(self):
        self.base_url = config('BOT_API_BASE_URL', default='http://localhost:8000/v1/')
        self.number_of_users = config('BOT_NUMBER_OF_USERS', default=5, cast=int)
        self.max_posts_per_user = config('BOT_MAX_POSTS_PER_USER', default=3, cast=int)
        self.max_likes_per_user = config('BOT_MAX_LIKES_PER_USER', default=7, cast=int)

        self.fake = Faker()
        self.fake.add_provider(internet)

    def process(self) -> None:
        logger.info("Bot starting: %d users, up to %d posts and %d likes each",
                    self.number_of_users, self.max_posts_per_user, self.max_likes_per_user)

        users = self._signup(self.number_of_users)
        tokens = self._login(users)
        self._create_posts(tokens)
        self._spread_likes(users, tokens)
        self._report(tokens[0])

        logger.info("Bot finished")

    # ---------- API wrappers ----------

    def _url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    def _auth(self, token: dict) -> dict:
        return {'Authorization': f"Bearer {token['access']}"}

    def _signup(self, count: int) -> list[dict]:
        users = []
        for _ in range(count):
            credentials = {
                'username': self.fake.user_name(),
                'password': self.fake.password(),
                'email': self.fake.unique.email(),
            }
            response = requests.post(self._url('users/'), data=credentials, timeout=10)
            response.raise_for_status()
            users.append(credentials)
        logger.info("Signed up %d users", len(users))
        return users

    def _login(self, users: list[dict]) -> list[dict]:
        tokens = []
        for u in users:
            response = requests.post(
                self._url('token/'),
                data={'username': u['username'], 'password': u['password']},
                timeout=10,
            )
            response.raise_for_status()
            tokens.append(response.json())
        return tokens

    def _create_posts(self, tokens: list[dict]) -> None:
        for token in tokens:
            for _ in range(random.randint(1, self.max_posts_per_user)):
                response = requests.post(
                    self._url('posts/'),
                    headers=self._auth(token),
                    data={'title': self.fake.sentence(), 'body': self.fake.paragraph()},
                    timeout=10,
                )
                response.raise_for_status()

    def _list_posts(self, token: dict) -> list[dict]:
        response = requests.get(self._url('posts/'), headers=self._auth(token), timeout=10)
        response.raise_for_status()
        return response.json()['results']

    def _like(self, post_id: int, token: dict) -> None:
        response = requests.post(
            self._url(f'posts/{post_id}/like/'),
            headers=self._auth(token),
            timeout=10,
        )
        response.raise_for_status()

    # ---------- Liking strategy ----------

    def _spread_likes(self, users: list[dict], tokens: list[dict]) -> None:
        """Each user likes up to max_likes_per_user posts that aren't theirs."""
        posts_by_user = self._user_id_by_username(users, tokens)
        for user, token in zip(users, tokens):
            own_id = posts_by_user[user['username']]
            posts = [p for p in self._list_posts(token) if p['user']['id'] != own_id]
            random.shuffle(posts)
            for post in posts[: self.max_likes_per_user]:
                self._like(post['id'], token)

    def _user_id_by_username(self, users: list[dict], tokens: list[dict]) -> dict:
        """Map username → user id by listing the public users endpoint once."""
        response = requests.get(self._url('users/'), timeout=10)
        response.raise_for_status()
        mapping = {row['username']: row['id'] for row in response.json()['results']}
        return {u['username']: mapping[u['username']] for u in users if u['username'] in mapping}

    def _report(self, token: dict) -> None:
        for post in self._list_posts(token):
            logger.info("Post %s by %s has %s likes",
                        post['id'], post['user']['username'], post['likes_count'])
