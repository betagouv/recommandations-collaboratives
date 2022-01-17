Workflows
=========

Dépot d'un nouveau projet
-------------------------

.. graphviz::

   digraph foo {
      "N: modérateurs de projets"[shape="diamond"];
      "N: acteurs du territoire"[shape="diamond"];
      "N: collaborateurs du projet"[shape="diamond"];

      "E: Invitation à devenir aiguilleur"[shape="parallelogram"];

      "Nouveau projet" -> "N: modérateurs de projets";
      "Nouveau projet" -> "Projet Validé" [label="validation interne"];
      "Projet Validé" -> "N: acteurs du territoire";
      "Projet Validé" -> "N: collaborateurs du projet";

      "N: acteurs du territoire" -> "E: Invitation à devenir aiguilleur";
   }


Devenir Aiguilleur
------------------

.. graphviz::

   digraph foo {
      "N: aiguilleuses internes"[shape="diamond"];
      "N: collaborateurs du projet"[shape="diamond"];

      "Acteur s'assigne comme aiguilleur" -> "Acteur ajouté comme aiguilleur";
      "Acteur s'assigne comme aiguilleur" -> "Acteur souscrit aux notifications";

      "Acteur ajouté comme aiguilleur" -> "N: aiguilleuses internes";
      "Acteur ajouté comme aiguilleur" -> "N: collaborateurs du projet";
   }



Conversations externes
----------------------

.. graphviz::

   digraph foo {
      "N: collaborateurs du projet"[shape="diamond"];
      "N: aiguilleurs du projet"[shape="diamond"];

      "Message d'un aiguilleur" -> "N: collaborateurs du projet";
      "Message d'un aiguilleur" -> "N: aiguilleurs du projet";

      "Message d'un collaborateur" -> "N: aiguilleurs du projet";

   
   }

Conversations internes
----------------------

.. graphviz::

   digraph foo {
      "N: aiguilleurs du projet"[shape="diamond"];

      "Message d'un aiguilleur" -> "N: aiguilleurs du projet";
   
   }


Préférences de notifications
============================

A chaque nouvelle notification
------------------------------

.. graphviz::

   digraph foo {

   "Emission d'une notification" -> "Ajouter aux notifications de l'usager" [label="pour chaque usager souscrit aux notifications du projet"];

   "Ajouter aux notifications de l'usager" -> "Envoyer un mail immédiatement" [label="si notification email immédiate activée"];
   
   }


Toutes les semaines
-------------------

.. graphviz::

   digraph foo {

   "Pour chaque notification personnelles non envoyées par email" -> "Compiler" [label="si résumé par email activé"];

   "Compiler" -> "Envoyer un mail de résumé immédiatement";
   
   }
