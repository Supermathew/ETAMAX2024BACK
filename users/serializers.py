from rest_framework import serializers
from rest_framework.settings import import_from_string

from transactions.serializers import TransactionSerializer

from .models import User, Participation, UserRequest
from events.serializers import EventSerializer2


class UserSerializer2(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = '__all__'

class ParticipationSerializer2(serializers.ModelSerializer):
  event = EventSerializer2(read_only=True)
  members = UserSerializer2(read_only=True, many=True)
  transaction = TransactionSerializer(read_only=True)
  class Meta:
    model = Participation
    fields = '__all__'

class ParticipationSerializer(serializers.ModelSerializer):
  event = EventSerializer2(read_only=True)
  transaction = TransactionSerializer(read_only=True)
  class Meta:
    model = Participation
    fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
  participations = ParticipationSerializer(many=True, read_only=True)
  class Meta:
    model = User
    fields = '__all__'
    extra_kwargs = {
      'password': {'write_only': True},
    }

  def create(self, validated_data):
    password = validated_data.pop('password', None)
    instance = self.Meta.model(**validated_data)
    if password is not None:
      instance.set_password(password)
    instance.save()
    return instance

class UserRequestSerializer(serializers.ModelSerializer):
  class Meta:
    model = UserRequest
    fields = '__all__'
