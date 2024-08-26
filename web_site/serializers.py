from rest_framework import serializers
from web_site.models import CallBackRequest


class CallBackRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallBackRequest
        fields = ['status', 'name', 'age', 'email', 'phone_num']

class CallBackRequestDisplaySerializer(serializers.ModelSerializer):
    class Meta:
        model = CallBackRequest
        fields = ['id', 'status', 'name', 'age', 'email', 'phone_num', 'note', 'date_create']