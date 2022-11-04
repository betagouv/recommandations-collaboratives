import Alpine from 'alpinejs'
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import { createMarkdownEditor } from 'tiptap-markdown';
import '../../css/tiptap.css'

const MarkdownEditor = createMarkdownEditor(Editor);

Alpine.data('editor', (content) => {

  let editor

  return {
    updatedAt: Date.now(), // force Alpine to rerender on selection change
    markdownContent: content ? content : "",
    init() {
      const _this = this

      editor = new MarkdownEditor({
        element: this.$refs.element,
        extensions: [
          StarterKit,
          Link
        ],
        content: content,
        onCreate({ editor }) {
          _this.updatedAt = Date.now()
        },
        onUpdate({ editor }) {
          _this.updatedAt = Date.now()
          _this.renderMarkdown();
        },
        onSelectionUpdate({ editor }) {
          _this.updatedAt = Date.now()
        }
      });
    },
    isLoaded() {
      return editor
    },
    isActive(type, opts = {}) {
      return editor.isActive(type, opts)
    },
    toggleHeading(opts) {
      editor.chain().toggleHeading(opts).focus().run()
    },
    toggleBold() {
      editor.chain().toggleBold().focus().run()
    },
    toggleItalic() {
      editor.chain().toggleItalic().focus().run()
    },
    toggleBulletList() {
      editor.chain().toggleBulletList().focus().run()
    },
    setLink() {

      const previousUrl = editor.getAttributes('link').href
      const url = window.prompt('URL', previousUrl)

      // cancelled
      if (url === null) {
        return
      }

      // empty
      if (url === '') {
        editor.chain().focus().extendMarkRange('link').unsetLink()
          .run()

        return
      }

      // update link
      editor.chain().focus().extendMarkRange('link').setLink({ href: url })
        .run()
    },
    unsetLink() {
      editor.chain().focus().unsetLink().run()
    },
    renderMarkdown() {
      this.markdownContent = editor.getMarkdown()
    }
  };
});
