# Frontend documentation

## Composants

### Fenêtre modale

Vous trouverez une interface à utiliser pour normaliser l'utilisation des fenetre modal dans l'application.

`recoco/frontend/src/js/models/Modal.js`

Elle permet de définir le comportement d'une fenetre modale lors de sa fermeture avec deux possibilités :

- fermeture avec envoie de données `responseModal`
- fermerture sans envoie de données `closeModal`

Ces fonctions utilisent un evènement qui devra être écouté dans le composant parent de la fenetre modale : `@modal-response`

Exemple dans le template du composant parent :

```html
<div @modal-response="handleModalResponse($event)">
  <!-- Modal component --->
</div>
```

## Icônes

### Comment ajouter une icône personnalisée ?

Placer le svg dans le dossier `recoco/frontend/src/assets/`.

Pour ajouter une icône personnalisée, il faut ajouter le nom de l'icône dans le fichier `recoco/frontend/src/css/custom-icon.css`.

Exemple :

```css
.fr-icon-contact-book-line::after,
.fr-icon-contact-book-line::before {
  mask-image: url(../assets/contacts-book-line.svg);
}
```

Et enfin utiliser l'icône dans le code html.
