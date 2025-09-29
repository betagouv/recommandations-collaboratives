import Alpine from '../utils/globals';

document.addEventListener('alpine:init', () => {
  Alpine.store('editor', {
    editorInstance: null,
    currentMessage: '',
    currentMessageJSON: '',
    isEditing: false,
    isSubmitted: false,
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
              id: node.attrs?.id || 42, // Fallback to fake ID as seen in FileCardExtension
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
  });
});
