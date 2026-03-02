from dataclasses import dataclass

from recoco import verbs


def normalize_user_name(user):
    """Return a user full name or standard greeting by default"""
    user_name = f"{user.first_name} {user.last_name}"
    if user_name.strip() == "":
        user_name = "Madame/Monsieur"
    return user_name


@dataclass
class FormattedNotification:
    summary: str
    excerpt: str | None = None


class NotificationFormatter:
    """Format notifications for email dispatch"""

    def __init__(self):
        self.dispatch_table = {
            verbs.Conversation.PRIVATE_MESSAGE: self.format_private_note_created,
            verbs.Project.BECAME_ADVISOR: self.format_action_became_advisor,
            verbs.Project.BECAME_OBSERVER: self.format_action_became_observer,
            verbs.Project.AVAILABLE: self.format_new_project_available,
            verbs.Project.SUBMITTED_BY: self.format_project_submitted,
            verbs.Project.SUBMITTED_BY_ADVISOR: self.format_project_submitted,
            verbs.Recommendation.COMMENTED: self.format_action_commented,
            verbs.Recommendation.CREATED: self.format_action_recommended,
            verbs.Document.ADDED_FILE: self.format_document_uploaded,
            verbs.Document.ADDED_LINK: self.format_document_uploaded,
        }

    def format(self, notification):
        """
        Try formatting the notification by the dispatch table or
        use the default reprensentation
        """

        def _default(notification):
            summary = "{n.actor} {n.verb} {n.action_object}".format(n=notification)
            return FormattedNotification(summary=summary)

        fmt = self.dispatch_table.get(notification.verb, _default)
        return fmt(notification)

    # ------ Formatter Utils -----#
    @staticmethod
    def _represent_user(user, is_short=False):
        if not user:
            fmt = "--compte indisponible--"
            return fmt

        if user.last_name:
            first_name = (
                f"{user.first_name[:1].capitalize()}." if is_short else user.first_name
            )
            fmt = f"{first_name} {user.last_name}"
        else:
            fmt = f"{user}"

        if user.profile.organization:
            fmt += f" ({user.profile.organization.name})"

        return fmt

    @staticmethod
    def _represent_recommendation(recommendation):
        if recommendation.resource:
            return recommendation.resource.title

        return recommendation.intent

    @staticmethod
    def _represent_recommendation_excerpt(recommendation):
        return recommendation.content[:50]

    @staticmethod
    def _represent_project(project):
        fmt = f"{project.name}"
        if project.commune:
            fmt += f" ({project.commune})"

        return fmt

    @staticmethod
    def _represent_project_excerpt(project):
        if project.description:
            return project.description[:50]

        return None

    @staticmethod
    def _represent_note_excerpt(note):
        return note.content[:200] or None

    @staticmethod
    def _represent_followup(followup):
        return followup.comment[:50]

    # -------- Routers -----------#
    # ------ Real Formatters -----#
    def format_private_note_created(self, notification):
        """A note was written by a switchtender"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Conversation.PRIVATE_MESSAGE}"
        excerpt = self._represent_note_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_document_uploaded(self, notification):
        """A document was uploaded by a user"""
        subject = self._represent_user(notification.actor)
        summary = (
            f"{subject} {notification.verb} {notification.action_object.feed_label()}"
        )

        return FormattedNotification(summary=summary, excerpt=None)

    def format_action_recommended(self, notification):
        """An action was recommended by a switchtender"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_recommendation(notification.action_object)
        summary = f"{subject} {verbs.Recommendation.CREATED} '{complement}'"
        excerpt = self._represent_recommendation_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_action_commented(self, notification):
        """An action was commented by someone"""
        subject = self._represent_user(notification.actor)

        if notification.action_object is None:
            summary = f"{subject} {verbs.Recommendation.COMMENTED}"
            excerpt = ""
        else:
            complement = self._represent_recommendation(notification.action_object.task)
            summary = f"{subject} a commenté la recommandation '{complement}'"
            excerpt = self._represent_followup(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_action_became_switchtender(self, notification):
        """Someone joined a project as switchtender"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} s'est joint·e à l'équipe de conseil."

        return FormattedNotification(summary=summary, excerpt=None)

    def format_action_became_advisor(self, notification):
        """Someone joined a project as advisor"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Project.BECAME_ADVISOR}."

        return FormattedNotification(summary=summary, excerpt=None)

    def format_action_became_observer(self, notification):
        """Someone joined a project as observer"""
        subject = self._represent_user(notification.actor)
        summary = f"{subject} {verbs.Project.BECAME_OBSERVER}."

        return FormattedNotification(summary=summary, excerpt=None)

    def format_project_submitted(self, notification):
        """A project was submitted for moderation"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_project(notification.action_object)
        summary = f"{subject} {notification.verb} : '{complement}'"

        excerpt = self._represent_project_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)

    def format_new_project_available(self, notification):
        """A new project is now available"""
        subject = self._represent_user(notification.actor)
        complement = self._represent_project(notification.action_object)
        summary = f"{subject} {verbs.Project.AVAILABLE} '{complement}'"

        excerpt = self._represent_project_excerpt(notification.action_object)

        return FormattedNotification(summary=summary, excerpt=excerpt)
