import Alpine from 'alpinejs';
import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import HardBreak from '@tiptap/extension-hard-break';
import { createMarkdownEditor } from 'tiptap-markdown';
import '../../css/tiptap.css';

const MarkdownEditor = createMarkdownEditor(Editor);

Alpine.data('editor', (content) => {
  let editor;

  return {
    updatedAt: Date.now(), // force Alpine to rerender on selection change
    contact: null,
    markdownContent: null,
    init() {
      const _this = this;

      editor = new MarkdownEditor({
        element: this.$refs.element,
        extensions: [
          StarterKit,
          Link,
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
        ],
        content: content,
        onCreate({ editor }) {
          _this.updatedAt = Date.now();
        },
        onUpdate({ editor }) {
          _this.updatedAt = Date.now();
          _this.renderMarkdown();
          _this.$store.editor.setIsSubmitted(false);

          _this.$store.editor.isEditing = editor.getMarkdown() != '';
          _this.$store.editor.currentMessage = editor.getMarkdown();
        },
        onSelectionUpdate({ editor }) {
          _this.updatedAt = Date.now();
        },
      });

      this.renderMarkdown();
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
      editor.commands.setContent(event.detail);
    },
    renderMarkdown() {
      this.markdownContent = editor.getMarkdown().replaceAll('\\', '');
    },
    handleSetContact(contact) {
      this.contact = { ...contact }; // XXX Copy since it can be destroyed from an inner scope and values result to null
    },
    resetContact() {
      this.contact = null;
    },
  };
});
