#!/usr/bin/env python

from rest_framework import viewsets

from .models import Message
from .serializers import MessageSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        return self.queryset.filter(project_id=project_id)
