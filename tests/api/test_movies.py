import pytest
from utils.data_generator import DataGenerator


class TestMoviesAPI:

    # ==================== ПОЗИТИВНЫЕ ТЕСТЫ ====================

    def test_get_movies_list(self, api_manager):
        """Проверка получения списка фильмов без фильтров."""
        response = api_manager.movies_api.get_movies(expected_status=200)
        data = response.json()

        assert "movies" in data, "В ответе отсутствует ключ 'movies'"
        assert isinstance(data["movies"], list), "Поле 'movies' должно быть списком"

    @pytest.mark.parametrize("location", ["MSK", "SPB"])
    def test_get_movies_with_location_filter(self, api_manager, super_admin_api, location):
        """Проверка фильтрации фильмов по локации (GET /movies?locations=...)."""
        # Создаем фильм с нужной локацией, чтобы гарантировать наличие данных в выдаче
        payload = DataGenerator.generate_movie_data()
        payload["location"] = location
        created = super_admin_api.movies_api.create_movie(payload).json()

        try:
            response = api_manager.movies_api.get_movies(
                params={"locations": location, "pageSize": 10},
                expected_status=200
            )
            movies = response.json().get("movies", [])
            assert len(movies) > 0, f"Список фильмов для локации {location} пуст"
            for movie in movies:
                assert movie["location"] == location, (
                    f"Ожидалась локация {location}, получена {movie['location']}"
                )
        finally:
            super_admin_api.movies_api.delete_movie(created["id"])

    def test_create_movie(self, super_admin_api, movie_data):
        """Проверка успешного создания фильма под ролью администратора."""
        response = super_admin_api.movies_api.create_movie(movie_data, expected_status=201)
        created = response.json()

        try:
            assert created["name"] == movie_data["name"]
            assert created["price"] == movie_data["price"]
            assert created["location"] == movie_data["location"]
            assert "id" in created
        finally:
            super_admin_api.movies_api.delete_movie(created["id"])

    def test_get_movie_by_id(self, api_manager, created_movie):
        """Проверка получения фильма по его ID."""
        movie_id = created_movie["id"]
        response = api_manager.movies_api.get_movie_by_id(movie_id, expected_status=200)
        fetched = response.json()

        assert fetched["id"] == movie_id
        assert fetched["name"] == created_movie["name"]

    def test_update_movie(self, super_admin_api, created_movie):
        """Проверка частичного обновления фильма (PATCH /movies/{id})."""
        movie_id = created_movie["id"]
        update_payload = {
            "name": f"Updated {created_movie['name']}",
            "price": created_movie["price"] + 100
        }

        response = super_admin_api.movies_api.update_movie(
            movie_id, update_payload, expected_status=200
        )
        updated = response.json()

        assert updated["name"] == update_payload["name"]
        assert updated["price"] == update_payload["price"]

    def test_delete_movie(self, super_admin_api, created_movie):
        """Проверка удаления фильма и недоступности его после удаления."""
        movie_id = created_movie["id"]

        super_admin_api.movies_api.delete_movie(movie_id, expected_status=200)
        # Убеждаемся, что фильм действительно удален
        super_admin_api.movies_api.get_movie_by_id(movie_id, expected_status=404)

    # ==================== НЕГАТИВНЫЕ ТЕСТЫ ====================

    def test_create_movie_unauthorized(self, api_manager, movie_data):
        """Неавторизованный пользователь не может создать фильм (401)."""
        api_manager.movies_api.create_movie(movie_data, expected_status=401)

    def test_create_movie_by_regular_user(self, user_api, movie_data):
        """Обычный пользователь без прав ADMIN не может создать фильм (403)."""
        user_api.movies_api.create_movie(movie_data, expected_status=403)

    def test_create_movie_with_invalid_data(self, super_admin_api, movie_data):
        """Создание фильма с некорректным типом данных (отрицательная цена -> 400)."""
        invalid_data = movie_data.copy()
        invalid_data["price"] = -500

        super_admin_api.movies_api.create_movie(invalid_data, expected_status=400)

    def test_get_nonexistent_movie(self, api_manager):
        """Запрос фильма по несуществующему ID возвращает 404."""
        nonexistent_id = 999999999
        api_manager.movies_api.get_movie_by_id(nonexistent_id, expected_status=404)

    def test_delete_movie_unauthorized(self, api_manager, created_movie):
        """Неавторизованный пользователь не может удалить фильм (401)."""
        api_manager.movies_api.session.headers.pop("Authorization", None)
        api_manager.movies_api.delete_movie(created_movie["id"], expected_status=401)
