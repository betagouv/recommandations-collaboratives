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
import { FileCardExtension } from './FileCardExtension';
import { ToastType } from '../models/toastType';

const MarkdownEditor = createMarkdownEditor(Editor);

Alpine.data(
  'editor',
  (
    content,
    placeholder,
    isActionPusher = false,
    onLeaveAlert = false,
    maxContacts = 0,
    maxFiles = 0
  ) => {
    let editor;

    return {
      updatedAt: Date.now(), // force Alpine to rerender on selection change
      markdownContent: null,
      formatDate,
      init() {
        const _this = this;

        editor = new MarkdownEditor({
          element: this.$refs.element,
          extensions: [
            StarterKit,
            Link,
            Placeholder.configure({
              placeholder: placeholder || 'Ecrivez votre message ici…',
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
            FileCardExtension,
          ],
          content: content,
          onCreate({ editor }) {
            _this.$store.editor.currentMessage = editor.getMarkdown();
            _this.$store.editor.currentMessageJSON = editor.getJSON();
            if (isActionPusher) {
              const jsonContent = editor.getJSON();
              const newContent = { type: 'doc', content: [] };
              let numberContact = 0,
                numberFile = 0;
              for (const node of jsonContent.content) {
                if (node.type === 'contactCard') {
                  numberContact++;
                  if (numberContact <= 1) {
                    newContent.content.push(node);
                    _this.$dispatch('set-contact', node.attrs.id);
                  }
                } else if (node.type === 'fileCard') {
                  numberFile++;
                  if (numberFile <= 1) {
                    newContent.content.push(node);
                  }
                } else {
                  newContent.content.push(node);
                }
              }
              editor.commands.setContent(newContent);
              if (numberContact > 1 || numberFile > 1) {
                const messages = [];
                if (numberContact > 1) {
                  messages.push('un seul contact');
                }
                if (numberFile > 1) {
                  messages.push('un seul fichier');
                }
                _this.$store.app.notification.message = `Dans ce formulaire, vous ne pouvez ajouter que ${messages.join(' et ')} par recommandation.`;
                _this.$store.app.notification.timeout = 5000;
                _this.$store.app.notification.isOpen = true;
                _this.$store.app.notification.type = ToastType.warning;
              }
            }
            _this.updatedAt = Date.now();
            _this.renderMarkdown();
            _this.isEditorEmpty = editor.isEmpty;
          },
          onUpdate({ editor }) {
            _this.updatedAt = Date.now();
            _this.renderMarkdown();
            _this.$store.editor.setIsSubmitted(false);

            _this.$store.editor.isEditing = editor.getMarkdown() != '';
            _this.$store.editor.currentMessage = editor.getMarkdown();
            _this.$store.editor.currentMessageJSON = editor.getJSON();

            _this.isEditorEmpty = editor.isEmpty;

            _this.$nextTick(() => {
              _this.updatedAt = Date.now();
            });
            if (onLeaveAlert) {
              _this.$store.onLeaveAlert.setDirty(true);
            }
          },
          onSelectionUpdate({ editor }) {
            _this.updatedAt = Date.now();
            _this.renderMarkdown();
          },
        });

        this.$store.editor.editorInstance = editor;
        this.renderMarkdown();

        this.$watch('selectedContact', () => {
          this.forceReactivity();
        });

        this.$watch('selectedFile', () => {
          this.forceReactivity();
        });

        this.$watch('isEditorEmpty', () => {
          this.forceReactivity();
        });

        document.addEventListener('htmx:afterSwap', () => {
          this.markdownContent = '';
          this.selectedContact = null;
          this.selectedFile = null;
          this.forceReactivity();
        });
      },
      forceReactivity() {
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
        this.markdownContent = editor.getMarkdown().replaceAll('\\', '');
      },
      /****************
       * Plugin contact
       */
      selectedContact: null,
      isSearchContactModalOpen: false,
      handleSetContact(contact) {
        this.selectedContact = { ...contact };
        this.forceReactivity();
      },
      handleResetContact() {
        this.selectedContact = null;
        this.forceReactivity();
      },
      openModalSearchContact() {
        this.isSearchContactModalOpen = true;
        this.$store.crisp.isPopupOpen = true;
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
        this.$store.crisp.isPopupOpen = false;
      },
      getContactCount() {
        let count = 0;
        if (editor) {
          editor.state.doc.descendants((node) => {
            if (node.type.name === 'contactCard') {
              count++;
            }
          });
        }
        return count;
      },
      get canAddContact() {
        // Depends of updatedAt for reactivity purpose
        const _ = this.updatedAt;
        if (maxContacts <= 0) return true;
        return this.getContactCount() < maxContacts;
      },
      insertContactCard(contact) {
        if (editor && contact) {
          // Check limit contact before insert (limit to 1)
          if (maxContacts > 0 && this.getContactCount() >= maxContacts) {
            this.$store.app.notification.message =
              maxContacts === 1
                ? "Vous ne pouvez ajouter qu'un seul contact."
                : `Vous ne pouvez ajouter que ${maxContacts} contacts.`;
            this.$store.app.notification.timeout = 5000;
            this.$store.app.notification.isOpen = true;
            this.$store.app.notification.type = ToastType.warning;
            return;
          }

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

          editor.chain().focus().insertContactCard(contactAttributes).run();

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
      removeFileCard() {
        if (editor) {
          // Find the current selection and remove the file card if it's selected
          const { from, to } = editor.state.selection;
          const node = editor.state.doc.nodeAt(from);

          if (node && node.type.name === 'fileCard') {
            editor.chain().focus().deleteSelection().run();
          }
        }
      },
      /****************
       * Plugin file
       */
      getFileCount() {
        let count = 0;
        if (editor) {
          editor.state.doc.descendants((node) => {
            if (node.type.name === 'fileCard') {
              count++;
            }
          });
        }
        return count;
      },
      get canAddFile() {
        // Depends of updatedAt for reactivity purpose
        const _ = this.updatedAt;
        if (maxFiles <= 0) return true; // Pas de limite
        return this.getFileCount() < maxFiles;
      },
      selectedFile: null,
      fileName: '',
      currentFile: null,
      isEditorEmpty: true,
      handleFileUpload(event) {
        const file = event.target.files[0];
        if (file) {
          // Check file limit before insert (limit to 1)
          if (maxFiles > 0 && this.getFileCount() >= maxFiles) {
            this.$store.app.notification.message =
              maxFiles === 1
                ? "Vous ne pouvez ajouter qu'un seul fichier."
                : `Vous ne pouvez ajouter que ${maxFiles} fichiers.`;
            this.$store.app.notification.timeout = 5000;
            this.$store.app.notification.isOpen = true;
            this.$store.app.notification.type = ToastType.warning;

            event.target.value = '';
            return;
          }

          this.selectedFile = file;
          this.fileName = file.name;

          if (editor) {
            const fileAttributes = {
              fileName: file.name,
              fileSize: file.size,
              fileType: file.type,
              uploadedAt: new Date().toISOString(),
              file: file,
            };

            try {
              const result = editor
                .chain()
                .focus()
                .insertFileCard(fileAttributes)
                .run();
            } catch (error) {
              console.error('Error inserting file card:', error);
              console.error('Error stack:', error.stack);
            }
          } else {
            console.error('Editor not initialized');
          }
        } else {
          this.selectedFile = null;
          this.fileName = '';
        }

        this.forceReactivity();
      },
      handleResetFile() {
        this.selectedFile = null;
        this.fileName = '';
        this.currentFile = null;
        this.forceReactivity();
      },
      get isFormValid() {
        // Form is valid if any of these is correct :
        // - Non empty message
        // - Selected contact
        // - Selected file
        // - FileCard in editor
        // unused variable hasMessage but necessary to force reactivity
        const hasMessage = this.$store?.editor.currentMessage !== '';
        const isEditorEmpty = !editor.state.doc.textContent.trim().length;
        const hasContact = this.selectedContact !== null;
        const hasFile = this.selectedFile !== null;

        const hasFileCards = editor.state.doc.descendants((node) => {
          return node.type.name === 'fileCard';
        });

        return !isEditorEmpty || hasContact || hasFile || hasFileCards;
      },
    };
  }
);
