# encoding: utf-8

"""
Provides all the verbs to be used by actions and notifications

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-26 14:37:45 CEST
"""

import enum


class User(enum.StrEnum):
    LOGIN = "s'est connecté"


class Document(enum.StrEnum):
    ADDED_OLD = "a ajouté un document"
    ADDED = "a ajouté un lien ou un document"


class CRM(enum.StrEnum):
    NOTE_CREATED = "a créé une note de CRM"


class Recommendation(enum.StrEnum):
    DRAFTED = "a créé un brouillon de recommandation"
    CREATED = "a recommandé l'action"
    REMINDER_ADDED = "a créé un rappel sur l'action"
    COMMENTED = "a commenté l'action"

    SEEN = "a visité l'action"
    NOT_INTERESTED = "n'est pas intéressé·e l'action"
    ALREADY_DONE = "a déjà fait l'action"
    IN_PROGRESS = "travaille sur l'action"
    STUCK = "est bloqué sur l'action"
    RESUMED = "a redémarré l'action"
    DONE = "a terminé l'action"


class Project(enum.StrEnum):
    INVITATION = "a invité un·e collaborateur·rice à rejoindre le projet"
    JOINED = "a rejoint l'équipe projet"
    JOINED_OLD = "a rejoint l'équipe sur le projet"

    SUBMITTED = "a été déposé"
    VALIDATED = "a été validé"
    AVAILABLE = "a déposé le projet"

    SUBMITTED_OLD = "a soumis pour modération le projet"
    VALIDATED_OLD = "a validé le projet"

    BECAME_SWITCHTENDER = "est devenu·e aiguilleur·se sur le projet"
    BECAME_ADVISOR = "est devenu·e conseiller·e sur le projet"
    BECAME_OBSERVER = "est devenu·e observateur·rice sur le projet"
    LEFT_ADVISING = "ne conseille plus le projet"

    USER_STATUS_UPDATED = "a changé l'état de son suivi"


class Survey(enum.StrEnum):
    STARTED = "a démarré le questionnaire"
    UPDATED = "a mis à jour le questionnaire"


class Conversation(enum.StrEnum):
    PUBLIC_MESSAGE = "a envoyé un message"
    PRIVATE_MESSAGE = "a envoyé un message dans l'espace conseillers"

    PRIVATE_MESSAGE_OLD = "a créé une note de suivi"


# eof
