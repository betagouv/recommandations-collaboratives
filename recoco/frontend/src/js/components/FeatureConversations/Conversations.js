import Alpine from '../../utils/globals';
import api, {
  conversationsMessagesUrl,
  contactUrl,
  conversationsParticipantsUrl,
  documentUrl,
} from '../../utils/api';

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
    messages: 0,
    new_messages: 0,
    tasks: 0,
    contacts: 0,
    documents: 0,
  },
  async init() {
    await this.getMessages();
    this.getMessagesParticipants();
    this.$store.tasksData._subscribe(() => {
      this.tasks = this.$store.tasksData.tasks;
    });
    this.countOf.messages = this.countMessagesInDiscussion();
    this.countOf.tasks = this.countTasksInDiscussion();
    this.countOf.contacts = this.countContactsInDiscussion();
    this.countOf.documents = this.countDocumentsInDiscussion();
    this.countOf.new_messages = this.countNewMessagesInDiscussion();
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
      console.log(this.feed.messages);
      this.messagesLoaded = true;
      setTimeout(() => {
        this.showMessages = true;
      }, 500);
    } catch (error) {
      throw new Error('Failed to get messages');
    }
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

  async sendMessage() {
    if (this.$store.editor.currentMessageJSON) {
      const parsedNodesFromEditor = this.$store.editor.parseTipTapContent(
        this.$store.editor.currentMessageJSON
      );
      console.log('Raw message:', { parsedNodesFromEditor });
      try {
        const payload = {
          nodes: parsedNodesFromEditor,
          posted_by: this.currentUserId,
          in_reply_to: null,
        };
        const messageResponse = await api.post(
          conversationsMessagesUrl(this.projectId),
          payload
        );
        this.feed.messages.push(messageResponse.data);
      } catch (error) {
        throw new Error('Failed to send message');
      }
    }
  },
  countDocumentsInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'DocumentNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countTasksInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'RecommendationNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countContactsInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'ContactNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countMessagesInDiscussion() {
    let count = 0;
    console.log(this.feed.messages);
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'MarkdownNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countNewMessagesInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      if (!message.read_by.includes(this.currentUserId)) {
        count += 1;
      }
    }
    return count;
  },
  countDocumentsInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'DocumentNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countTasksInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'RecommendationNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countContactsInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'ContactNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countMessagesInDiscussion() {
    let count = 0;
    console.log(this.feed.messages);
    for (const message of this.feed.messages) {
      for (const node of message.nodes) {
        if (node.type === 'MarkdownNode') {
          count += 1;
        }
      }
    }
    return count;
  },
  countNewMessagesInDiscussion() {
    let count = 0;
    for (const message of this.feed.messages) {
      if (!message.read_by.includes(this.currentUserId)) {
        count += 1;
      }
    }
    return count;
  },
}));
