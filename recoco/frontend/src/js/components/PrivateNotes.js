import Alpine from '../utils/globals';
import { ToastType } from '../models/toastType';
import api, { documentsUrl, notesUrl } from '../utils/api';

Alpine.data('PrivateNotes', (projectId) => ({
  projectId,
  sendingNote: false,

  /**
   * Upload a file to the documents API
   * @param {File} file - The file to upload
   * @returns {Promise} - The API response
   */
  uploadFile(file) {
    const formData = new FormData();
    formData.append('the_file', file);
    return api.post(documentsUrl(this.projectId), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  /**
   * Send the private note with attached files and contacts
   */
  async sendNote() {
    if (!this.$store.editor.currentMessageJSON) return;
    if (this.sendingNote) return;

    this.sendingNote = true;

    try {
      const parsedNodesFromEditor = this.$store.editor.parseTipTapContent(
        this.$store.editor.currentMessageJSON
      );

      // Extract document nodes that need uploading (no document_id yet)
      const documentNodesToUpload = parsedNodesFromEditor.filter(
        (node) => node.type === 'DocumentNode' && !node.document_id && node.file
      );

      // Upload files and get their IDs
      let uploadResponses = [];
      if (documentNodesToUpload.length > 0) {
        try {
          uploadResponses = await Promise.all(
            documentNodesToUpload.map((node) => this.uploadFile(node.file))
          );
        } catch (error) {
          const errorMessage =
            error.response?.data?.the_file?.[0] ||
            "Contactez nous via le chat pour obtenir de l'aide.";
          this.$store.app.displayToastMessage({
            message: `Erreur lors de l'envoi d'un document : ${errorMessage}`,
            timeout: 5000,
            type: ToastType.error,
          });
          this.sendingNote = false;
          throw new Error('Failed to upload documents', { cause: error });
        }

        // Assign document IDs to the nodes
        documentNodesToUpload.forEach((node, index) => {
          node.document_id = uploadResponses[index].data.id;
        });
      }

      // Collect all document IDs (both newly uploaded and existing)
      const documentIds = parsedNodesFromEditor
        .filter((node) => node.type === 'DocumentNode' && node.document_id)
        .map((node) => node.document_id);

      // Extract markdown content
      const markdownNodes = parsedNodesFromEditor.filter(
        (node) => node.type === 'MarkdownNode'
      );
      const content = markdownNodes.map((node) => node.text).join('\n\n');

      // Extract contact ID (only first contact if multiple)
      const contactNode = parsedNodesFromEditor.find(
        (node) => node.type === 'ContactNode'
      );
      const contactId = contactNode?.contact_id || null;

      // Build payload
      const payload = {
        content: content,
        document_ids: documentIds,
      };

      if (contactId) {
        payload.contact = contactId;
      }

      // Send the note
      await api.post(notesUrl(this.projectId), payload);

      // Clear editor and reload page
      this.$store.editor.clearEditorContent();
      this.$store.app.displayToastMessage({
        message: 'Note enregistrée avec succès',
        timeout: 3000,
        type: ToastType.success,
      });

      // Reload page to show the new note
      setTimeout(() => {
        window.location.reload();
      }, 500);
    } catch (error) {
      this.sendingNote = false;
      if (!error.message?.includes('Failed to upload documents')) {
        this.$store.app.displayToastMessage({
          message: `Erreur lors de l'enregistrement de la note: ${error.message || 'Erreur inconnue'}`,
          timeout: 5000,
          type: ToastType.error,
        });
      }
      throw error;
    }
  },
}));
