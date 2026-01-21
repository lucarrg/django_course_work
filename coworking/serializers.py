from rest_framework import serializers
from .models import Coworking, Workplace

class CoworkingSerializer(serializers.ModelSerializer):
    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название коворкинга не может быть пустым")
        return value

    class Meta:
        model = Coworking
        fields = '__all__'


class WorkplaceSerializer(serializers.ModelSerializer):
    # проверка на уровне api
    def validate_price_per_hour(self, value):
        if value <= 0:
            raise serializers.ValidationError("Цена за час должна быть больше 0")
        return value

    def validate(self, data):
        if data.get('price_per_hour') and data['price_per_hour'] > 10000:
            raise serializers.ValidationError(
                'Цена за час слишком высокая'
            )
        return data

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Название рабочего места не может быть пустым")
        return value

    class Meta:
        # Указывает, для какой модели строится сериализатор
        model = Workplace
        # Перечисляет поля, которые будут включены в сериализацию
        fields = '__all__'
