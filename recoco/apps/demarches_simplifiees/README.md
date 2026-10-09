Le modèle `DSResource` représente l'association entre
- une ressource recoco
- une démarche de https://demarche.numerique.gouv.fr identifiée par son nom
- les départements concernés,
- **le schéma de la démarche** qui est chargé automatiquement par `load_ds_resource_schema` (depuis l'interface admin mais surtout depuis un signal `post_save`)

Le modèle `DSMapping` associe
- le modèle `DSResource` ci-dessus
- le site (portail) côté recoco
- si le lien doit être activé ou non
- le **mapping** des champ pour ré-remplir la démarche.

Un mapping est un objet json de la forme `{ field_ds_id: [*mapping_items] }`. En effet, plusieurs mapping_items sont possibles pour un même champ final. En principe, ce cas se présente en lien avec les **conditions** (voir ci-dessous). La dernière valeur proposée à respecter les conditions est celle qui est retenue.

`resolve_mapping_value` récupère la valeur à partir du mapping concerné.
Les différents types de chemins pour la valeur à remplir sont
- `raw[value]` -> value
- `option[i]` -> lit les options proposées par DN et renvoie la i-ème
- `project.lookup` -> lit en profondeur les attributs du projets pour suivre `lookup`
- `edl.slug` -> lit la valeur de la réponse à la question dont le slug est indiqué
- `edl.slug.comment` -> lit le commentaire de la question dont le slug est indiqué

Un mapping peut être utilisé pour renvoyer la valeur pour pré-remplissage, ou bien pour tester une condition et arbitrer quelle valeur retourner pour pré-remplissage lorsque plusieurs chemins sont proposés.

Les conditions sont un système qui permet de conditionner la valeur mappée en fonction de données qu'on récupère de l'état des lieux.
- Tous les tags précisés dans `condition.tags` doivent être présents dans la réponse d'états des lieux pointée par `condition.value` pour que la condition soit réputée vérifiée
- Toutes les conditions doivent être vérifiée  pour utiliser la valleur donnée dans `mapping.value`

La dataclass `MappingField` formalise la nomenclature d'un mapping.

[//]: # ( todo : heading and examples)

-------------

## En pratique
- Lors d'une nouvelle démarche, on peut s'appuyer sur https://demarche.numerique.gouv.fr/preremplir/<nom de la démarche> pour écrire le mapping et en particulier connaître les identifiants techniques des champs.
- Potentiellement il faut ajouter des `MappingItem` voire des `property` au modèle `Project`
- Les admin/staff du portail créent la ressource à associer
- **Après la publication de la démarche** (sinon le nom de la démarche n'est pas figé, et surtout il n'est pas possible de récupérer le schéma de la démarche), créer un objet `DSResource` sans remplir le schéma : il doit être récupéré à la première sauvegarde
- puis créer un objet `DSMapping` en remplissant le mapping en question comme explicité ci-dessus
