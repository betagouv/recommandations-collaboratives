import Alpine from 'alpinejs';
import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import HardBreak from '@tiptap/extension-hard-break';
import { createMarkdownEditor } from 'tiptap-markdown';
import '../../css/tiptap.css';
import { formatDate } from '../utils/date';
import Placeholder from '@tiptap/extension-placeholder';
import { ContactCardExtension } from './ContactCardExtension';

// const MarkdownEditor = createMarkdownEditor(Editor);

Alpine.data('editor', (content) => {
  let editor;

  return {
    updatedAt: Date.now(), // force Alpine to rerender on selection change
    markdownContent: null,
    formatDate,
    init() {
      const _this = this;

      editor = new Editor({
        element: this.$refs.element,
        extensions: [
          StarterKit,
          Link,
          Placeholder.configure({
            placeholder: 'Ecrivez votre message ici…',
          }),
          HardBreak.extend({
            addKeyboardShortcuts() {
              const handleEnter = () =>
                this.editor.commands.first(({ commands }) => [
                  () => commands.newlineInCode(),
                  () => commands.createParagraphNear(),
                  () => commands.liftEmptyBlock(),
                  () => commands.splitBlock(),
                ]);

              return {
                'Shift-Enter': handleEnter,
                'Control-Enter': handleEnter,
                'Cmd-Enter': handleEnter,
              };
            },
          }),
          ContactCardExtension,
        ],
        content: content,
        onCreate({ editor }) {
          _this.updatedAt = Date.now();
          _this.renderMarkdown();
          _this.isEditorEmpty = editor.isEmpty;
        },
        onUpdate({ editor }) {
          _this.updatedAt = Date.now();
          _this.renderMarkdown();
          _this.$store.editor.setIsSubmitted(false);

          _this.$store.editor.isEditing = editor.getHTML() != '';
          _this.$store.editor.currentMessage = editor.getHTML();

          // Mettre à jour la propriété réactive
          _this.isEditorEmpty = editor.isEmpty;

          // S'assurer que Alpine.js traite les mises à jour
          _this.$nextTick(() => {
            _this.updatedAt = Date.now();
          });
        },
        onSelectionUpdate({ editor }) {
          _this.updatedAt = Date.now();
          _this.renderMarkdown();
        },
      });

      this.renderMarkdown();

      // Ajouter des watchers pour déclencher des mises à jour réactives
      this.$watch('selectedContact', () => {
        this.forceReactivity();
      });

      this.$watch('selectedFile', () => {
        this.forceReactivity();
      });

      this.$watch('isEditorEmpty', () => {
        this.forceReactivity();
      });
    },
    forceReactivity() {
      // Force Alpine.js à re-rendre le composant
      this.updatedAt = Date.now();
    },
    isLoaded() {
      return editor;
    },
    isActive(type, opts = {}) {
      return editor.isActive(type, opts);
    },
    toggleHeading(opts) {
      editor.chain().toggleHeading(opts).focus().run();
    },
    toggleBold() {
      editor.chain().toggleBold().focus().run();
    },
    toggleItalic() {
      editor.chain().toggleItalic().focus().run();
    },
    toggleBulletList() {
      editor.chain().toggleBulletList().focus().run();
    },
    setLink() {
      const previousUrl = editor.getAttributes('link').href;
      const url = window.prompt('URL', previousUrl);

      // cancelled
      if (url === null) {
        return;
      }

      // empty
      if (url === '') {
        editor.chain().focus().extendMarkRange('link').unsetLink().run();

        return;
      }

      // update link
      editor
        .chain()
        .focus()
        .extendMarkRange('link')
        .setLink({ href: url })
        .run();
    },
    unsetLink() {
      editor.chain().focus().unsetLink().run();
    },
    setMarkdownContent(event) {
      editor.commands.setContent(event.detail.text);
      if (event.detail.contact) {
        this.selectedContact = event.detail.contact;
      } else {
        this.selectedContact = null;
      }
    },
    renderMarkdown() {
      this.markdownContent = editor.getHTML();
    },
    /****************
     * Plugin contact
     */
    selectedContact: null,
    isSearchContactModalOpen: false,
    handleSetContact(contact) {
      this.selectedContact = { ...contact }; // XXX Copy since it can be destroyed from an inner scope and values result to null
      this.forceReactivity();
    },
    handleResetContact() {
      this.selectedContact = null;
      this.forceReactivity();
    },
    openModalSearchContact() {
      this.isSearchContactModalOpen = true;
    },
    closeSearchContactModal(event) {
      if (event.target.id !== 'search-contact-modal') {
        return;
      }
      const contact = event.detail;
      if (contact) {
        this.handleSetContact(contact);
        // Insert contact card into editor
        this.insertContactCard(contact);
      }
      this.isSearchContactModalOpen = false;
    },
    insertContactCard(contact) {
      if (editor && contact) {
        console.log('Inserting contact card:', contact);

        const contactAttributes = {
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
        };

        console.log('Contact attributes:', contactAttributes);

        editor.chain().focus().insertContactCard(contactAttributes).run();

        // Mettre à jour le contact sélectionné
        this.selectedContact = contact;
        this.forceReactivity();
      }
    },
    removeContactCard() {
      if (editor) {
        // Find the current selection and remove the contact card if it's selected
        const { from, to } = editor.state.selection;
        const node = editor.state.doc.nodeAt(from);

        if (node && node.type.name === 'contactCard') {
          editor.chain().focus().deleteSelection().run();
        }
      }
    },
    /****************
     * Plugin file
     */
    selectedFile: null,
    fileName: '',
    isEditorEmpty: true, // Propriété réactive pour suivre si l'éditeur est vide
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.selectedFile = file;
        // Mettre à jour le nom du fichier affiché
        this.fileName = file.name;
      } else {
        this.selectedFile = null;
        this.fileName = '';
      }
      // Force la réactivité
      this.forceReactivity();
    },
    get isFormValid() {
      // Le formulaire est valide si au moins un des éléments suivants est présent :
      // - Un message non vide
      // - Un contact sélectionné
      // - Un fichier sélectionné
      // Utiliser les propriétés du store pour la réactivité
      // unused variable hasMessage but necessary to force reactivity
      const hasMessage = this.$store.editor.currentMessage !== '';
      const isEditorEmpty = !editor.state.doc.textContent.trim().length;
      const hasContact = this.selectedContact !== null;
      const hasFile = this.selectedFile !== null;

      return !isEditorEmpty || hasContact || hasFile;
    },
  };
});
