from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.email

class Plant(models.Model):
    # Plant Types
    PLANT_TYPES = [
        ('succulent', 'Succulent'),
        ('fern', 'Fern'),
        ('flowering', 'Flowering Plant'),
        ('herb', 'Herb'),
        ('vegetable', 'Vegetable'),
        ('tree', 'Tree'),
        ('shrub', 'Shrub'),
        ('other', 'Other'),
    ]
    
    # Sunlight Requirements
    SUNLIGHT_CHOICES = [
        ('low', 'Low Light'),
        ('medium', 'Medium Light'),
        ('bright', 'Bright Light'),
        ('direct', 'Direct Sunlight'),
    ]
    
    # Health Status
    HEALTH_STATUS = [
        ('healthy', 'Healthy'),
        ('needs_attention', 'Needs Attention'),
        ('struggling', 'Struggling'),
        ('disease_suspected', 'Disease Suspected'),
    ]
    
    # Watering Frequency (in days)
    WATERING_FREQUENCY = [
        (1, 'Daily'),
        (2, 'Every 2 days'),
        (3, 'Every 3 days'),
        (7, 'Weekly'),
        (14, 'Bi-weekly'),
        (30, 'Monthly'),
    ]
    
    # Fertilizing Frequency (in days)
    FERTILIZING_FREQUENCY = [
        (7, 'Weekly'),
        (14, 'Bi-weekly'),
        (30, 'Monthly'),
        (60, 'Every 2 months'),
        (90, 'Quarterly'),
        (180, 'Twice a year'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="Common name of the plant")
    scientific_name = models.CharField(max_length=255, blank=True, null=True, help_text="Scientific name of the plant")
    plant_type = models.CharField(max_length=20, choices=PLANT_TYPES, default='other', help_text="Type of plant")
    
    # Care requirements
    sunlight_requirement = models.CharField(max_length=20, choices=SUNLIGHT_CHOICES, default='medium', help_text="Amount of sunlight needed")
    watering_frequency = models.IntegerField(choices=WATERING_FREQUENCY, default=7, help_text="How often to water (in days)")
    fertilizing_frequency = models.IntegerField(choices=FERTILIZING_FREQUENCY, default=30, help_text="How often to fertilize (in days)")
    
    # Location and environment
    location = models.CharField(max_length=255, help_text="Where the plant is located")
    room = models.CharField(max_length=100, blank=True, null=True, help_text="Specific room or area")
    
    # Health and status
    health_status = models.CharField(max_length=20, choices=HEALTH_STATUS, default='healthy', help_text="Current health status")
    last_watered = models.DateTimeField(null=True, blank=True, help_text="When the plant was last watered")
    last_fertilized = models.DateTimeField(null=True, blank=True, help_text="When the plant was last fertilized")
    next_watering = models.DateTimeField(null=True, blank=True, help_text="When to water next")
    
    # Media and notes
    image_url = models.URLField(max_length=500, blank=True, null=True, help_text="URL of the plant's image")
    notes = models.TextField(blank=True, null=True, help_text="Additional notes about the plant")
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Plant'
        verbose_name_plural = 'Plants'
    
    def __str__(self):
        return f"{self.name} ({self.get_plant_type_display()})"
    
    def save(self, *args, **kwargs):
        # Update next_watering when last_watered changes
        if self.last_watered and self.watering_frequency:
            from django.utils import timezone
            self.next_watering = self.last_watered + timezone.timedelta(days=self.watering_frequency)
        super().save(*args, **kwargs)

class CareTask(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=50)
    title = models.TextField()
    description = models.TextField()
    scheduled_date = models.DateField()
    completed_date = models.DateTimeField(null=True, blank=True)
    status = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PlantCareLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    task = models.ForeignKey(CareTask, on_delete=models.CASCADE)
    task_type = models.TextField()
    notes = models.TextField()
    performed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

class AIChatSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AIChatMessage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AIChatSession, on_delete=models.CASCADE)
    role = models.TextField()
    content = models.TextField()
    image_url = models.TextField(null=True, blank=True)
    is_user = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
