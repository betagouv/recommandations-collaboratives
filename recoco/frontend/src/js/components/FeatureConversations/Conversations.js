import Alpine from '../../utils/globals';
import api, {
  conversationsMessagesUrl,
  conversationsActivitiesUrl,
  contactUrl,
  conversationsParticipantsUrl,
  conversationsMessageUrl,
  documentUrl,
  documentsUrl,
  editTaskUrl,
  markTaskNotificationAsVisited,
} from '../../utils/api';
import { trackOpenRessource } from '../../utils/trackingMatomo';
import { formatDateFrench } from '../../utils/date';

Alpine.data('Conversations', (projectId, currentUserId) => ({
  projectId,
  currentUserId,
  feed: {},
  messages: [],
  messagesLoaded: false,
  showMessages: false,
  tasks: [],
  users: [],
  messagesParticipants: [],
  documents: [],
  contacts: [],
  message: { the_file: '', text: '', contact: '' },
  countOf: {
    isLoaded: false,
    messages: 0,
    new_messages: 0,
    tasks: 0,
    contacts: 0,
    documents: 0,
  },
  isEditorFocused: false,
  isEditorInEditMode: false,
  isEditorInReplyMode: false,
  messageIdToEdit: null,
  oldMessageToEdit: null,
  messageIdToReply: null,
  lastMessageDate: null,
  elementToDelete: null,
  theFiles: [],
  formatDateFrench,
  editTaskUrl,
  async init() {
    this.getMessagesParticipants();
    await this.getActivities();
    await this.getMessages();
    this.createFullFeed();
    this.messagesLoaded = true;
    setTimeout(() => {
      this.showMessages = true;
    }, 500);
    this.$store.tasksData._subscribe(() => {
      this.tasks = this.$store.tasksData.tasks;
    });
    this.$store.tasksData._notify();
    this.countElementsInDiscussion();
  },
  getRecommendationById(id) {
    const foundRecommendation = this.tasks.find(
      (recommendation) => recommendation.id == id
    );
    return foundRecommendation;
  },
  getMessageById(id) {
    return this.feed.messages.find((message) => message.id === +id);
  },
  async getMessages() {
    try {
      const messages = await api.get(conversationsMessagesUrl(this.projectId));
      this.feed.messages = messages.data;
    } catch (error) {
      throw new Error('Failed to get messages');
    }
  },
  async getActivities() {
    try {
      const activities = await api.get(
        conversationsActivitiesUrl(this.projectId)
      );
      this.feed.activities = activities.data;
    } catch (error) {
      throw new Error('Failed to get activities');
    }
  },
  createFullFeed() {
    const messages = (this.feed.messages || []).map((m) =>
      m.type ? m : { ...m, type: 'message' }
    );

    const activities = (this.feed.activities || []).map((a) =>
      a.type ? a : { ...a, type: 'activity' }
    );

    this.feed.elements = [...messages, ...activities].sort((a, b) => {
      const ta = Date.parse(a.created ?? a.timestamp ?? 0);
      const tb = Date.parse(b.created ?? b.timestamp ?? 0);
      if (ta !== tb) return ta - tb;
      return 0;
    });
    let countOfUnread = 0;
    this.feed.elements.forEach((el) => {
      if (el.unread > 0 && !countOfUnread && !el.deleted) {
        el.firstUnread = true;
        countOfUnread++;
      }
    });
  },
  async getMessagesParticipants() {
    try {
      const participants = await api.get(
        conversationsParticipantsUrl(this.projectId)
      );
      this.messagesParticipants = [
        ...participants.data,
        ...this.$store.djangoData.recipients.map((recipient) => ({
          id: +recipient.id,
          first_name: recipient.first_name,
          last_name: recipient.last_name,
          email: recipient.email,
          phone_no: recipient.phone_no,
          last_login: {
            date: recipient.last_login,
          },
          is_active: recipient.is_active,
          profile: {
            organization_position: recipient.profile__organization_position,
            organization: {
              name: recipient.profile__organization__name,
            },
          },
        })),
      ];
    } catch (error) {
      throw new Error('Failed to get messages participants');
    }
  },
  async getShortMessageInReplyTo(id) {
    const shortMessage = this.getMessageById(id);
    if (!shortMessage) {
      return '';
    }
    let contentToSummarize;
    if (shortMessage.nodes[0].type === 'RecommendationNode') {
      const recommendationIdToSummarize =
        shortMessage.nodes[0].recommendation_id;
      const recommendationToSummarize = await this.getRecommendationById(
        recommendationIdToSummarize
      );
      if (!recommendationToSummarize) {
        return 'Recommandation supprimée';
      }
      contentToSummarize = `Recommandation - ${recommendationToSummarize.intent}`;
    } else if (shortMessage.nodes[0].type === 'ContactNode') {
      const contactIdToSummarize = shortMessage.nodes[0].contact_id;
      const contactToSummarize =
        await this.getContactById(contactIdToSummarize);
      contentToSummarize = `Contact - ${contactToSummarize.first_name} ${contactToSummarize.last_name}`;
    } else if (shortMessage.nodes[0].type === 'DocumentNode') {
      const documentIdToSummarize = shortMessage.nodes[0].document_id;
      const documentToSummarize = await this.getDocumentById(
        documentIdToSummarize
      );
      contentToSummarize = `Document - ${documentToSummarize.filename}`;
    } else {
      contentToSummarize = shortMessage.nodes[0].text;
    }
    contentToSummarize = contentToSummarize.replace(/\n/g, ' ');

    return `${contentToSummarize.slice(0, 120)}${contentToSummarize.length > 120 ? '...' : ''}`;
  },
  getUserById(id) {
    if (id === this.currentUserId) {
      return this.$store.djangoData.currentUser;
    }
    const foundUser = this.messagesParticipants.find((user) => user.id === +id);
    if (!foundUser) {
      /** MOCK DATA */
      const user = {};
      user.data = {
        id: +id,
        place: this.users.length,
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        phone_no: '0642424242',
        last_login: {
          date: '2021-01-01',
        },
        is_active: true,
        profile: {
          organization_position: 'Developer',
          organization: {
            name: 'Example Inc.',
          },
        },
      };
      return user.data;
    }
    return foundUser;
  },
  async getDocumentById(id) {
    const foundDocument = this.documents.find(
      (document) => document.id === +id
    );
    if (!foundDocument) {
      try {
        const document = await api.get(documentUrl(this.projectId, id));
        this.documents.push(document.data);
        return document.data;
      } catch (error) {
        return null;
      }
    }
    return foundDocument;
  },
  async getContactById(id) {
    const foundContact = this.contacts.find((contact) => contact.id === +id);
    if (!foundContact) {
      const contact = await api.get(contactUrl(id));
      this.contacts.push(contact.data);
      return contact.data;
    }
    return foundContact;
  },
  async sendFormMessage() {
    if (this.isEditorInEditMode) {
      await this.sendMessage({
        updateMessage: true,
        messageIdToEdit: this.messageIdToEdit,
      });
    } else {
      await this.sendMessage();
    }
  },
  uploadFile(file) {
    const formData = new FormData();
    formData.append('the_file', file);
    return api.post(documentsUrl(this.projectId), formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  async sendMessage({ updateMessage = false, messageIdToEdit = null } = {}) {
    if (this.$store.editor.currentMessageJSON) {
      let promises = [];
      const parsedNodesFromEditor = this.$store.editor.parseTipTapContent(
        this.$store.editor.currentMessageJSON
      );
      if (parsedNodesFromEditor.some((node) => node.type === 'DocumentNode')) {
        promises = parsedNodesFromEditor
          .filter((node) => node.type === 'DocumentNode')
          .map((node) => this.uploadFile(node.file));
      }

      try {
        const responseUploadFiles = await Promise.all(promises);
        parsedNodesFromEditor.forEach((node) => {
          if (node.type === 'DocumentNode') {
            node.document_id = responseUploadFiles.shift().data.id;
          }
        });
        const payload = {
          nodes: parsedNodesFromEditor,
          in_reply_to: this.messageIdToReply,
        };
        let messageResponse;
        if (updateMessage) {
          messageResponse = await api.patch(
            conversationsMessageUrl(this.projectId, messageIdToEdit),
            payload
          );
          this.updateCountOfElementsInDiscussion(this.oldMessageToEdit, true);
          this.replaceMessage(messageResponse.data, messageIdToEdit);
          this.oldMessageToEdit = null;
          this.messageIdToEdit = null;
          this.isEditorInEditMode = false;
        } else {
          messageResponse = await api.post(
            conversationsMessagesUrl(this.projectId),
            payload
          );
          this.feed.elements.push({ ...messageResponse.data, type: 'message' });
          this.isEditorInReplyMode = false;
          this.scrollToNewMessage();
        }
        this.$store.editor.clearEditorContent();
        this.updateCountOfElementsInDiscussion(messageResponse.data);
        this.messageIdToReply = null;
      } catch (error) {
        if (updateMessage) {
          throw new Error('Failed to send message', error);
        } else {
          throw new Error('Failed to update message', error);
        }
      }
    }
  },
  countElementsInDiscussion() {
    for (const message of this.feed.elements) {
      if (message.unread > 0 && !message.deleted) {
        this.countOf.new_messages += 1;
      }
      this.updateCountOfElementsInDiscussion(message);
    }
    this.countOf.isLoaded = true;
  },
  updateCountOfElementsInDiscussion(element, decrease = false) {
    if (element.nodes) {
      for (const node of element.nodes) {
        if (node.type === 'DocumentNode') {
          this.countOf.documents += decrease ? -1 : 1;
        }
        if (node.type === 'RecommendationNode') {
          this.countOf.tasks += decrease ? -1 : 1;
        }
        if (node.type === 'ContactNode') {
          this.countOf.contacts += decrease ? -1 : 1;
        }
      }
      if (!element.deleted) {
        this.countOf.messages += decrease ? -1 : 1;
      } else if (decrease) {
        this.countOf.messages += -1;
      }
    }
  },
  onClickHandleReply(message) {
    this.messageIdToReply = message.id;
    this.isEditorInReplyMode = true;
    Alpine.raw(this.$store.editor.editorInstance).commands.focus();
  },
  onClickCancelReply() {
    this.messageIdToReply = null;
    this.isEditorInReplyMode = false;
  },
  onClickHandleEdit(message) {
    this.oldMessageToEdit = { ...message };
    this.messageIdToReply = message.in_reply_to;
    this.messageIdToEdit = message.id;
    message.nodes.forEach((node) => {
      if (node.type === 'ContactNode') {
        const contact = this.contacts.find(
          (contact) => contact.id === node.contact_id
        );
        const {
          id,
          first_name,
          last_name,
          email,
          phone_no,
          mobile_no,
          division,
          organization,
        } = contact;
        node.attrs = {
          id,
          first_name,
          last_name,
          email,
          phone_no,
          mobile_no,
          division,
          organization,
        };
      }
      if (node.type === 'DocumentNode') {
        const document = this.documents.find(
          (document) => document.id === node.document_id
        );
        node.attrs = {
          id: document.id,
          fileName: document.filename,
        };
      }
    });
    const tiptapJson = this.$store.editor.convertNodesToTipTapJson(
      message.nodes
    );

    Alpine.raw(this.$store.editor.editorInstance).commands.setContent(
      tiptapJson
    );
    this.$store.editor.currentMessageJSON = tiptapJson;

    const { to } = Alpine.raw(this.$store.editor.editorInstance).state
      .selection;
    Alpine.raw(this.$store.editor.editorInstance)
      .chain()
      .focus()
      .setTextSelection(to)
      .insertContent('<br>')
      .run();
    this.toggleEditMode({ activateEditMode: true });
  },
  setElementToDelete(element) {
    this.elementToDelete = element;
  },
  onClickHandleDelete() {
    if (!this.elementToDelete) {
      return;
    }
    try {
      const messageEl = document.getElementById(
        `message-${this.elementToDelete.id}`
      );
      if (messageEl) {
        messageEl.classList.add('message-item--deleting');
      }
      api.delete(
        conversationsMessageUrl(this.projectId, this.elementToDelete.id)
      );
      setTimeout(() => {
        this.feed.elements = this.feed.elements.map((el) =>
          el.id === this.elementToDelete.id ? { ...el, deleted: true } : el
        );
        this.updateCountOfElementsInDiscussion(this.elementToDelete, true);
        this.elementToDelete = null;
      }, 200);
    } catch (error) {
      throw new Error('Failed to delete message', error);
    }
  },
  toggleEditMode({ activateEditMode = false }) {
    this.isEditorInEditMode = activateEditMode;

    if (!activateEditMode) {
      Alpine.raw(this.$store.editor.editorInstance).commands.clearContent();
    }
  },
  async onClickRessourceConsummeNotification(taskId) {
    try {
      if (!Alpine.store('djangoData').isAdvisor) {
        await api.post(markTaskNotificationAsVisited(this.projectId, taskId));
      }
    } catch (error) {
      throw new Error('Failed to mark task notification as visited', error);
    }
    trackOpenRessource();
  },
  replaceMessage(message, messageIdToEdit) {
    const messageIndex = this.feed.elements.findIndex(
      (message) => message.id === messageIdToEdit
    );
    this.feed.elements[messageIndex] = { ...message, type: 'message' };
  },
  // Simple ifchanged implementation
  shouldShowDate(element) {
    const dateString =
      element.type === 'message' ? element.created : element.timestamp;
    const dateToCompare = this.formatDateFrench(dateString);
    if (dateToCompare !== this.lastMessageDate) {
      this.lastMessageDate = dateToCompare;
      return true;
    }
    return false;
  },
  scrollToNewMessage() {
    requestAnimationFrame(() => {
      window.scroll({
        top: document.body.getBoundingClientRect().height,
        behavior: 'auto',
      });
    });
  },

  async goToCreateRecommendation(url) {
    if (this.$store.editor.currentMessageJSON) {
      const parsedNodesFromEditor = this.$store.editor.parseTipTapContent(
        this.$store.editor.currentMessageJSON
      );
      if (parsedNodesFromEditor.some((node) => node.type === 'DocumentNode')) {
        const documentNode = parsedNodesFromEditor.find(
          (node) => node.type === 'DocumentNode'
        );
        // connect to the database
        await this.$store.idbObjectStoreMgmt.init();
        const value = await this.$store.idbObjectStoreMgmt.add({
          file: documentNode.file,
        });
      }
    }

    window.location.href = url;
  },
}));
