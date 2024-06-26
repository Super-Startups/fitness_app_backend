from django.contrib import admin

from core.models import Trainer


# Register your models here.

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    pass
