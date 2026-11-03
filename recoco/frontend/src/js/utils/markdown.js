import { marked } from 'marked';
import DOMPurify from 'dompurify';

export function renderMarkdown(content) {
  const html = marked.parse(content);
  return DOMPurify.sanitize(html);
}
