# encoding: utf-8

"""
Provides all the verbs to be used by actions and notifications

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-26 14:37:45 CEST
"""

import enum


class User:
    LOGIN = "s'est connecté·e"


class Document:
    ADDED = "a ajouté un lien ou un document"
    ADDED_FILE = "a ajouté un document"
    ADDED_LINK = "a ajouté un lien"


class CRM:
    NOTE_CREATED = "a créé une note de CRM"


class Recommendation:
    DRAFTED = "a créé un brouillon de recommandation"
    CREATED = "a recommandé l'action"
    REMINDER_ADDED = "a créé un rappel sur la recommandation"
    COMMENTED = "a commenté la recommandation"

    SEEN = "a consulté la recommandation"
    NOT_APPLICABLE = "a classé la recommandation comme «non applicable»"
    NOT_INTERESTED = "n'est pas intéressé·e par la recommandation"  # ^
    ALREADY_DONE = "a déjà fait l'action recommandée"  # FIXME to keep?
    IN_PROGRESS = "a classé la recommandation comme «en cours»"
    STANDBY = "a classé la recommandation comme «en attente»"
    # STUCK is replaced by STANDBY
    RESUMED = "a redémarré l'action recommandée"  # FIXME to keep ?
    DONE = "a classé la recommandation comme «terminée»"


class Project:
    INVITATION = "a invité un·e collaborateur·rice à rejoindre le projet"

    JOINED = "a rejoint le projet"

    SUBMITTED = "a été déposé"  # FIXME to be removed and keep _BY
    SUBMITTED_BY = "a soumis pour modération le projet"

    VALIDATED = "a été validé"
    VALIDATED_BY = "a validé le projet"

    # FIXME redondant avec VALIDATED
    AVAILABLE = "a déposé le projet"

    # FIXME to be removed
    BECAME_SWITCHTENDER = "est devenu·e aiguilleur·se sur le projet"

    BECAME_ADVISOR = "est devenu·e conseiller·ère sur le projet"
    BECAME_OBSERVER = "est devenu·e observateur·rice sur le projet"
    LEFT_ADVISING = "ne suit plus le projet"
    LEFT_OBSERVING = "ne suit plus le projet"

    # Only related to advisor kanban
    USER_STATUS_UPDATED = "a changé l'état de son suivi projet"


class Survey:
    STARTED = "a démarré l'état des lieux"
    UPDATED = "a mis à jour l'état des lieux"


class Conversation:
    PUBLIC_MESSAGE = "a envoyé un message dans l'espace conversation"
    PRIVATE_MESSAGE = "a envoyé un message dans l'espace conseillers"


# eof
