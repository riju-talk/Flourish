from django.contrib import admin
from .models import Profile, Plant, CareTask, PlantCareLog

admin.site.register(Profile)
admin.site.register(Plant)
admin.site.register(CareTask)
admin.site.register(PlantCareLog)