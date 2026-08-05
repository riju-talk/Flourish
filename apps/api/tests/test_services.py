"""
Tests for service layer - mocks external dependencies (httpx, groq, firebase)
"""
import httpx
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from api.models.plant import Plant, PlantSize, PlantType, ToxicityLevel
from api.models.task import CareTask
from api.services.weather_service import WeatherService
from api.services.plant_service import PlantService


class TestWeatherService:
    def test_generate_recommendations_hot_temperature(self):
        recs = WeatherService._generate_plant_recommendations(35.0, 50.0, "Clear")
        assert "High temperature: Increase watering frequency" in recs
        assert "Provide shade during peak heat hours" in recs

    def test_generate_recommendations_cold_temperature(self):
        recs = WeatherService._generate_plant_recommendations(5.0, 50.0, "Cloudy")
        assert "Low temperature: Reduce watering and protect from frost" in recs

    def test_generate_recommendations_optimal_temperature(self):
        recs = WeatherService._generate_plant_recommendations(20.0, 50.0, "Cloudy")
        assert "Optimal temperature range for most plants" in recs

    def test_generate_recommendations_low_humidity(self):
        recs = WeatherService._generate_plant_recommendations(22.0, 30.0, "Clear")
        assert "Low humidity: Consider misting plants regularly" in recs

    def test_generate_recommendations_high_humidity(self):
        recs = WeatherService._generate_plant_recommendations(22.0, 85.0, "Cloudy")
        assert "High humidity: Ensure good air circulation to prevent mold" in recs

    def test_generate_recommendations_rain_condition(self):
        recs = WeatherService._generate_plant_recommendations(18.0, 70.0, "Rain")
        assert "Rain expected: Reduce manual watering" in recs

    def test_generate_recommendations_sunny_condition(self):
        recs = WeatherService._generate_plant_recommendations(25.0, 50.0, "Sunny")
        assert "Sunny conditions: Monitor soil moisture closely" in recs

    def test_generate_recommendations_clear_condition(self):
        recs = WeatherService._generate_plant_recommendations(25.0, 50.0, "Clear")
        assert "Sunny conditions: Monitor soil moisture closely" in recs

    def test_generate_recommendations_normal_conditions(self):
        # 26°C skips all temperature triggers, 50% humidity is moderate, "Cloudy" doesn't match rain/clear/sunny
        recs = WeatherService._generate_plant_recommendations(26.0, 50.0, "Cloudy")
        assert "Weather conditions appear normal" in recs

    def test_generate_recommendations_multiple_triggers(self):
        """Hot + Low humidity + Sunny should produce multiple recommendations"""
        recs = WeatherService._generate_plant_recommendations(35.0, 30.0, "Sunny")
        assert len(recs) >= 4

    @pytest.mark.asyncio
    async def test_get_weather_no_api_key(self):
        """When API_KEY is empty, should return mock data"""
        with patch.object(WeatherService, 'API_KEY', ''):
            result = await WeatherService.get_weather_by_location(40.0, -74.0)
            assert result["temperature"] == 22.0
            assert result["humidity"] == 65.0
            assert "Moderate watering needed" in result["recommendations"]

    @pytest.mark.asyncio
    async def test_get_weather_httpx_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "main": {"temp": 28.0, "humidity": 55.0},
            "weather": [{"main": "Clear"}],
            "wind": {"speed": 3.5}
        }
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.get.return_value = mock_response

        with patch.object(WeatherService, 'API_KEY', 'test-key'), \
             patch("httpx.AsyncClient", return_value=mock_client):
            result = await WeatherService.get_weather_by_location(40.0, -74.0)
            assert result["temperature"] == 28.0
            assert result["humidity"] == 55.0
            assert result["condition"] == "Clear"
            assert result["wind_speed"] == 3.5

    @pytest.mark.asyncio
    async def test_get_weather_httpx_request_error(self):
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.get.side_effect = httpx.RequestError("Connection error")

        with patch.object(WeatherService, 'API_KEY', 'test-key'), \
             patch("httpx.AsyncClient", return_value=mock_client):
            result = await WeatherService.get_weather_by_location(40.0, -74.0)
            assert result["temperature"] == 20.0
            assert result["humidity"] == 60.0
            assert "Weather data unavailable" in result["recommendations"]


class TestPlantService:
    @staticmethod
    def _mock_create_task():
        """FirestoreDB.create_task echoes the task dict back with a fake id, like real Firestore writes."""
        async def _create(task_data):
            return {**task_data, "id": f"task-{len(task_data)}-{task_data['task_type']}-{task_data['due_date']}"}
        return _create

    @pytest.mark.asyncio
    async def test_projected_schedule_watering_only(self):
        plant = {"id": "plant-1", "name": "Test Plant", "watering_frequency_days": 7}

        with patch("api.services.plant_service.FirestoreDB.create_task", side_effect=self._mock_create_task()):
            tasks = await PlantService.create_projected_schedule("user-1", plant, types=["watering"])

        # ceil(30 / 7) = 5 occurrences, covering ~30 days ahead
        assert len(tasks) == 5
        assert all(t["task_type"] == "watering" for t in tasks)
        assert all(t["plant_id"] == "plant-1" for t in tasks)
        assert all(t["user_id"] == "user-1" for t in tasks)

    @pytest.mark.asyncio
    async def test_projected_schedule_includes_fertilizing(self):
        plant = {
            "id": "plant-2", "name": "Fern",
            "watering_frequency_days": 3, "fertilizer_frequency_days": 30
        }

        with patch("api.services.plant_service.FirestoreDB.create_task", side_effect=self._mock_create_task()):
            tasks = await PlantService.create_projected_schedule("user-1", plant)

        task_types = {t["task_type"] for t in tasks}
        assert "fertilizing" in task_types
        assert "watering" in task_types
        for task in tasks:
            assert task["plant_id"] == "plant-2"

    @pytest.mark.asyncio
    async def test_watering_task_first_priority_high(self):
        plant = {"id": "p1", "name": "Aloe", "watering_frequency_days": 7}

        with patch("api.services.plant_service.FirestoreDB.create_task", side_effect=self._mock_create_task()):
            tasks = await PlantService.create_projected_schedule("user-1", plant, types=["watering"])

        assert tasks[0]["priority"] == "high"
        assert all(t["priority"] == "medium" for t in tasks[1:])

    @pytest.mark.asyncio
    async def test_projected_schedule_occurrence_count_is_capped(self):
        # Daily watering (1-day interval) would naively be 30 occurrences - must be capped at 6.
        plant = {"id": "p1", "name": "Fern", "watering_frequency_days": 1}

        with patch("api.services.plant_service.FirestoreDB.create_task", side_effect=self._mock_create_task()):
            tasks = await PlantService.create_projected_schedule("user-1", plant, types=["watering"])

        assert len(tasks) == 6

    @pytest.mark.asyncio
    async def test_fetch_plant_image_success(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [{"urls": {"regular": "http://example.com/plant.jpg"}}]
        }

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            url = await PlantService.fetch_plant_image("Aloe", "Aloe vera")
            assert url == "http://example.com/plant.jpg"

    @pytest.mark.asyncio
    async def test_fetch_plant_image_fallback(self):
        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.get.side_effect = Exception("API error")

        with patch("httpx.AsyncClient", return_value=mock_client):
            url = await PlantService.fetch_plant_image("Aloe", "Aloe vera")
            assert "images.unsplash.com" in url

    @pytest.mark.asyncio
    async def test_fetch_plant_image_empty_results(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}

        mock_client = AsyncMock()
        mock_client.__aenter__.return_value.get.return_value = mock_response

        with patch("httpx.AsyncClient", return_value=mock_client):
            url = await PlantService.fetch_plant_image("Aloe", "Aloe vera")
            assert "images.unsplash.com" in url
