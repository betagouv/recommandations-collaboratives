# Extension Contact Card pour TipTap

Cette extension permet d'afficher des cartes de contact comme composants intégrés dans l'éditeur TipTap.

## Fonctionnalités

- Affiche les informations de contact dans un format de carte stylisé dans l'éditeur
- Prend en charge les détails de contact incluant nom, organisation, division, email, téléphone et mobile
- Inclut des liens cliquables pour email et téléphone
- Fonctionnalité de copie dans le presse-papiers pour les adresses email
- Design responsive qui correspond au style existant des cartes de contact
- **Bouton d'annulation** pour supprimer la carte de contact de l'éditeur

## Utilisation

### 1. Importer l'Extension

L'extension est déjà importée et configurée dans `Editor.js` :

```javascript
import { ContactCardExtension } from './ContactCardExtension';

// Ajouter au tableau des extensions
extensions: [
  StarterKit,
  Link,
  Placeholder.configure({
    placeholder: 'Ecrivez votre message ici…',
  }),
  ContactCardExtension, // Ajouter cette ligne
  // ... autres extensions
];
```

### 2. Insérer une Carte de Contact

Les cartes de contact sont automatiquement insérées lorsqu'un utilisateur sélectionne un contact depuis la modal de recherche. L'extension gère l'insertion automatiquement.

### 3. Supprimer une Carte de Contact

Chaque carte de contact affiche un bouton "X" (fermer) dans le coin supérieur droit. Cliquer sur ce bouton supprime la carte de contact de l'éditeur.

### 4. Insertion Manuelle (si nécessaire)

Vous pouvez également insérer manuellement une carte de contact en utilisant la commande de l'éditeur :

```javascript
editor
  .chain()
  .focus()
  .insertContactCard({
    id: contact.id,
    firstName: contact.first_name,
    lastName: contact.last_name,
    email: contact.email,
    phoneNo: contact.phone_no,
    mobileNo: contact.mobile_no,
    division: contact.division,
    organization: contact.organization,
    modified: contact.modified,
    created: contact.created,
  })
  .run();
```

### 5. Suppression Manuelle (si nécessaire)

Vous pouvez également supprimer manuellement une carte de contact en utilisant la commande de l'éditeur :

```javascript
editor.chain().focus().removeContactCard().run();
```

## Structure de la Carte de Contact

La carte de contact affiche les informations suivantes :

- **Nom** : Prénom et nom de famille du contact
- **Organisation** : Nom de l'organisation (si disponible)
- **Division** : Division/poste (si disponible)
- **Email** : Adresse email avec lien mailto et bouton de copie
- **Téléphone** : Numéro de téléphone avec lien tel (si disponible)
- **Mobile** : Numéro de mobile avec lien tel (si disponible)
- **Bouton d'annulation** : Bouton "X" pour supprimer la carte

## Stylisation

Les cartes de contact utilisent les classes CSS existantes des cartes de contact et sont stylisées pour s'intégrer parfaitement dans le contexte de l'éditeur. Des styles supplémentaires sont définis dans `editor.scss` pour l'apparence spécifique à l'éditeur.

Le bouton d'annulation est stylisé avec la classe `close-contact-button-style` et apparaît dans le coin supérieur droit de la carte.

## Événements

L'extension écoute l'événement personnalisé `insert-contact-card` pour insérer automatiquement les cartes de contact lorsque les utilisateurs sélectionnent des contacts depuis la modal de recherche.

## Sérialisation Markdown

Les cartes de contact sont sérialisées comme éléments HTML personnalisés dans la sortie markdown, préservant les informations de contact pour le stockage et la récupération.
