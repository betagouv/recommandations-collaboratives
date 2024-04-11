
TPL_PROJECT_RECEIVED = "project_received"
TPL_PROJECT_ACCEPTED = "project_accepted"
TPL_DIGEST_FOR_NON_SWITCHTENDER = "digest_for_non_switchtender"
TPL_DIGEST_FOR_SWITCHTENDER = "digest_for_switchtender"
TPL_NEW_RECOMMENDATIONS_DIGEST = "new_recommendations_digest"
TPL_NEW_SITE_FOR_SWITCHTENDER = "new_site_for_switchtender"
TPL_SHARING_INVITATION = "sharing_invitation"
TPL_PROJECT_REMINDERS_NEW_RECO_DIGEST = "project_reminders_new_reco_digest"
TPL_PROJECT_REMINDERS_WHATS_UP_DIGEST = "project_reminders_whats_up_digest"

TPL_CHOICES = (
    (TPL_PROJECT_RECEIVED, "Projet bien reçu"),
    (TPL_PROJECT_ACCEPTED, "Projet accepté par l'équipe de modération"),
    (TPL_DIGEST_FOR_NON_SWITCHTENDER, "Résumé quotidien général de notifications"),
    (TPL_DIGEST_FOR_SWITCHTENDER, "Résumé quotidien des conseillers"),
    (TPL_NEW_RECOMMENDATIONS_DIGEST, "Résumé des nouvelles recommandations"),
    (TPL_NEW_SITE_FOR_SWITCHTENDER, "Alerte conseillers d'un nouveau projet sur le territoire"),
    (TPL_SHARING_INVITATION, "Invitation à rejoindre un projet"),
    (TPL_PROJECT_REMINDERS_NEW_RECO_DIGEST, "Rappel des nouvelles recommandations (mail projet B)"),
    (TPL_PROJECT_REMINDERS_WHATS_UP_DIGEST, "Où en êtes-vous ? (mail projet C)"),
)
