import { generateHTML } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { ContactCardExtension } from '../components/ContactCardExtension';
import { FileCardExtension } from '../components/FileCardExtension';

export function tiptapParserJSONToHTML(content) {
  return generateHTML(content, [
    StarterKit,
    ContactCardExtension,
    FileCardExtension,
  ]);
}
