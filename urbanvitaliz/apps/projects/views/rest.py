# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from copy import copy

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, F, Q
from django.http import Http404
from notifications import models as notifications_models
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from urbanvitaliz.utils import get_group_for_site

from .. import models, signals
from ..serializers import (
    ProjectSerializer,
    ProjectForListSerializer,
    TaskFollowupSerializer,
    TaskNotificationSerializer,
    TaskSerializer,
    UserProjectStatusForListSerializer,
    UserProjectStatusSerializer,
)

########################################################################
# REST API
########################################################################


class ProjectDetail(APIView):
    """Retrieve a project"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return models.Project.on_site.get(pk=pk)
        except models.Project.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        ups = self.get_object(pk)
        context = {"request": request}
        serializer = ProjectSerializer(ups, context=context)
        return Response(serializer.data)


class ProjectList(APIView):
    """List all user project status"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        projects = fetch_the_site_projects(request.site, request.user)
        context = {"request": request}

        serializer = ProjectForListSerializer(projects, context=context, many=True)
        return Response(serializer.data)


def fetch_the_site_projects(site, user):
    """Returns the complete project list of site for advisor user

    Here we face a n+1 fetching problem that happens at multiple levels
    implying an explosition of requests
    The intent is to fetch each kind of objects in on request and then to
    reattach the information to the appropriate object.
    """
    projects = (
        models.Project.on_site.for_user(user)
        .order_by("-created_on", "-updated_on")
        .prefetch_related("commune")
        .prefetch_related("commune__department")
        .prefetch_related("switchtender__profile__organization")
    )

    # asscoiated related notification to their projects
    update_projects_with_their_notifications(site, projects)

    return projects


def update_projects_with_their_notifications(site, projects):
    """Fetch all the related notifications and associate them w/ their projects"""

    project_ct = ContentType.objects.get_for_model(models.Project)

    advisor_group = get_group_for_site("advisor", site)
    advisors = [
        int(advisor) for advisor in advisor_group.user_set.values_list("id", flat=True)
    ]

    unread_notifications = (
        notifications_models.Notification.on_site.filter(
            target_content_type=project_ct.pk
        )
        .unread()
        .order_by("target_object_id")
    )

    # fetch the related notifications
    all_unread_notifications = (
        unread_notifications.values(project_id=F("target_object_id"))
        .annotate(count=Count("id"))
        .annotate(
            unread_public_messages=Count("id", filter=Q(verb="a envoyé un message"))
        )
        .annotate(
            unread_private_messages=Count(
                "id", filter=Q(verb="a envoyé un message dans l'espace conseillers")
            )
        )
        .annotate(
            new_recommendations=Count("id", filter=Q(verb="a recommandé l'action"))
        )
    )
    notifications = {n["project_id"]: n for n in all_unread_notifications}

    # Specific request for collaborator activity as it relies on exclusion
    collaborator_activity = (
        unread_notifications.exclude(actor_object_id__in=advisors)
        .values(project_id=F("target_object_id"))
        .annotate(activity=Count("id"))
    )
    collaborators = {n["project_id"]: n["activity"] for n in collaborator_activity}

    # the empty dict is going to be used read only, so sharing same object
    empty = {
        "count": 0,
        "has_collaborator_activity": 0,
        "unread_public_messages": 0,
        "unread_private_messages": 0,
        "new_recommendations": 0,
    }

    # for each project associate the corresponding notifications
    for p in projects:
        p.notifications = notifications.get(str(p.id), empty)
        active = collaborators.get(str(p.id), False)
        p.notifications["has_collaborator_activity"] = active


# class ProjectViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows projects to be viewed or edited.
#     """
#
#     def get_queryset(self):
#         # TODO tune query set to prevent loads of requests on subqueries
#         return self.queryset.for_user(self.request.user).order_by(
#             "-created_on", "-updated_on"
#         )
#
#     queryset = models.Project.on_site
#     serializer_class = ProjectSerializer
#     permission_classes = [permissions.IsAuthenticated]


class TaskFollowupViewSet(viewsets.ModelViewSet):
    """
    API endpoint for TaskFollowups
    """

    serializer_class = TaskFollowupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        task_id = int(self.kwargs["task_id"])

        user_projects = list(
            models.Project.on_site.for_user(self.request.user).values_list(flat=True)
        )

        if project_id not in user_projects:
            project = models.Project.objects.get(pk=project_id)
            if not (
                self.request.method == "GET"
                and self.request.user.has_perm("projects.use_tasks", project)
            ):
                raise PermissionDenied()

        return models.TaskFollowup.objects.filter(task_id=task_id)

    def create(self, request, project_id, task_id):
        data = request.data
        data["task_id"] = task_id
        data["who_id"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint for project tasks
    """

    def perform_update(self, serializer):
        original_object = self.get_object()
        updated_object = serializer.save()

        if original_object.public is False and updated_object.public is True:
            signals.action_created.send(
                sender=self,
                task=updated_object,
                project=updated_object.project,
                user=self.request.user,
            )

    @action(
        methods=["post"],
        detail=True,
    )
    def move(self, request, project_id, pk):
        task = self.get_object()

        if not self.request.user.has_perm("projects.use_tasks", task.project):
            raise PermissionDenied()

        above_id = request.POST.get("above", None)
        below_id = request.POST.get("below", None)

        if above_id:
            other_pk = above_id
        else:
            other_pk = below_id

        try:
            other_task = self.queryset.get(project_id=task.project_id, pk=other_pk)
        except models.Task.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if above_id:
            task.above(other_task)
            return Response({"status": "insert above done"})

        if below_id:
            task.below(other_task)
            return Response({"status": "insert below done"})

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])

        project = models.Project.on_site.get(pk=project_id)

        if not (
            self.request.user.has_perm("projects.view_tasks", project)
            or self.request.user.has_perm("sites.list_projects", self.request.site)
        ):
            raise PermissionDenied()

        return self.queryset.filter(project_id=project_id).order_by(
            "-created_on", "-updated_on"
        )

    queryset = models.Task.on_site
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]


class TaskNotificationViewSet(
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    API endpoint for Task
    """

    def get_queryset(self):
        task_id = int(self.kwargs["task_id"])
        task = models.Task.objects.get(pk=task_id)

        notifications = self.request.user.notifications.unread()

        task_ct = ContentType.objects.get_for_model(models.Task)
        followup_ct = ContentType.objects.get_for_model(models.TaskFollowup)

        task_actions = notifications.filter(
            action_object_content_type=task_ct.pk,
            action_object_object_id=task_id,
        )

        followup_ids = list(task.followups.all().values_list("id", flat=True))

        followup_actions = notifications.filter(
            action_object_content_type=followup_ct.pk,
            action_object_object_id__in=followup_ids,
        )

        return task_actions | followup_actions

    @action(
        methods=["post"],
        detail=False,
    )
    def mark_all_as_read(self, request, project_id, task_id):
        self.get_queryset().mark_all_as_read(request.user)
        return Response({}, status=status.HTTP_200_OK)

    serializer_class = TaskNotificationSerializer
    permission_classes = [permissions.IsAuthenticated]


########################################################################
# user project statuses
########################################################################


class UserProjectStatusDetail(APIView):
    """Retrieve or update a user project status"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return models.UserProjectStatus.objects.get(pk=pk)
        except models.UserProjectStatus.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        ups = self.get_object(pk)
        if ups.user != request.user:
            raise Http404
        context = {"request": request}
        serializer = UserProjectStatusSerializer(ups, context=context)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        ups = self.get_object(pk)
        if ups.user != request.user:
            raise Http404
        context = {"request": request, "view": self, "format": format}
        serializer = UserProjectStatusSerializer(
            ups, context=context, data=request.data
        )
        if serializer.is_valid():
            old = copy(ups)
            new = serializer.save()
            if new:
                signals.project_userprojectstatus_updated.send(
                    sender=self, old_one=old, new_one=new
                )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProjectStatusList(APIView):
    """List all user project status"""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        ups = fetch_the_site_project_statuses_for_user(request.site, request.user)
        context = {"request": request}

        serializer = UserProjectStatusForListSerializer(ups, context=context, many=True)
        return Response(serializer.data)


def fetch_the_site_project_statuses_for_user(site, user):
    """Returns the complete user project status list for user on site

    Here we face a n+1 fetching problem that happens at multiple levels
    implying an explosition of requests (order of 400+ request for 30+ projects)
    The intent is to fetch each kind of objecst in on request and then to
    reattache the information to the appropriate object.
    """
    project_statuses = models.UserProjectStatus.objects.filter(
        user=user, project__deleted=None
    )

    # create missing user project status
    create_missing_user_project_statuses(site, user, project_statuses)

    # fetch all projects statuses for user
    project_statuses = list(project_statuses.prefetch_related("user__profile"))

    # associate related project information with each user project status
    update_user_project_status_with_their_project(site, project_statuses)

    # asscoiated related notification to their projects
    update_project_statuses_with_their_notifications(site, user, project_statuses)

    return project_statuses


def create_missing_user_project_statuses(site, user, project_statuses):
    """Create user projects statuses for given projects"""

    # get projects with no user project status
    ids = list(project_statuses.values_list("project__id", flat=True))
    projects = models.Project.on_site.for_user(user).exclude(id__in=ids)

    # create the missing ones
    new_statuses = [
        models.UserProjectStatus(user=user, site=site, project=p, status="NEW")
        for p in projects
    ]
    models.UserProjectStatus.objects.bulk_create(new_statuses)


def update_user_project_status_with_their_project(site, project_statuses):
    """Fetch all related projects and associate them with their project status"""

    # fetch all requested projects and their annotations in a single query
    ids = [ps.project_id for ps in project_statuses]
    projects = {p.id: p for p in fetch_site_projects_with_ids(site, ids)}

    # update project statuses with the right project
    for ps in project_statuses:
        ps.project = projects[ps.project_id]


def update_project_statuses_with_their_notifications(site, user, project_statuses):
    """Fetch all the related notifications and associate them w/ their projects"""

    # projects of interest
    project_ids = [s.project_id for s in project_statuses]

    notifications = notifications_models.Notification.on_site.filter(recipient=user)

    project_ct = ContentType.objects.get_for_model(models.Project)

    advisor_group = get_group_for_site("advisor", site)
    advisors = [
        int(advisor) for advisor in advisor_group.user_set.values_list("id", flat=True)
    ]

    unread_notifications = (
        notifications.filter(
            target_content_type=project_ct.pk, target_object_id__in=project_ids
        )
        .unread()
        .order_by("target_object_id")
    )

    # fetch the related notifications
    all_unread_notifications = (
        unread_notifications.values(project_id=F("target_object_id"))
        .annotate(count=Count("id"))
        .annotate(
            unread_public_messages=Count("id", filter=Q(verb="a envoyé un message"))
        )
        .annotate(
            unread_private_messages=Count(
                "id", filter=Q(verb="a envoyé un message dans l'espace conseillers")
            )
        )
        .annotate(
            new_recommendations=Count("id", filter=Q(verb="a recommandé l'action"))
        )
    )
    notifications = {n["project_id"]: n for n in all_unread_notifications}

    # Specific request for collaborator activity as it relies on exclusion
    collaborator_activity = (
        unread_notifications.exclude(actor_object_id__in=advisors)
        .values(project_id=F("target_object_id"))
        .annotate(activity=Count("id"))
    )
    collaborators = {n["project_id"]: n["activity"] for n in collaborator_activity}

    # the empty dict is going to be used read only, so sharing same object
    empty = {
        "count": 0,
        "has_collaborator_activity": 0,
        "unread_public_messages": 0,
        "unread_private_messages": 0,
        "new_recommendations": 0,
    }

    # for each project associate the corresponding notifications
    for ps in project_statuses:
        ps.project.notifications = notifications.get(str(ps.project_id), empty)
        active = collaborators.get(str(ps.project_id), False)
        ps.project.notifications["has_collaborator_activity"] = active


#     return {
#         "count": unread_notifications.count(),
#         "has_collaborator_activity": unread_notifications.exclude(
#             actor_object_id__in=advisors
#         ).exists(),
#         "unread_public_messages": unread_public_messages.count(),
#         "unread_private_messages": unread_private_messages.count(),
#         "new_recommendations": new_recommendations.count(),
#     }


def fetch_site_projects_with_ids(site, ids):
    """Return site projects with given ids including annotations."""
    return (
        models.Project.objects.filter(id__in=ids)
        .prefetch_related("commune__department")
        .prefetch_related("switchtenders__profile")
        .prefetch_related("switchtenders__profile__organization")
        .annotate(
            recommendation_count=Count(
                "tasks",
                filter=Q(tasks__public=True, tasks__site=site),
            )
        )
        .annotate(
            public_message_count=Count(
                "notes",
                filter=Q(notes__public=True, notes__site=site),
            )
        )
        .annotate(
            private_message_count=Count(
                "notes",
                filter=Q(notes__public=False, notes__site=site),
            )
        )
    )


# eof
