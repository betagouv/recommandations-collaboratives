import StarterKit from '@tiptap/starter-kit';
import Link from '@tiptap/extension-link';
import HardBreak from '@tiptap/extension-hard-break';
import { ContactCardExtension } from '../components/ContactCardExtension';
import { FileCardExtension } from '../components/FileCardExtension';

const HardBreakWithShortcuts = HardBreak.extend({
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
});

export function getTiptapSchemaExtensions() {
  return [
    StarterKit.configure({
      link: false,
      hardBreak: false,
      underline: false,
      trailingNode: false,
    }),
    Link,
    HardBreakWithShortcuts,
    ContactCardExtension,
    FileCardExtension,
  ];
}
