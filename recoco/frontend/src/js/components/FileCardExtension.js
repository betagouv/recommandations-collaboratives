import { Node, mergeAttributes } from '@tiptap/core';
import { formatFileSize } from '../utils/file';

const FileCardExtension = Node.create({
  name: 'fileCard',
  group: 'block',
  atom: true,
  selectable: true,
  draggable: true,

  addAttributes() {
    return {
      fileName: {
        default: null,
      },
      fileSize: {
        default: null,
      },
      fileType: {
        default: null,
      },
      uploadedBy: {
        default: null,
      },
      uploadedAt: {
        default: null,
      },
      file: {
        default: null,
      },
    };
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-type="file-card"]',
      },
    ];
  },

  renderHTML({ HTMLAttributes }) {
    const { fileName, fileSize, fileType, file } = HTMLAttributes;
    const formattedSize = fileSize ? formatFileSize(fileSize) : '';

    const fileCardContent = [
      'div',
      {
        class:
          'd-flex align-items-center file__card fr-p-3v bg-white position-relative',
      },
      ['span', { class: 'fr-icon-file-add-line fr-btn--icon-left fr-icon-sm' }],
      [
        'span',
        { class: 'file-upload-text' },
        `${fileName || 'Fichier sans nom'} ${formattedSize}`,
      ],
      [
        'div',
        { class: 'file-card__actions' },
        [
          'button',
          {
            type: 'button',
            class:
              'fr-btn fr-btn--tertiary fr-btn--sm justify-content-center fr-text--sm close-file-button-style position-absolute top-0 end-0',
            title: 'Supprimer le fichier',
            'data-test-id': 'file-card-delete',
          },
          ['span', { class: 'fr-icon-close-line', 'aria-hidden': 'true' }],
        ],
      ],
    ];

    return [
      'div',
      mergeAttributes(HTMLAttributes, {
        'data-type': 'file-card',
        'data-id': HTMLAttributes.id,
      }),
      fileCardContent,
    ];
  },

  addCommands() {
    return {
      insertFileCard:
        (attributes) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: attributes,
          });
        },
      removeFileCard:
        () =>
        ({ commands }) => {
          return commands.deleteSelection();
        },
    };
  },

  // Custom node view like ContactCard
  addNodeView() {
    return ({ node, getPos, editor }) => {
      const { fileName, fileSize, fileType, file } = node.attrs;
      const formattedSize = fileSize ? formatFileSize(fileSize) : '';

      const dom = document.createElement('div');
      dom.setAttribute('data-type', 'file-card');
      dom.setAttribute('data-test-id', 'file-card');
      dom.className =
        'd-flex align-items-center file__card fr-p-3v bg-white position-relative';

      // Build the file card HTML
      const html = `
          <span class="fr-icon-file-add-line fr-btn--icon-left fr-icon-sm"></span>
          <span class="file-upload-text"> ${fileName || 'Fichier sans nom'} ${formattedSize}</span>
          <div class="file-card__actions">
            <button type="button" class="fr-btn fr-btn--tertiary fr-btn--sm justify-content-center fr-text--sm close-file-button-style position-absolute top-0 end-0"
                    title="Supprimer le fichier" data-test-id="file-card-delete">
              <span class="fr-icon-close-line" aria-hidden="true"></span>
            </button>
          </div>
      `;

      dom.innerHTML = html;

      // Add event listener for the delete button
      const deleteButton = dom.querySelector(
        '[data-test-id="file-card-delete"]'
      );
      if (deleteButton) {
        deleteButton.addEventListener('click', (event) => {
          event.preventDefault();
          event.stopPropagation();

          // Remove the file card from the editor
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

export { FileCardExtension };
