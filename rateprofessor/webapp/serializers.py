from rest_framework import serializers
from .models import Module, Professor, ModuleInstance, Rating

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'


class ProfessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professor
        fields = '__all__'


class ModuleInstanceSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)
    professors = ProfessorSerializer(many=True, read_only=True)
    
    class Meta:
        model = ModuleInstance
        fields = ['id', 'module', 'year', 'semester', 'professors']


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'
