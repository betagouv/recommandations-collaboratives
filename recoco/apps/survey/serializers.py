from rest_framework import serializers

from recoco.apps.home.serializers import UserSerializer

from .models import Answer, Choice, Question, Session


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = [
            "id",
            "value",
            "text",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "text_short",
            "slug",
            "is_multiple",
            "choices",
        ]


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer()
    updated_by = UserSerializer()
    choices = ChoiceSerializer(many=True)
    project = serializers.SerializerMethodField()

    def get_project(self, obj: Answer):
        return obj.session.project.id

    class Meta:
        model = Answer
        fields = [
            "id",
            "created_on",
            "updated_on",
            "question",
            "session",
            "project",
            "choices",
            "values",
            "comment",
            "signals",
            "updated_by",
            "attachment",
        ]


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "survey",
            "project",
        ]
