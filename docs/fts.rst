Indexation et recherche
#######################

L'indexation et la recherche plein texte sont gérées par `Watson <https://github.com/etianen/django-watson/tree/master>`_ (`documentation
<https://github.com/etianen/django-watson/wiki>`_).


Installation et maintien des index
==================================

Dans le cas d'une première installation, construire la structure avec :


.. code-block:: bash

   ./manage.py installwatson


Puis, à l'installation ou à chaque modification de modèle, rafraîchir les index avec :

.. code-block:: bash

   ./manage.py buildwatson


Notez cependant que la configuration actuelle indique à `Watson`_ de mettre à
jour les index à chaque sauvegarde d'un modèle enregistré, il n'est pas
nécessaire de lancer cette commande périodiquement (sauf en cas
d'inserts/suppressions massives).


Modèles indexés
===============

Actuellement, les modèles principaux sont : :class:`Project<recoco.apps.projects.models.Project>`, :class:`ProjectAnnotations (CRM)<recoco.apps.crm.models.ProjectAnnotations>`, :class:`User<django.contrib.auth.models.User>`, :class:`Resource<recoco.apps.resources.models.Resource>`.


Adaptateurs de recherche
========================

Dans certains cas, il est nécessaire d'écrire des adaptateurs pour améliorer l'indexation. Voici un exemple avec les dossiers :

.. autoclass:: recoco.apps.projects.models.ProjectSearchAdapter
   :members:
   :undoc-members:


Fragments de rendu côté frontend
================================

`Watson`_ offre un templatetag (``search_result_item``) pour rechercher automatiquement un fragment côté frontend qui correspond au nom du modèle indexé.
Pour ce faire, il suit la convention suivante:

.. code-block::

   watson/includes/search_result_[APP_NAME]_[MODEL_NAME].html

Par exemple, si vous souhaitez faire un fragment de recherche pour le modèle :class:`ProjectAnnotations<recoco.apps.crm.models.ProjectAnnotations>` du CRM, le fichier s'appelera alors : ``watson/includes/search_result_crm_projectannotations.html``

Améliorations
=============

Notez qu'aucun effort n'a été fait pour l'instant pour s'assurer l'indexation
atomique des modèles liés (cf `doc
<https://github.com/etianen/django-watson/wiki/registering-models#searching-across-related-models>`_).
