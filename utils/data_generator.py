import random
from faker import Faker
from datetime import timedelta

faker = Faker("ru_RU")


class DataGenerator:
    @staticmethod
    def generate_movie_data(genre_id=1):
        return {
            "name": f"{faker.catch_phrase()} {random.randint(100, 9999)}",
            "imageUrl": faker.image_url(),
            "price": random.randint(100, 1500),
            "description": faker.text(max_nb_chars=150),
            "location": random.choice(["MSK", "SPB"]),
            "published": True,
            "genreId": genre_id
        }

    @staticmethod
    def generate_random_email():
        random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return f"kek{random_string}@gmail.com"



    @staticmethod
    def generate_random_password():
        random_string = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=5))
        return f"Kek{random_string}"

    @staticmethod
    def generate_random_name() -> str:
        return faker.name()