#!/usr/bin/env python

from rest_framework import mixins, viewsets

from recoco import verbs
from recoco.apps.projects import models as projects_models

from .models import Message
from .serializers import ActivitySerializer, MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects
    serializer_class = MessageSerializer

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        return self.queryset.filter(project_id=project_id)


class ActivityViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Message.objects
    serializer_class = ActivitySerializer

    activity_verbs = [verbs.Project.BECAME_OBSERVER, verbs.Project.BECAME_ADVISOR]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        project = projects_models.Project.objects.get(id=project_id)

        return project.target_actions.filter(verb__in=self.activity_verbs, public=True)
