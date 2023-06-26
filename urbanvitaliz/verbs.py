# encoding: utf-8

"""
Provides all the verbs to be used by actions and notifications

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-26 14:37:45 CEST
"""

import enum


class User(enum.StrEnum):
    login = "s'est connecté"


class Document(enum.StrEnum):
    added_old = "a ajouté un document"
    added = "a ajouté un lien ou un document"


class CRM(enum.StrEnum):
    note_created = "a créé une note de CRM"


class Recommendation(enum.StrEnum):
    drafted = "a créé un brouillon de recommandation"
    created = "a recommandé l'action"
    reminder_added = "a créé un rappel sur l'action"
    commented = "a commenté l'action"

    seen = "a visité l'action"
    not_interesting = "n'est pas intéressé·e l'action"
    already_done = "a déjà fait l'action"
    in_progress = "travaille sur l'action"
    stuck = "est bloqué sur l'action"
    resumed = "a redémarré l'action"
    completed = "a terminé l'action"


class Project(enum.StrEnum):
    invitation = "a invité un·e collaborateur·rice à rejoindre le projet"
    joined = "a rejoint l'équipe projet"
    joined_old = "a rejoint l'équipe sur le projet"

    submitted = "a été déposé"
    validated = "a été validé"
    available = "a déposé le projet"

    submitted_old = "a soumis pour modération le projet"
    validated_old = "a validé le projet"

    became_switchtender = "est devenu·e aiguilleur·se sur le projet"
    became_advisor = "est devenu·e conseiller·e sur le projet"
    became_observer = "est devenu·e observateur·rice sur le projet"
    left_advising = "ne conseille plus le projet"

    user_status_updated = "a changé l'état de son suivi"


class Survey(enum.StrEnum):
    started = "a démarré le questionnaire"
    updated = "a mis à jour le questionnaire"


class Conversation(enum.StrEnum):
    public_message = "a envoyé un message"
    private_message = "a envoyé un message dans l'espace conseillers"

    private_message_old = "a créé une note de suivi"


# eof
