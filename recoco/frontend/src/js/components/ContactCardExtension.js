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

  renderHTML({ HTMLAttributes }) {
    console.log('RENDERING CONTACT CARD:', HTMLAttributes);
    const contact = {
      // id: HTMLAttributes.id,
      first_name: HTMLAttributes.firstName,
      last_name: HTMLAttributes.lastName,
      // email: HTMLAttributes.email,
      // phone_no: HTMLAttributes.phoneNo,
      // mobile_no: HTMLAttributes.mobileNo,
      division: HTMLAttributes.division,
      organization: HTMLAttributes.organization,
      // modified: HTMLAttributes.modified,
      // created: HTMLAttributes.created,
    };

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
          contact.first_name || contact.last_name
            ? [
                'span',
                {
                  class:
                    'contact-card-light__name contact-names fr-pr-1v text-ellipsis',
                  title: `${contact.first_name} ${contact.last_name}`,
                },
                `${contact.first_name} ${contact.last_name}`,
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
      mergeAttributes(HTMLAttributes, { 'data-type': 'contact-card' }),
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

  // Custom markdown serializer
  addNodeView() {
    return ({ node, getPos, editor }) => {
      console.log('Creating contact card node view:', node.attrs);

      const contact = {
        // id: node.attrs.id,
        first_name: node.attrs.firstName,
        last_name: node.attrs.lastName,
        // email: node.attrs.email,
        // phone_no: node.attrs.phoneNo,
        // mobile_no: node.attrs.mobileNo,
        division: node.attrs.division,
        organization: node.attrs.organization,
        // modified: node.attrs.modified,
        // created: node.attrs.created,
      };

      const dom = document.createElement('div');
      dom.setAttribute('data-type', 'contact-card');
      dom.className = 'contact-card__container border position-relative';

      let html = '<div class="contact-card-light fr-p-3v bg-white">';
      // Build the contact card HTML
      html += '<div class="contact-card-light__firstline-container">';

      // Add contact book icon
      html +=
        '<span class="fr-icon-contact-book-line fr-btn--icon-left fr-icon-sm"></span>';

      if (contact.first_name || contact.last_name) {
        html += `<span class="contact-card-light__name contact-names fr-pr-1v text-ellipsis" title="${contact.first_name} ${contact.last_name}">${contact.first_name} ${contact.last_name}</span>`;
      }

      if (contact.organization && contact.organization.name) {
        html += `<span class="contact-card-light__organization color-3a3a3a text-position text-ellipsis" title="${contact.organization.name}">${contact.organization.name}</span>`;
      }

      if (contact.division) {
        html += `<span class="contact-card-light__division" title="${contact.division}"><span class="color-3a3a3a text-organization text-ellipsis">${contact.division}</span></span>`;
      }

      html += '</div></div>';

      // Add cancel button
      html += `
        <button class="fr-btn fr-btn--tertiary fr-btn--sm justify-content-center fr-text--sm close-contact-button-style position-absolute top-0 end-0"
                data-test-id="button-remove-contact-card"
                title="Supprimer le contact">
          <span class="fr-icon-close-line" aria-hidden="true"></span>
        </button>
      `;

      dom.innerHTML = html;
      console.log('Contact card HTML:', html);

      // Add event listener for the cancel button
      const cancelButton = dom.querySelector(
        '[data-test-id="button-remove-contact-card"]'
      );
      if (cancelButton) {
        cancelButton.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();

          console.log('Cancel button clicked');
          console.log('getPos:', getPos);
          console.log('node:', node);

          // Remove the contact card from the editor
          if (getPos !== undefined) {
            const pos = getPos();
            const nodeSize = node.nodeSize;

            console.log('Position:', pos, 'Node size:', nodeSize);

            // Delete the entire node
            editor
              .chain()
              .focus()
              .setTextSelection(pos)
              .deleteRange({ from: pos, to: pos + nodeSize })
              .run();

            console.log('Delete command executed');
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
