from rest_framework import serializers
from SmartSaha.models import Task, TaskPriority, TaskStatus


class TaskPrioritySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskPriority
        fields = '__all__'


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['completed_at', 'history']

    def create(self, validated_data):
        task = Task.objects.create( **validated_data)
        task.add_history("Created")
        return task

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.add_history("Updated")
        instance.save()
        return instance