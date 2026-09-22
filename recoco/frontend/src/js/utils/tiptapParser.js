import { generateHTML } from '@tiptap/core';
import { getTiptapSchemaExtensions } from './tiptapExtensions';

export function tiptapParserJSONToHTML(content) {
  return generateHTML(content, getTiptapSchemaExtensions());
}
