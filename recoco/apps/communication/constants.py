TPL_PROJECT_RECEIVED = "project_received"
TPL_PROJECT_ACCEPTED = "project_accepted"
TPL_PROJECT_REFUSED = "project_refused"
TPL_DIGEST_FOR_NON_SWITCHTENDER = "digest_for_non_switchtender"
TPL_DIGEST_FOR_SWITCHTENDER = "digest_for_switchtender"
TPL_NEW_RECOMMENDATIONS_DIGEST = "new_recommendations_digest"
TPL_NEW_SITE_FOR_SWITCHTENDER = "new_site_for_switchtender"
TPL_SHARING_INVITATION = "sharing_invitation"
TPL_PROJECT_REMINDERS_NEW_RECO_DIGEST = "project_reminders_new_reco_digest"
TPL_PROJECT_REMINDERS_WHATS_UP_DIGEST = "project_reminders_whats_up_digest"
TPL_PROJECT_ADDED_TO_NEW_SITE = "project_added_to_new_site"
TPL_ADVISOR_ACCESS_REQUEST_ACCEPTED = "advisor_access_request_accepted"
TPL_ADVISOR_ACCESS_REQUEST_REFUSED = "advisor_access_request_refused"
TPL_MESSAGES_DIGEST = "messages_digest"
TPL_RGDP_DELETION_FIRST_WARNING = "rgpd_deletion_first_warning"
TPL_RGDP_DELETION_SECOND_WARNING = "rgpd_deletion_second_warning"

TPL_CHOICES = (
    (TPL_PROJECT_RECEIVED, "Dossier bien reçu"),
    (TPL_PROJECT_ACCEPTED, "Dossier accepté par l'équipe de modération"),
    (TPL_PROJECT_REFUSED, "Dossier refusé par l'équipe de modération"),
    (TPL_DIGEST_FOR_NON_SWITCHTENDER, "Résumé quotidien général de notifications"),
    (TPL_DIGEST_FOR_SWITCHTENDER, "Résumé quotidien des conseillers"),
    (TPL_NEW_RECOMMENDATIONS_DIGEST, "Résumé des nouvelles recommandations"),
    (
        TPL_NEW_SITE_FOR_SWITCHTENDER,
        "Alerte conseillers d'un nouveau dossier sur le territoire",
    ),
    (TPL_SHARING_INVITATION, "Invitation à rejoindre un dossier"),
    (
        TPL_PROJECT_REMINDERS_NEW_RECO_DIGEST,
        "Rappel des nouvelles recommandations (mail dossier B)",
    ),
    (TPL_PROJECT_REMINDERS_WHATS_UP_DIGEST, "Où en êtes-vous ? (mail dossier C)"),
    (TPL_PROJECT_ADDED_TO_NEW_SITE, "Le Dossier a été validé sur un nouveau portail"),
    (TPL_ADVISOR_ACCESS_REQUEST_ACCEPTED, "Demande d'accès conseillers acceptée"),
    (TPL_ADVISOR_ACCESS_REQUEST_REFUSED, "Demande d'accès conseillers refusée"),
    (TPL_MESSAGES_DIGEST, "Résumé des messages reçus (nouvelle conv')"),
    (
        TPL_RGDP_DELETION_FIRST_WARNING,
        "Premier avertissement avant suppression pour inactivité",
    ),
    (
        TPL_RGDP_DELETION_SECOND_WARNING,
        "Second et dernier avertissement avant suppression pour inactivité",
    ),
)
