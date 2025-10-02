import Alpine from '../../utils/globals';
import api, {
  conversationsMessagesUrl,
  conversationsActivitiesUrl,
  contactUrl,
  conversationsParticipantsUrl,
  conversationsMessageUrl,
  documentUrl,
} from '../../utils/api';
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
  messageIdToReply: null,
  lastMessageDate: null,
  formatDateFrench,
  async init() {
    await this.getActivities();
    await this.getMessages();
    this.createFullFeed();
    console.log('this.feed', this.feed);
    this.messagesLoaded = true;
    setTimeout(() => {
      this.showMessages = true;
    }, 500);
    this.getMessagesParticipants();
    this.$store.tasksData._subscribe(() => {
      console.log('tasksData', this.$store.tasksData.tasks);
      this.tasks = this.$store.tasksData.tasks;
    });
    this.$store.tasksData._notify();
    this.countElementsInDiscussion();
  },
  getRecommendationById(id) {
    console.log('getRecommendationById', id);
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
    // !!! MOCKED DATA !!!
    // !!! MOCKED DATA !!!
    this.feed.elements = this.feed.elements.map((el, index) => {
      if (index > this.feed.messages.length - 2) {
        return { ...el, read: false };
      } else {
        return { ...el, read: true };
      }
    });
    // !!! MOCKED DATA !!!
    // !!! MOCKED DATA !!!
    let countOfUnread = 0;
    this.feed.elements.forEach((el) => {
      if (!el.read && !countOfUnread) {
        el.firstUnread = true;
        countOfUnread++;
      }
    });
  },
  async getMessagesParticipants() {
    try {
      const messagesParticipants = await api.get(
        conversationsParticipantsUrl(this.projectId)
      );
      this.messagesParticipants = messagesParticipants.data;
    } catch (error) {
      throw new Error('Failed to get messages participants');
    }
  },
  getShortMessageInReplyTo(id) {
    const shortMessage = this.getMessageById(id);
    if (!shortMessage) {
      return '';
    }
    const markdownNode = shortMessage.nodes.find(
      (node) => node.type === 'MarkdownNode'
    );
    return `${markdownNode.text.slice(0, 40)}${markdownNode.text.length > 40 ? '...' : ''}`;
  },
  getUserById(id) {
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
      const document = await api.get(documentUrl(this.projectId, id));
      this.documents.push(document.data);
      return document.data;
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
  async sendFormMessage(message) {
    if (this.isEditorInEditMode) {
      await this.onSubmitUpdateMessage(message, this.messageIdToEdit);
    } else {
      await this.sendMessage();
    }
  },
  async sendMessage() {
    if (this.$store.editor.currentMessageJSON) {
      const parsedNodesFromEditor = this.$store.editor.parseTipTapContent(
        this.$store.editor.currentMessageJSON
      );
      try {
        const payload = {
          nodes: parsedNodesFromEditor,
          posted_by: this.currentUserId,
          in_reply_to: this.messageIdToReply,
        };
        const messageResponse = await api.post(
          conversationsMessagesUrl(this.projectId),
          payload
        );
        this.updateCountOfElementsInDiscussion(messageResponse.data);
        this.feed.elements.push({ ...messageResponse.data, type: 'message' });
        this.$store.editor.clearEditorContent();
        this.messageIdToReply = null;
        this.isEditorInReplyMode = false;
      } catch (error) {
        throw new Error('Failed to send message', error);
      }
    }
  },
  countElementsInDiscussion() {
    for (const message of this.feed.elements) {
      if (!message.read) {
        this.countOf.new_messages += 1;
      }
     this.updateCountOfElementsInDiscussion(message);
    }
    this.countOf.isLoaded = true;
  },
  updateCountOfElementsInDiscussion(element) {
    console.log('updateCountOfElementsInDiscussion', element);
    let sameNode = false;
    if (element.nodes) {
      for (const node of element.nodes) {
        if (node.type === 'DocumentNode') {
          this.countOf.documents += 1;
        }
        if (node.type === 'RecommendationNode') {
          this.countOf.tasks += 1;
        }
        if (node.type === 'ContactNode') {
          this.countOf.contacts += 1;
        }
        if (node.type === 'MarkdownNode' && !sameNode) {
          this.countOf.messages += 1;
          sameNode = true;
        }
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
    });
    const tiptapJson = this.$store.editor.convertNodesToTipTapJson(
      message.nodes
    );

    Alpine.raw(this.$store.editor.editorInstance).commands.setContent(
      tiptapJson
    );
    this.$store.editor.currentMessageJSON = tiptapJson;

    Alpine.raw(this.$store.editor.editorInstance).commands.focus();
    this.toggleEditMode({ activateEditMode: true });
  },
  onClickHandleDelete(message) {
    try {
      api.delete(conversationsMessageUrl(this.projectId, message.id));
      this.feed.elements = this.feed.elements.map((el) =>
        el.id === message.id ? { ...el, deleted: true } : el
      );
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
  async onSubmitUpdateMessage(message, messageIdToEdit) {
    console.log('onSubmitUpdateMessage', message);

    if (this.$store.editor.currentMessageJSON) {
      const parsedNodesFromEditor = this.$store.editor.parseTipTapContent(
        this.$store.editor.currentMessageJSON
      );
      try {
        const payload = {
          nodes: parsedNodesFromEditor,
          posted_by: this.currentUserId,
          in_reply_to: this.messageIdToReply,
        };
        const messageResponse = await api.patch(
          conversationsMessageUrl(this.projectId, messageIdToEdit),
          payload
        );
        this.replaceMessage(messageResponse.data, messageIdToEdit);
        this.messageIdToEdit = null;
        this.isEditorInEditMode = false;
        this.$store.editor.clearEditorContent();
      } catch (error) {
        throw new Error('Failed to update message', error);
      }
    }
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
}));
