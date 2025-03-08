from django.contrib import admin
from .models import Module, Professor, ModuleInstance, Rating

# Register your models here.
admin.site.register(Module)
admin.site.register(Professor)
admin.site.register(ModuleInstance)
admin.site.register(Rating)
