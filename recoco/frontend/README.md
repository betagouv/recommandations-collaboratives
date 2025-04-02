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
<div @modal-response="handleModalResponse($event.detail)">
  <!-- Modal component --->
</div>
```
