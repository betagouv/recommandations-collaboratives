
# Notes sur le système de Webhook

Le système est basé sur la lib `django-webhook`.
Pour le moment sur ce fork: <https://github.com/etchegom/django-webhook>, le temps de soumettre les changements au repo source.

Les changements dans ce fork permettent d'étendre la class `SignalListener`, afin de prendre en compte le multi-sites.
Cette surcharge se trouve dans `recoco.apps.webhook.signals.WebhookSignalListener`, ainsi que dans le model `WebhookSite` qui permet de mettre en place un webhook pour un site donné.

Les événements de webhook sont envoyés en `post_save` des modèles référencés.
Pour le moment, deux modèles sont activés:

- `projects.Project` => notifie des changements sur un projet
- `survey.Answer` => notifie des changements sur un EDL

Les payloads des événements de webhook sont construits sur les serializers DRF de l'API.
