--
-- Conversion of verbs in actions and notifications
--
-- authors: raphael@softosapiens.fr
-- created: 2023-07-03 12:28:59 CEST
--

--
-- extend search path to urbanvitaliz schema on postgres 15

SET search_path TO urbanvitaliz, public ;

--
-- Use a transaction for testing and then atomicity

BEGIN ;

--
-- temporary table to define the mapping of verbs

CREATE TEMP TABLE verb_mapping (
  old VARCHAR,
  new VARCHAR
);

INSERT INTO verb_mapping
  (old, new)
VALUES
  ('old', 'new'),  -- fill w/ actual mapping
  ('s''est connecté', 's''est connecté·e'),
  ('a ajouté un document', 'a ajouté un document'),
  ('a ajouté un lien ou un document', 'a ajouté un lien'),
  ('a créé une note de CRM', 'a créé une note de CRM'),
  ('a créé un brouillon de recommandation', 'a créé un brouillon de recommandation'),
  ('a recommandé l''action', 'a recommandé l''action'),
  ('a créé un rappel sur l''action', 'a créé un rappel sur la recommandation'),
  ('a commenté l''action', 'a commenté la recommandation'),
  ('a accepté l''action', 'a accepté l''action'),
  ('n''est pas intéressé·e l''action', 'n''est pas intéressé·e par la recommandation'),
  ('a refusé l''action', 'a classé la recommandation comme «non applicable»'),
  ('a déjà fait l''action', 'a déjà fait l''action recommandée'),
  ('a redémarré l''action', 'a redémarré l''action recommandée'),
  ('a visité l''action', 'a consulté la recommandation'),
  ('est bloqué sur l''action', 'a classé la recommandation comme «en attente»'),
  ('a terminé l''action', 'a classé la recommandation comme «terminée»'),
  ('travaille sur l''action', 'a classé la recommandation comme «en cours»'),
  ('a soumis pour modération le projet','a déposé un nouveau projet, qui est en attente de validation'),
  ('a déposé le projet', 'a déposé le projet'),
  ('a été déposé', 'a été déposé'),
  ('a été validé', 'a été validé'),
  ('a validé le projet', 'a validé le projet'),
  ('a invité un·e collaborateur·rice à rejoindre le projet', 'a invité un·e collaborateur·rice à rejoindre le projet'),
  ('a rejoint l''équipe projet', 'a rejoint le projet'),
  ('a rejoint l''équipe sur le projet', 'a rejoint le projet'),
  ('est devenu·e aiguilleur·se sur le projet', 'est devenu·e aiguilleur·euse sur le projet'),
  ('est devenu·e conseiller·e sur le projet', 'est devenu·e conseiller·ère sur le projet'),
  ('est devenu·e observateur·rice sur le projet', 'est devenu·e observateur·ice sur le projet'),
  ('n''aiguille plus le projet', 'ne suit plus le projet'),
  ('ne conseille plus le projet', 'ne suit plus le projet'),
  ('a changé l''état de son suivi','a changé l''état de son suivi'),
  ('a démarré le questionnaire', 'a commencé à remplir l''état des lieux'),
  ('a mis à jour le questionnaire', 'a mis à jour l''état des lieux'),
  ('a rédigé un message', 'a envoyé un message dans l''espace conversation'),
  ('a envoyé un message', 'a envoyé un message dans l''espace conversation'),
  ('a envoyé un message dans l''espace conseillers', 'a envoyé un message dans l''espace conseillers'),
  ('a créé une note de suivi', 'a envoyé un message dans l''espace conseillers'),
  ('a rédigé une note interne', 'a envoyé un message dans l''espace conseillers');


--
-- apply the mapping to notification verbs

UPDATE notifications_notification AS notif
SET verb = mapping.new
FROM verb_mapping mapping
WHERE notif.verb = mapping.old ;


--
-- apply the mapping to action verbs

UPDATE actstream_action AS action
SET verb = mapping.new
FROM verb_mapping mapping
WHERE action.verb = mapping.old ;


--
-- check the result

WITH all_verbs AS (
  SELECT DISTINCT verb
  FROM notifications_notification
UNION
  SELECT DISTINCT verb
  FROM actstream_action
)
SELECT DISTINCT verb
FROM all_verbs
ORDER BY verb ;


--
-- cleanup temp table

DROP TABLE verb_mapping ;

--
-- to commit once properly tested

ROLLBACK ;


-- eof
