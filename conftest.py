import requests
import pytest
from clients.api_manager import ApiManager
from utils.data_generator import DataGenerator
from config.credentials import SUPER_ADMIN_CREDS


@pytest.fixture(scope="session")
def session():
    http_session = requests.Session()
    yield http_session
    http_session.close()


@pytest.fixture(scope="session")
def api_manager(session):
    return ApiManager(session)


@pytest.fixture(scope="function")
def test_user():
    password = DataGenerator.generate_random_password()
    return {
        "email": DataGenerator.generate_random_email(),
        "fullName": DataGenerator.generate_random_name(),
        "password": password,
        "passwordRepeat": password,
        "roles": ["USER"]
    }


@pytest.fixture(scope="function")
def registered_user(api_manager, test_user):
    response = api_manager.auth_api.register_user(test_user).json()
    test_user["id"] = response["id"]
    return test_user



@pytest.fixture
def super_admin_api():
    """Авторизованный ApiManager под суперадмином."""
    session = requests.Session()
    manager = ApiManager(session)
    # Авторизация через ваш AuthApi (подставьте ваши креды из констант)
    manager.auth_api.authenticate(SUPER_ADMIN_CREDS)
    yield manager
    session.close()


@pytest.fixture
def movie_data():
    """Генерация случайных данных для фильма."""
    return DataGenerator.generate_movie_data()


@pytest.fixture
def created_movie(super_admin_api, movie_data):
    """Создает фильм перед тестом и удаляет после завершения."""
    response = super_admin_api.movies_api.create_movie(movie_data, expected_status=201)
    movie = response.json()
    yield movie
    try:
        super_admin_api.movies_api.delete_movie(movie["id"], expected_status=200)
    except ValueError:
        pass

@pytest.fixture
def user_api(api_manager, registered_user):
    api_manager.auth_api.authenticate(registered_user) # или другой метод, обновляющий заголовки
    return api_manager
