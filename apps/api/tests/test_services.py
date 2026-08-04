"""
Tests for service layer - mocks external dependencies (httpx, ollama, firebase)
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
    def test_generate_care_schedule_default_plant(self):
        plant = Plant(
            id="plant-1",
            name="Test Plant",
            species="Test Species",
            watering_frequency_days=7
        )
        # Plant model doesn't have fertilizing_frequency_days, so patch it to 0 to skip fertilizing branch
        object.__setattr__(plant, 'fertilizing_frequency_days', 0)

        import asyncio
        tasks = asyncio.run(PlantService.generate_care_schedule(plant))

        # 14 watering tasks (every 7 days for 2 weeks * 7 days interval → 14 iterations)
        # 7 daily health check tasks
        # No fertilizing since fertilizing_frequency_days is 0
        assert len(tasks) == 14 + 7

        task_types = {t.task_type for t in tasks}
        assert "watering" in task_types
        assert "checking" in task_types
        assert "fertilizing" not in task_types

    def test_generate_care_schedule_with_fertilizing(self):
        plant = Plant(
            id="plant-2",
            name="Fern",
            species="Nephrolepis",
            watering_frequency_days=3
        )
        object.__setattr__(plant, 'fertilizing_frequency_days', 30)

        import asyncio
        tasks = asyncio.run(PlantService.generate_care_schedule(plant))

        task_types = {t.task_type for t in tasks}
        assert "fertilizing" in task_types
        assert "watering" in task_types
        assert "checking" in task_types

        # Verify all tasks reference the correct plant
        for task in tasks:
            assert task.plant_id == "plant-2"

    def test_watering_task_first_priority_high(self):
        plant = Plant(id="p1", name="Aloe", species="Aloe vera", watering_frequency_days=7)
        object.__setattr__(plant, 'fertilizing_frequency_days', 0)

        import asyncio
        tasks = asyncio.run(PlantService.generate_care_schedule(plant))

        watering_tasks = [t for t in tasks if t.task_type == "watering"]
        assert watering_tasks[0].priority == "high"
        assert all(t.priority == "medium" for t in watering_tasks[1:])

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

    def test_health_check_task_estimated_time(self):
        plant = Plant(id="p1", name="Cactus", species="Cactaceae")
        object.__setattr__(plant, 'fertilizing_frequency_days', 0)

        import asyncio
        tasks = asyncio.run(PlantService.generate_care_schedule(plant))

        checking_tasks = [t for t in tasks if t.task_type == "checking"]
        for task in checking_tasks:
            assert task.estimated_time == "2 minutes"
