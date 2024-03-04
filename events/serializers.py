from rest_framework import serializers
from .models import Event

class EventSerializer(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = '__all__'


class EventSerializer2(serializers.ModelSerializer):
  class Meta:
    model = Event
    fields = '__all__'
