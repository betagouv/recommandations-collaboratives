import { Node, mergeAttributes } from '@tiptap/core';

export const ContactCardExtension = Node.create({
  name: 'contactCard',
  group: 'block',
  atom: true,

  addAttributes() {
    return {
      id: {
        default: null,
      },
      firstName: {
        default: null,
      },
      lastName: {
        default: null,
      },
      email: {
        default: null,
      },
      phoneNo: {
        default: null,
      },
      mobileNo: {
        default: null,
      },
      division: {
        default: null,
      },
      organization: {
        default: null,
      },
      modified: {
        default: null,
      },
      created: {
        default: null,
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="contact-card"]',
      },
    ];
  },

  // Produce the HTML to export from tiptap
  renderHTML({ HTMLAttributes }) {
    const contact = { HTMLAttributes };
    //   id: HTMLAttributes.id,
    //   first_name: HTMLAttributes.firstName,
    //   last_name: HTMLAttributes.lastName,
    //   // email: HTMLAttributes.email,
    //   // phone_no: HTMLAttributes.phoneNo,
    //   // mobile_no: HTMLAttributes.mobileNo,
    //   division: HTMLAttributes.division,
    //   organization: HTMLAttributes.organization,
    //   // modified: HTMLAttributes.modified,
    //   // created: HTMLAttributes.created,
    // };

    // Create a simple contact card structure
    const contactCardContent = [
      'div',
      {
        class: 'contact-card__container border position-relative',
      },
      [
        'div',
        {
          class: 'contact-card-light position-relativefr-p-3v bg-white',
        },
        [
          'div',
          { class: 'contact-card-light__firstline-container' },
          [
            'span',
            { class: 'fr-icon-contact-book-line fr-btn--icon-left fr-icon-sm' },
          ],
          contact.firstName || contact.lastName
            ? [
                'span',
                {
                  class:
                    'contact-card-light__name contact-names fr-pr-1v text-ellipsis',
                  title: `${contact.firstName} ${contact.lastName}`,
                },
                `${contact.firstName} ${contact.lastName}`,
              ]
            : null,
          contact.organization && contact.organization.name
            ? [
                'span',
                {
                  class:
                    'contact-card-light__organization color-3a3a3a text-position text-ellipsis',
                  title: contact.organization.name,
                },
                contact.organization.name,
              ]
            : null,
          contact.division
            ? [
                'span',
                {
                  class: 'contact-card-light__division',
                  title: contact.division,
                },
                [
                  'span',
                  {
                    class: 'color-3a3a3a text-organization text-ellipsis',
                  },
                  contact.division,
                ],
              ]
            : null,
        ].filter(Boolean),
      ],
    ];

    return [
      'div',
      mergeAttributes(HTMLAttributes, {
        'data-type': 'contact-card',
        'data-id': HTMLAttributes.id,
      }),
      contactCardContent,
    ];
  },

  addCommands() {
    return {
      insertContactCard:
        (attributes) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: attributes,
          });
        },
      removeContactCard:
        () =>
        ({ commands }) => {
          return commands.deleteSelection();
        },
    };
  },

  // Custom node view in tiptap
  addNodeView() {
    return ({ node, getPos, editor }) => {
      const contact = {
        first_name: node.attrs.firstName,
        last_name: node.attrs.lastName,
        division: node.attrs.division,
        organization: node.attrs.organization,
      };

      const dom = document.createElement('div');
      dom.setAttribute('data-type', 'contact-card');
      dom.className = 'contact-card__container border position-relative';

      const contactCardContentPart = {
        name: '',
        organization: '',
        division: '',
      };

      if (contact.first_name || contact.last_name) {
        contactCardContentPart.name = `<span class="contact-card-light__name contact-names fr-pr-1v text-ellipsis" title="${contact.first_name} ${contact.last_name}">${contact.first_name} ${contact.last_name}</span>`;
      }

      if (contact.organization && contact.organization.name) {
        contactCardContentPart.organization = `<span class="contact-card-light__organization color-3a3a3a text-position text-ellipsis" title="${contact.organization.name}">${contact.organization.name}</span>`;
      }

      if (contact.division) {
        contactCardContentPart.division = `<span class="contact-card-light__division" title="${contact.division}"><span class="color-3a3a3a text-organization text-ellipsis">${contact.division}</span></span>`;
      }

      // Build the contact card HTML
      let html = `
        <div class="contact-card-light fr-p-3v bg-white">
          <div class="contact-card-light__firstline-container">
            <span class="fr-icon-contact-book-line fr-btn--icon-left fr-icon-sm"></span>
            ${contactCardContentPart.name}
            ${contactCardContentPart.organization}
            ${contactCardContentPart.division}
          </div>
        </div>
        <button class="fr-btn fr-btn--tertiary fr-btn--sm justify-content-center fr-text--sm close-contact-button-style position-absolute top-0 end-0"
                data-test-id="button-remove-contact-card"
                title="Supprimer le contact">
          <span class="fr-icon-close-line" aria-hidden="true"></span>
        </button>
      `;

      dom.innerHTML = html;

      // Add event listener for the cancel button
      const cancelButton = dom.querySelector(
        '[data-test-id="button-remove-contact-card"]'
      );
      if (cancelButton) {
        cancelButton.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();

          // Remove the contact card from the editor
          if (getPos !== undefined) {
            const pos = getPos();
            const nodeSize = node.nodeSize;

            // Delete the entire node
            editor
              .chain()
              .focus()
              .setTextSelection(pos)
              .deleteRange({ from: pos, to: pos + nodeSize })
              .run();
          }
        });
      }

      return {
        dom,
        update: (updatedNode) => {
          // Handle updates if needed
          return true;
        },
      };
    };
  },
});
