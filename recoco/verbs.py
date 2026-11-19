# encoding: utf-8

"""
Provides all the verbs to be used by actions and notifications

authors: guillaume.libersat@beta.gouv.fr, raphael.marvie@beta.gouv.fr
created: 2023-06-26 14:37:45 CEST
"""


class User:
    LOGIN = "s'est connecté·e"
    ADVISOR_REQUEST = "a demandé un accès conseiller"
    ADVISOR_ACCEPTED = "a accepté la demande de compte conseiller de"
    ADVISOR_REJECTED = "a refusé la demande de compte conseiller de"


class Document:
    ADDED_ADVISOR_FILE = "a ajouté dans l'espace conseiller le document"
    ADDED_FILE = "a ajouté le document"
    ADDED_LINK = "a ajouté le lien"


class CRM:
    NOTE_CREATED = "a créé une note de CRM"


class Recommendation:
    DRAFTED = "a créé un brouillon de recommandation"
    CREATED = "a recommandé l'action"
    REMINDER_ADDED = "a créé un rappel sur la recommandation"
    GOT_RECO_REMINDER = "a reçu un rappel de recommandations"
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
    INVITATION = "a invité un·e collaborateur·rice à rejoindre le dossier"
    INVITATION_OWNER = "a invité en tant que référent"

    JOINED_BY_INVITATION = "a accepté l'invitation à rejoindre"
    JOINED_OWNER = "a rejoint en tant que référent"
    NEW_OWNER = "est dorénavant référent sur"

    SUBMITTED = "a été déposé"  # legaccy, replaced by SUBMITTED_BY
    SUBMITTED_BY = "a déposé une nouvelle demande"
    SUBMITTED_BY_ADVISOR = "a créé en tant que conseiller"

    VALIDATED = "a été validé"
    VALIDATED_BY = "a validé"
    REJECTED_BY = "a refusé à la modération"

    # legacy, replaced by SUBMITTED et SUBMITTED_BY
    AVAILABLE = "a déposé"

    # legacy
    BECAME_SWITCHTENDER = "est devenu·e aiguilleur·se sur"

    BECAME_ADVISOR = "est devenu·e conseiller·ère sur"
    BECAME_OBSERVER = "est devenu·e observateur·rice sur"
    LEFT_ADVISING = "ne suit plus"
    LEFT_OBSERVING = "ne suit plus"

    # Only related to advisor kanban # todo guillaume on garde..?
    USER_STATUS_UPDATED = "a changé l'état de son suivi dossier"

    GOT_WHATSUP_REMINDER = "a reçu un rappel de suivi de dossier"

    SET_INACTIVE = "a mis en pause"
    SET_ACTIVE = "a réactivé"

    EDITED = "a modifié les informations sur"
    UPDATE_ADVISORS_NOTE = "a modifié la note interne sur"


class Survey:
    STARTED = "a commencé à remplir l'état des lieux"  # legacy
    UPDATED = "a mis à jour l'état des lieux"


class Conversation:
    PUBLIC_MESSAGE = "a envoyé dans l'espace conversation"  # deprecated but reflects state in db so should not be deleted
    PRIVATE_MESSAGE = "a envoyé dans l'espace conseillers"
    POST_MESSAGE = "a envoyé"


# eof
