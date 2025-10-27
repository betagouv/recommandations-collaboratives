import Alpine from '../utils/globals';

document.addEventListener('alpine:init', () => {
  Alpine.store('editor', {
    editorInstance: null,
    currentMessage: '',
    currentMessageJSON: '',
    isEditing: false,
    isSubmitted: false,
    setContent(content) {
      Alpine.raw(this.editorInstance).commands.setContent(content);
    },
    clearEditorContent() {
      Alpine.raw(this.editorInstance).commands.clearContent();
    },
    setIsSubmitted(isSubmitted) {
      this.isSubmitted = isSubmitted;
    },
    /**
     * Parse TipTap JSON content and extract nodes in order
     * @param {Object} tiptapJson - The JSON content from TipTap editor
     * @returns {Array} Array of nodes with position, type, and relevant data
     */
    parseTipTapContent(tiptapJson) {
      const nodes = [];
      let position = 1;

      if (!tiptapJson || !tiptapJson.content) {
        return nodes;
      }

      const processNode = (node) => {
        if (!node) return;

        switch (node.type) {
          case 'doc':
            // Process all child nodes of the document
            if (node.content) {
              node.content.forEach(processNode);
            }
            break;

          case 'paragraph':
            // Extract text content from paragraph
            if (node.content) {
              const textContent = this.extractTextFromNode(node);
              if (textContent.trim()) {
                nodes.push({
                  position: position++,
                  type: 'MarkdownNode',
                  text: textContent,
                });
              }
            }
            break;

          case 'contactCard':
            // Extract contact card information
            nodes.push({
              position: position++,
              type: 'ContactNode',
              contact_id: node.attrs?.id,
            });
            break;

          case 'fileCard':
            // Extract file card information
            nodes.push({
              position: position++,
              type: 'DocumentNode',
              document_id: node.attrs?.id,
              fileName: node.attrs?.fileName,
              file: node.attrs?.file,
            });
            break;

          case 'heading':
            // Handle headings with proper markdown formatting
            if (node.content) {
              const textContent = this.extractTextFromNode(node);
              if (textContent.trim()) {
                const level = node.attrs?.level || 1;
                const headingPrefix = '#'.repeat(level);
                nodes.push({
                  position: position++,
                  type: 'MarkdownNode',
                  text: `${headingPrefix} ${textContent}`,
                });
              }
            }
            break;

          case 'bulletList':
            // Handle bullet lists - process each list item
            if (node.content) {
              node.content.forEach((listItem) => {
                if (listItem.type === 'listItem' && listItem.content) {
                  const textContent = this.extractTextFromNode(listItem);
                  if (textContent.trim()) {
                    nodes.push({
                      position: position++,
                      type: 'MarkdownNode',
                      text: `- ${textContent}`,
                    });
                  }
                }
              });
            }
            break;

          case 'orderedList':
            // Handle ordered lists - process each list item with numbering
            if (node.content) {
              let itemNumber = 1;
              node.content.forEach((listItem) => {
                if (listItem.type === 'listItem' && listItem.content) {
                  const textContent = this.extractTextFromNode(listItem);
                  if (textContent.trim()) {
                    nodes.push({
                      position: position++,
                      type: 'MarkdownNode',
                      text: `${itemNumber}. ${textContent}`,
                    });
                    itemNumber++;
                  }
                }
              });
            }
            break;

          case 'listItem':
            // List items are handled by their parent lists, but we can process them individually if needed
            if (node.content) {
              const textContent = this.extractTextFromNode(node);
              if (textContent.trim()) {
                nodes.push({
                  position: position++,
                  type: 'MarkdownNode',
                  text: textContent,
                });
              }
            }
            break;

          case 'blockquote':
            // Handle blockquotes with proper markdown formatting
            if (node.content) {
              const textContent = this.extractTextFromNode(node);
              if (textContent.trim()) {
                // Split by lines and add > prefix to each line
                const lines = textContent.split('\n');
                const quotedText = lines.map((line) => `> ${line}`).join('\n');
                nodes.push({
                  position: position++,
                  type: 'MarkdownNode',
                  text: quotedText,
                });
              }
            }
            break;

          case 'codeBlock':
            // Handle code blocks with proper markdown formatting
            if (node.content) {
              const textContent = this.extractTextFromNode(node);
              if (textContent.trim()) {
                const language = node.attrs?.language || '';
                const codeBlock = language
                  ? `\`\`\`${language}\n${textContent}\n\`\`\``
                  : `\`\`\`\n${textContent}\n\`\`\``;
                nodes.push({
                  position: position++,
                  type: 'MarkdownNode',
                  text: codeBlock,
                });
              }
            }
            break;

          default:
            // For any other node types, process their children
            if (node.content) {
              node.content.forEach(processNode);
            }
            break;
        }
      };

      // Start processing from the root
      processNode(tiptapJson);

      return nodes;
    },

    /**
     * Extract text content from a TipTap node, preserving markdown formatting
     * @param {Object} node - The TipTap node
     * @returns {string} The extracted text with markdown formatting
     */
    extractTextFromNode(node) {
      if (!node) return '';

      let text = '';

      if (node.text) {
        // Handle text nodes with marks (bold, italic, etc.)
        let nodeText = node.text;

        if (node.marks) {
          node.marks.forEach((mark) => {
            switch (mark.type) {
              case 'bold':
                nodeText = `**${nodeText}**`;
                break;
              case 'italic':
                nodeText = `*${nodeText}*`;
                break;
              case 'code':
                nodeText = `\`${nodeText}\``;
                break;
              case 'link':
                nodeText = `[${nodeText}](${mark.attrs?.href || ''})`;
                break;
              case 'strike':
                nodeText = `~~${nodeText}~~`;
                break;
              case 'underline':
                // Underline is not standard markdown, but we can represent it
                nodeText = `<u>${nodeText}</u>`;
                break;
            }
          });
        }

        text += nodeText;
      }

      if (node.content) {
        node.content.forEach((child) => {
          text += this.extractTextFromNode(child);
        });
      }

      return text;
    },
    /**
     * Convert parsed nodes back to TipTap JSON structure
     * @param {Array} nodes - Array of nodes with position, type, and relevant data
     * @returns {Object} TipTap JSON structure
     */
    convertNodesToTipTapJson(nodes) {
      if (!nodes || nodes.length === 0) {
        return {
          type: 'doc',
          content: [],
        };
      }

      // Sort nodes by position to maintain order
      const sortedNodes = [...nodes].sort((a, b) => a.position - b.position);

      const content = sortedNodes.map((node) => {
        switch (node.type) {
          case 'MarkdownNode':
            return this.parseMarkdownToTipTapNode(node.text);
          case 'ContactNode':
            return {
              type: 'contactCard',
              attrs: {
                id: node.contact_id,
                firstName: node.attrs.first_name,
                lastName: node.attrs.last_name,
                email: node.attrs.email,
                phoneNo: node.attrs.phone_no,
                mobileNo: node.attrs.mobile_no,
                division: node.attrs.division,
                organization: node.attrs.organization,
              },
            };
          case 'DocumentNode':
            return {
              type: 'fileCard',
              attrs: {
                id: node.attrs.id,
                fileName: node.attrs.fileName,
                fileSize: node.attrs.fileSize,
                fileType: node.attrs.fileType,
              },
            };
          default:
            // Fallback to paragraph for unknown types
            return {
              type: 'paragraph',
              content: [
                {
                  type: 'text',
                  text: node.text || '',
                },
              ],
            };
        }
      });

      return {
        type: 'doc',
        content: content,
      };
    },

    /**
     * Parse markdown text and convert to TipTap node structure
     * @param {string} markdownText - The markdown text to parse
     * @returns {Object} TipTap node structure
     */
    parseMarkdownToTipTapNode(markdownText) {
      if (!markdownText) {
        return {
          type: 'paragraph',
          content: [],
        };
      }

      // Handle headings
      const headingMatch = markdownText.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        const level = headingMatch[1].length;
        const text = headingMatch[2];
        return {
          type: 'heading',
          attrs: { level },
          content: this.parseInlineMarkdown(text),
        };
      }

      // Handle blockquotes
      if (markdownText.startsWith('> ')) {
        const lines = markdownText.split('\n');
        const quotedText = lines
          .map((line) => line.replace(/^> /, ''))
          .join('\n');
        return {
          type: 'blockquote',
          content: [
            {
              type: 'paragraph',
              content: this.parseInlineMarkdown(quotedText),
            },
          ],
        };
      }

      // Handle code blocks
      const codeBlockMatch = markdownText.match(/^```(\w+)?\n([\s\S]*?)\n```$/);
      if (codeBlockMatch) {
        const language = codeBlockMatch[1] || '';
        const code = codeBlockMatch[2];
        return {
          type: 'codeBlock',
          attrs: { language },
          content: [
            {
              type: 'text',
              text: code,
            },
          ],
        };
      }

      // Handle bullet lists
      if (markdownText.startsWith('- ')) {
        const text = markdownText.replace(/^- /, '');
        return {
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: this.parseInlineMarkdown(text),
            },
          ],
        };
      }

      // Handle ordered lists
      const orderedListMatch = markdownText.match(/^(\d+)\.\s+(.+)$/);
      if (orderedListMatch) {
        const text = orderedListMatch[2];
        return {
          type: 'listItem',
          content: [
            {
              type: 'paragraph',
              content: this.parseInlineMarkdown(text),
            },
          ],
        };
      }

      // Default to paragraph
      return {
        type: 'paragraph',
        content: this.parseInlineMarkdown(markdownText),
      };
    },

    /**
     * Parse inline markdown formatting and convert to TipTap marks
     * @param {string} text - The text with inline markdown
     * @returns {Array} Array of TipTap text nodes with marks
     */
    parseInlineMarkdown(text) {
      if (!text) return [];

      // This is a simplified parser - in a real implementation, you'd want a more robust markdown parser
      const nodes = [];
      let remainingText = text;

      // Handle bold text (**text**)
      const boldRegex = /\*\*(.*?)\*\*/g;
      let lastIndex = 0;
      let match;

      while ((match = boldRegex.exec(remainingText)) !== null) {
        // Add text before the bold section
        if (match.index > lastIndex) {
          const beforeText = remainingText.slice(lastIndex, match.index);
          if (beforeText) {
            nodes.push({
              type: 'text',
              text: beforeText,
            });
          }
        }

        // Add the bold text
        nodes.push({
          type: 'text',
          text: match[1],
          marks: [{ type: 'bold' }],
        });

        lastIndex = match.index + match[0].length;
      }

      // Add remaining text
      if (lastIndex < remainingText.length) {
        const remaining = remainingText.slice(lastIndex);
        if (remaining) {
          nodes.push({
            type: 'text',
            text: remaining,
          });
        }
      }

      // If no formatting was found, return the text as is
      if (nodes.length === 0) {
        nodes.push({
          type: 'text',
          text: text,
        });
      }

      return nodes;
    },

    /**
     * Convert JSON structure to HTML for TipTap editor
     * @param {Object} tiptapJson - The TipTap JSON structure
     * @returns {string} HTML string ready for TipTap editor
     */
    convertJsonToHtml(tiptapJson) {
      if (!tiptapJson || !tiptapJson.content) {
        return '';
      }

      return this.convertNodeToHtml(tiptapJson);
    },

    /**
     * Convert a TipTap node to HTML
     * @param {Object} node - The TipTap node
     * @returns {string} HTML string
     */
    convertNodeToHtml(node) {
      if (!node) return '';

      switch (node.type) {
        case 'doc':
          if (node.content) {
            return node.content
              .map((child) => this.convertNodeToHtml(child))
              .join('');
          }
          return '';

        case 'paragraph':
          const paragraphContent = node.content
            ? node.content
                .map((child) => this.convertNodeToHtml(child))
                .join('')
            : '';
          return `<p>${paragraphContent}</p>`;

        case 'heading':
          const level = node.attrs?.level || 1;
          const headingContent = node.content
            ? node.content
                .map((child) => this.convertNodeToHtml(child))
                .join('')
            : '';
          return `<h${level}>${headingContent}</h${level}>`;

        case 'bulletList':
          const bulletContent = node.content
            ? node.content
                .map((child) => this.convertNodeToHtml(child))
                .join('')
            : '';
          return `<ul>${bulletContent}</ul>`;

        case 'orderedList':
          const orderedContent = node.content
            ? node.content
                .map((child) => this.convertNodeToHtml(child))
                .join('')
            : '';
          return `<ol>${orderedContent}</ol>`;

        case 'listItem':
          const listItemContent = node.content
            ? node.content
                .map((child) => this.convertNodeToHtml(child))
                .join('')
            : '';
          return `<li>${listItemContent}</li>`;

        case 'blockquote':
          const blockquoteContent = node.content
            ? node.content
                .map((child) => this.convertNodeToHtml(child))
                .join('')
            : '';
          return `<blockquote>${blockquoteContent}</blockquote>`;

        case 'codeBlock':
          const language = node.attrs?.language || '';
          const codeContent = node.content
            ? node.content
                .map((child) => this.convertNodeToHtml(child))
                .join('')
            : '';
          return `<pre><code class="language-${language}">${codeContent}</code></pre>`;

        case 'contactCard':
          const contactId = node.attrs?.id;
          return `<div data-type="contactCard" data-id="${contactId}">Contact Card (ID: ${contactId})</div>`;

        case 'fileCard':
          const fileId = node.attrs?.id;
          return `<div data-type="fileCard" data-id="${fileId}">File Card (ID: ${fileId})</div>`;

        case 'text':
          let text = node.text || '';

          // Apply marks
          if (node.marks) {
            node.marks.forEach((mark) => {
              switch (mark.type) {
                case 'bold':
                  text = `<strong>${text}</strong>`;
                  break;
                case 'italic':
                  text = `<em>${text}</em>`;
                  break;
                case 'code':
                  text = `<code>${text}</code>`;
                  break;
                case 'link':
                  const href = mark.attrs?.href || '#';
                  text = `<a href="${href}">${text}</a>`;
                  break;
                case 'strike':
                  text = `<s>${text}</s>`;
                  break;
                case 'underline':
                  text = `<u>${text}</u>`;
                  break;
              }
            });
          }

          return text;

        default:
          // For unknown node types, process children if they exist
          if (node.content) {
            return node.content
              .map((child) => this.convertNodeToHtml(child))
              .join('');
          }
          return '';
      }
    },
    /**
     * Remove contactCard and fileCard nodes from the content
     */
    removeContactCardAndFileCardNodes() {
      debugger;
      this.currentMessageJSON.content = this.currentMessageJSON.content.filter(
        (node) => node.type !== 'contactCard' && node.type !== 'fileCard'
      );
      this.setContent(this.currentMessageJSON);
    },
  });
});
