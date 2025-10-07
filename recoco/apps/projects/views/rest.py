# encoding: utf-8

"""
Views for projects application

author  : raphael.marvie@beta.gouv.fr,guillaume.libersat@beta.gouv.fr
created : 2021-05-26 15:56:20 CEST
"""

from __future__ import annotations

from copy import copy

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Count, F, OuterRef, Q, QuerySet, Subquery
from django.http import Http404
from django.shortcuts import get_object_or_404
from notifications import models as notifications_models
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from recoco import verbs
from recoco.rest_api.filters import (
    TagsFilterbackend,
    VectorSearchFilter,
    WatsonSearchFilter,
)
from recoco.rest_api.pagination import LargeResultsSetPagination
from recoco.utils import (
    get_group_for_site,
    has_perm,
    has_perm_or_403,
)

from .. import models, signals
from ..filters import DepartmentsFilter, ProjectActivityFilter
from ..models import Project
from ..serializers import (
    DocumentSerializer,
    NewDocumentSerializer,
    ProjectForListSerializer,
    ProjectSiteSerializer,
    TopicSerializer,
    UserProjectSerializer,
    UserProjectStatusForListSerializer,
    UserProjectStatusSerializer,
)

########################################################################
# Project API
########################################################################


class ProjectDetail(APIView):
    """Retrieve a project"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return models.Project.on_site.with_site_status().get(pk=pk)
        except models.Project.DoesNotExist as exc:
            raise Http404 from exc

    def get(self, request, pk, format=None):
        p = self.get_object(pk)
        has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
            request.user, "view_project", p
        )
        context = {"request": request}
        serializer = UserProjectSerializer(p, context=context)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        p = self.get_object(pk)
        has_perm(request.user, "list_projects", request.site) or has_perm_or_403(
            request.user, "projects.change_location", p
        )  # need at least one write perm
        context = {"request": request, "view": self, "format": format}
        serializer = UserProjectSerializer(
            p, context=context, data=request.data, partial=True
        )
        if serializer.is_valid():
            # old = copy(p)
            serializer.save()
            # if new:
            #     signals.project_project_updated.send(
            #         sender=self, old_one=old, new_one=new
            #     )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectList(ListAPIView):
    """List all user projects"""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectForListSerializer
    filter_backends = [
        TagsFilterbackend,
        WatsonSearchFilter,
        DepartmentsFilter,
        ProjectActivityFilter,
    ]

    def get_queryset(self):
        return (
            models.Project.on_site.for_user(self.request.user)
            .order_by("-created_on", "-updated_on")
            .annotate(
                project_site_status=Subquery(
                    models.ProjectSite.objects.filter(
                        project_id=OuterRef("pk"), site=self.request.site
                    ).values("status")
                )
            )
            .prefetch_related(
                "commune__department",
                "switchtenders__profile__organization",
                "project_sites",
                "tags",
            )
        )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        projects = self._update_the_site_projects(
            queryset=queryset, site=request.site, user=request.user
        )

        serializer = self.get_serializer(projects, many=True)
        return Response(serializer.data)

    def _update_the_site_projects(
        self, queryset: QuerySet[models.Project], site: Site, user: User
    ) -> list[models.Project]:
        """Returns the complete project list of site for advisor user

        Here we face a n+1 fetching problem that happens at multiple levels
        implying an explosition of requests
        The intent is to fetch each kind of objects in one request and then to
        reattach the information to the appropriate object.
        """
        projects = list(queryset)

        ids = [p.id for p in projects]

        # fetch all related site project switchtender to annotate furthemore the project
        switchtendering = {
            ps["project_id"]: ps["is_observer"]
            for ps in models.ProjectSwitchtender.objects.filter(
                site=site, switchtender=user, project_id__in=ids
            ).values("project_id", "is_observer")
        }

        # update project statuses with the right project and switchtendering statuses
        for p in projects:
            p.is_switchtender = p.id in switchtendering
            p.is_observer = switchtendering.get(p.id, False)

        # associate related notification to their projects
        self._update_projects_with_their_notifications(site, user, projects)

        return projects

    def _update_projects_with_their_notifications(self, site, user, projects):
        """Fetch all the related notifications and associate them w/ their projects"""

        project_ct = ContentType.objects.get_for_model(models.Project)

        advisor_group = get_group_for_site("advisor", site)
        advisors = [
            int(advisor)
            for advisor in advisor_group.user_set.values_list("id", flat=True)
        ]

        unread_notifications = (
            notifications_models.Notification.on_site.filter(recipient=user)
            .filter(target_content_type=project_ct.pk)
            .unread()
            .order_by("target_object_id")
        )

        # fetch the related notifications
        all_unread_notifications = (
            unread_notifications.values(project_id=F("target_object_id"))
            .annotate(count=Count("id", distinct=True))
            .annotate(
                unread_public_messages=Count(
                    "id", filter=Q(verb=verbs.Conversation.PUBLIC_MESSAGE)
                )
            )
            .annotate(
                unread_private_messages=Count(
                    "id", filter=Q(verb=verbs.Conversation.PRIVATE_MESSAGE)
                )
            )
            .annotate(
                new_recommendations=Count(
                    "id", filter=Q(verb=verbs.Recommendation.CREATED)
                )
            )
        )
        notifications = {n["project_id"]: n for n in all_unread_notifications}

        # Specific request for collaborator activity as it relies on exclusion
        collaborator_activity = (
            unread_notifications.exclude(actor_object_id__in=advisors)
            .values(project_id=F("target_object_id"))
            .annotate(activity=Count("id", disctint=True))
        )
        collaborators = {n["project_id"]: n["activity"] for n in collaborator_activity}

        # the empty dict is going to be used read only, so sharing same object
        empty = {
            "count": 0,
            "has_collaborator_activity": False,
            "unread_public_messages": 0,
            "unread_private_messages": 0,
            "new_recommendations": 0,
        }

        # for each project associate the corresponding notifications
        for p in projects:
            p.notifications = notifications.get(str(p.id), empty)
            active = bool(collaborators.get(str(p.id)))
            p.notifications["has_collaborator_activity"] = active


########################################################################
# user project statuses
########################################################################


class UserProjectStatusDetail(APIView):
    """Retrieve or update a user project status"""

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return models.UserProjectStatus.objects.get(pk=pk)
        except models.UserProjectStatus.DoesNotExist as exc:
            raise Http404 from exc

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
    The intent is to fetch each kind of objects in on request and then to
    reattache the information to the appropriate object.
    """
    project_statuses = models.UserProjectStatus.objects.filter(
        user=user, project__deleted=None, project__sites=site
    ).exclude(project__project_sites__status__in=["DRAFT", "REJECTED"])

    # create missing user project status
    create_missing_user_project_statuses(site, user, project_statuses)

    # fetch all projects statuses for user
    project_statuses = list(project_statuses.prefetch_related("user__profile"))

    # associate related project information with each user project status
    update_user_project_status_with_their_project(site, user, project_statuses)

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
    models.UserProjectStatus.objects.bulk_create(
        new_statuses, ignore_conflicts=True
    )  # XXX Might be a better way


def update_user_project_status_with_their_project(site, user, project_statuses):
    """Fetch all related projects and associate them with their project status"""

    # fetch all requested projects and their annotations in a single query
    ids = [ps.project_id for ps in project_statuses]
    projects = {p.id: p for p in fetch_site_projects_with_ids(site, ids)}

    # fetch all related site project switchtender to annotate furthemore the project
    switchtendering = {
        ps["project_id"]: ps["is_observer"]
        for ps in models.ProjectSwitchtender.objects.filter(
            site=site, switchtender=user, project_id__in=ids
        ).values("project_id", "is_observer")
    }

    # update project statuses with the right project and switchtendering statuses
    for ps in project_statuses:
        ps.project = projects[ps.project_id]
        ps.is_switchtender = ps.project_id in switchtendering
        ps.is_observer = switchtendering.get(ps.project_id, False)


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
        .annotate(count=Count("id", distinct=True))
        .annotate(
            unread_public_messages=Count(
                "id", filter=Q(verb=verbs.Conversation.PUBLIC_MESSAGE)
            )
        )
        .annotate(
            unread_private_messages=Count(
                "id", filter=Q(verb=verbs.Conversation.PRIVATE_MESSAGE)
            )
        )
        .annotate(
            new_recommendations=Count("id", filter=Q(verb=verbs.Recommendation.CREATED))
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
        "has_collaborator_activity": False,
        "unread_public_messages": 0,
        "unread_private_messages": 0,
        "new_recommendations": 0,
    }

    # for each project associate the corresponding notifications
    for ps in project_statuses:
        ps.project.notifications = notifications.get(str(ps.project_id), empty)
        active = bool(collaborators.get(str(ps.project_id)))
        ps.project.notifications["has_collaborator_activity"] = active


def fetch_site_projects_with_ids(site, ids):
    """Return site projects with given ids including annotations."""
    return (
        models.Project.objects.filter(id__in=ids)
        .prefetch_related("commune__department")
        .prefetch_related("switchtenders__profile")
        .prefetch_related("project_sites")
        .prefetch_related("switchtenders__profile__organization")
        .annotate(
            recommendation_count=Count(
                "tasks",
                filter=Q(tasks__public=True, tasks__site=site),
                distinct=True,
            )
        )
        .annotate(
            public_message_count=Count(
                "notes",
                filter=Q(notes__public=True, notes__site=site),
                distinct=True,
            )
        )
        .annotate(
            private_message_count=Count(
                "notes",
                filter=Q(notes__public=False, notes__site=site),
                distinct=True,
            )
        )
    )


########################################################################
# Topic API
########################################################################


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint that allows searching for topics"""

    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LargeResultsSetPagination
    search_fields = ["name"]
    filter_backends = [VectorSearchFilter]
    search_min_rank = 0.05

    def get_queryset(self):
        """Return a list of all topics."""
        restrict_to = self.request.query_params.get("restrict_to", None)
        topics = models.Topic.objects.none()
        if restrict_to:
            # Warning : make sure the models mapping here have a "deleted" field or change the code below ;)
            # If not, a django.core.exceptions.FieldError will be throw.
            models_mapping = {
                "projects": "projects",
                "recommendations": "tasks",
            }
            try:
                topics = (
                    models.Topic.objects.filter(
                        **{f"{models_mapping[restrict_to]}__deleted": None}
                    )
                    .annotate(ntag=Count(models_mapping[restrict_to]))
                    .exclude(ntag=0)
                )
            except KeyError:
                pass

        return topics


########################################################################
# Project Site API (status on given site)
########################################################################

# /project/:X/moderate (POST)
# /projects/status (GET => list)
# /projects/status/:X (PATCH => "status")


class ProjectSiteViewSet(viewsets.GenericViewSet):
    """
    API endpoint for listing project state relative to a site
    """

    serializer_class = ProjectSiteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = models.ProjectSite.objects.filter(site=self.request.site)

        if not has_perm(self.request.user, "moderate_projects", self.request.site):
            qs = qs.exclude(status__in=["DRAFT", "PROPOSED"])

        return qs

    def list(self, request):
        has_perm_or_403(self.request.user, "list_projects", self.request.site)

        serializer = self.get_serializer_class()
        data = serializer(self.get_queryset(), many=True).data

        return Response(data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        has_perm_or_403(self.request.user, "list_projects", self.request.site)

        project_site = get_object_or_404(
            self.get_queryset(),
            pk=pk,
        )

        serializer = ProjectSiteSerializer(
            project_site, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)


########################################################################
# Document API
########################################################################


class DocumentViewSet(
    mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """API endpoint that allows searching for topics"""

    permission_classes = [permissions.IsAuthenticated]
    queryset = models.Document.objects
    parsers = (
        JSONParser,
        MultiPartParser,
        FormParser,
    )

    def get_queryset(self):
        project_id = int(self.kwargs["project_id"])
        return self.queryset.filter(project_id=project_id)

    def get_serializer_class(self):
        if self.action == "create":
            return NewDocumentSerializer
        return DocumentSerializer

    def perform_create(self, serializer):
        instance = serializer.save(
            project_id=int(self.kwargs["project_id"]),
            uploaded_by=self.request.user,
            site=get_current_site(self.request),
        )
        signals.document_uploaded.send(sender=self.create, instance=instance)


# eof
class DocumentPermission(BasePermission):
    def has_permission(self, request, view):
        project = Project.objects.get(pk=view.kwargs["project_id"])
        # perms from recoco.app.projects.views.documents
        return has_perm(request.user, "manage_documents", project)
