"""
Tests for Pydantic models - no external dependencies needed
"""
import pytest
from datetime import datetime
from api.models.plant import Plant, PlantSize, PlantType, ToxicityLevel, PlantAnalysis, CareSchedule, HealthCheckItem
from api.models.chat import ChatMessage, ChatResponse, ImageAnalysis
from api.models.task import CareTask


class TestEnums:
    def test_plant_size_values(self):
        assert PlantSize.SMALL.value == "small"
        assert PlantSize.MEDIUM.value == "medium"
        assert PlantSize.LARGE.value == "large"

    def test_plant_type_values(self):
        assert PlantType.INDOOR.value == "indoor"
        assert PlantType.OUTDOOR.value == "outdoor"
        assert PlantType.BOTH.value == "both"

    def test_toxicity_level_values(self):
        assert ToxicityLevel.NON_TOXIC.value == "non-toxic"
        assert ToxicityLevel.MILDLY_TOXIC.value == "mildly-toxic"
        assert ToxicityLevel.TOXIC.value == "toxic"
        assert ToxicityLevel.HIGHLY_TOXIC.value == "highly-toxic"


class TestPlantModel:
    def test_minimal_plant(self):
        plant = Plant(name="Fern", species="Nephrolepis exaltata")
        assert plant.name == "Fern"
        assert plant.species == "Nephrolepis exaltata"
        assert plant.plant_type == PlantType.INDOOR
        assert plant.size == PlantSize.MEDIUM
        assert plant.toxicity == ToxicityLevel.NON_TOXIC
        assert plant.location == "Living Room"
        assert plant.watering_frequency_days == 7
        assert plant.health_score == 100.0
        assert plant.needs_watering is False

    def test_plant_with_all_fields(self):
        now = datetime.now()
        plant = Plant(
            id="plant-1",
            name="Monstera",
            species="Monstera deliciosa",
            scientific_name="Monstera deliciosa",
            plant_type=PlantType.INDOOR,
            size=PlantSize.LARGE,
            toxicity=ToxicityLevel.MILDLY_TOXIC,
            location="Corner of living room",
            watering_frequency_days=10,
            health_score=95.5,
            created_at=now,
            updated_at=now,
        )
        assert plant.id == "plant-1"
        assert plant.scientific_name == "Monstera deliciosa"
        assert plant.watering_frequency_days == 10
        assert plant.health_score == 95.5
        assert plant.created_at == now
        assert plant.updated_at == now

    def test_plant_type_assignment(self):
        plant = Plant(name="Rose", species="Rosa", plant_type=PlantType.OUTDOOR)
        assert plant.plant_type == PlantType.OUTDOOR
        assert plant.plant_type.value == "outdoor"

    def test_plant_size_assignment(self):
        plant = Plant(name="Bonsai", species="Pinus", size=PlantSize.SMALL)
        assert plant.size == PlantSize.SMALL

    def test_plant_toxicity_assignment(self):
        plant = Plant(name="Oleander", species="Nerium oleander", toxicity=ToxicityLevel.HIGHLY_TOXIC)
        assert plant.toxicity == ToxicityLevel.HIGHLY_TOXIC

    def test_plant_preferred_locations_default(self):
        plant = Plant(name="Test", species="Test")
        assert plant.preferred_locations == []

    def test_plant_fun_facts_default(self):
        plant = Plant(name="Test", species="Test")
        assert plant.fun_facts == []

    def test_plant_temperature_range_default(self):
        plant = Plant(name="Test", species="Test")
        assert plant.temperature_range == {"min": 18, "max": 24}

    def test_plant_care_instructions_default(self):
        plant = Plant(name="Test", species="Test")
        assert plant.care_instructions == ""

    def test_plant_autonomous_tracking_defaults(self):
        plant = Plant(name="Test", species="Test")
        assert plant.days_since_watering == 0
        assert plant.days_since_fertilizing == 0
        assert plant.needs_watering is False
        assert plant.needs_fertilizing is False

    def test_plant_image_url_optional(self):
        plant = Plant(name="Test", species="Test", image_url="http://example.com/plant.jpg")
        assert plant.image_url == "http://example.com/plant.jpg"

    def test_plant_image_url_none_by_default(self):
        plant = Plant(name="Test", species="Test")
        assert plant.image_url is None


class TestChatMessageModel:
    def test_chat_message_minimal(self):
        msg = ChatMessage(role="user", content="Hello")
        assert msg.role == "user"
        assert msg.content == "Hello"
        assert msg.image_url is None
        assert isinstance(msg.timestamp, datetime)

    def test_chat_message_assistant(self):
        msg = ChatMessage(role="assistant", content="Plant care tip")
        assert msg.role == "assistant"

    def test_chat_message_with_image(self):
        msg = ChatMessage(role="user", content="What's wrong?", image_url="http://example.com/leaf.jpg")
        assert msg.image_url == "http://example.com/leaf.jpg"

    def test_chat_response_defaults(self):
        resp = ChatResponse(response="Hello!")
        assert resp.response == "Hello!"
        assert resp.suggestions == []
        assert isinstance(resp.timestamp, datetime)

    def test_chat_response_with_suggestions(self):
        resp = ChatResponse(response="Try watering", suggestions=["Water more", "Check soil"])
        assert len(resp.suggestions) == 2

    def test_image_analysis_defaults(self):
        analysis = ImageAnalysis(health_assessment="Healthy")
        assert analysis.health_assessment == "Healthy"
        assert analysis.issues_detected == []
        assert analysis.recommendations == []
        assert analysis.confidence == 0.0

    def test_image_analysis_with_values(self):
        analysis = ImageAnalysis(
            health_assessment="Unhealthy",
            issues_detected=["Yellow leaves"],
            recommendations=["Water less"],
            confidence=0.85
        )
        assert analysis.confidence == 0.85
        assert len(analysis.issues_detected) == 1


class TestCareTaskModel:
    def test_care_task_defaults(self):
        now = datetime.now()
        task = CareTask(plant_id="p1", task_type="watering", title="Water plant", scheduled_date=now)
        assert task.status == "pending"
        assert task.ai_generated is True
        assert task.priority == "medium"
        assert task.estimated_time == "5 minutes"
        assert task.description is None
        assert task.completed_date is None
        assert task.id is None

    def test_care_task_with_all_fields(self):
        now = datetime.now()
        completed = datetime.now()
        task = CareTask(
            id="task-1",
            plant_id="p1",
            task_type="fertilizing",
            title="Fertilize",
            description="Spring feeding",
            scheduled_date=now,
            completed_date=completed,
            status="completed",
            ai_generated=False,
            priority="high",
            estimated_time="10 minutes"
        )
        assert task.id == "task-1"
        assert task.status == "completed"
        assert task.ai_generated is False
        assert task.priority == "high"
        assert task.estimated_time == "10 minutes"
        assert task.description == "Spring feeding"
        assert task.completed_date == completed

    def test_care_task_status_values(self):
        now = datetime.now()
        for status in ("pending", "completed", "skipped"):
            task = CareTask(plant_id="p1", task_type="pruning", title="Prune", scheduled_date=now, status=status)
            assert task.status == status

    def test_care_task_priority_values(self):
        now = datetime.now()
        for priority in ("low", "medium", "high"):
            task = CareTask(plant_id="p1", task_type="checking", title="Check", scheduled_date=now, priority=priority)
            assert task.priority == priority


class TestHealthCheckItem:
    def test_health_check_item_requires_fields(self):
        item = HealthCheckItem(id="h1", plant_id="p1", check_type="leaves", status="good")
        assert item.check_type == "leaves"
        assert item.status == "good"
        assert item.notes is None
        assert item.symptoms == []

    def test_health_check_item_with_symptoms(self):
        item = HealthCheckItem(
            id="h1", plant_id="p1", check_type="pests", status="poor",
            symptoms=["Aphids", "Leaf curl"], notes="Needs neem oil"
        )
        assert len(item.symptoms) == 2
        assert item.notes == "Needs neem oil"


class TestPlantAnalysis:
    def test_plant_analysis_required_fields(self):
        analysis = PlantAnalysis(
            plant_id="p1",
            health_score=85.0,
            issues=["Yellowing"],
            recommendations=["Water less"],
            next_actions=["Check soil"]
        )
        assert analysis.health_score == 85.0
        assert len(analysis.issues) == 1
        assert analysis.care_adjustments == {}

    def test_plant_analysis_with_adjustments(self):
        analysis = PlantAnalysis(
            plant_id="p1",
            health_score=70.0,
            issues=["Drooping"],
            recommendations=["Water more"],
            next_actions=["Adjust schedule"],
            care_adjustments={"watering_frequency_days": 5}
        )
        assert analysis.care_adjustments["watering_frequency_days"] == 5


class TestCareSchedule:
    def test_care_schedule_defaults(self):
        now = datetime.now()
        sched = CareSchedule(plant_id="p1", schedule_type="watering", title="Water", description="Desc", scheduled_date=now)
        assert sched.priority == "medium"
        assert sched.estimated_time == "5 minutes"
        assert sched.completed is False
        assert sched.completed_at is None
        assert sched.notes is None
