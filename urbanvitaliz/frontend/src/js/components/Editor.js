import Alpine from 'alpinejs'
import { Editor } from '@tiptap/core'
import StarterKit from '@tiptap/starter-kit'
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
          StarterKit
        ],
        content: content,
        onCreate({ editor }) {
          _this.updatedAt = Date.now()
        },
        onUpdate({ editor }) {
          _this.updatedAt = Date.now()
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
    renderMarkdown() {
      this.markdownContent = editor.getMarkdown()
    }
  };
});
