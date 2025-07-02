import '../store/tasks.js';
import '../store/tasksData.js';

import '../utils/htmx.js';

import '../components/Task.js';
import '../components/TaskModal.js';
import '../components/TaskStatus.js';
import '../components/TaskStatusSwitcherConversations.js';
import '../components/NotificationEater.js';
import '../components/ConversationTopicSwitch.js';
import { generateHTML } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import { ContactCardExtension } from '../components/ContactCardExtension';
import { FileCardExtension } from '../components/FileCardExtension';

window.generateHTML = generateHTML;
window.StarterKit = StarterKit;
window.ContactCardExtension = ContactCardExtension;
window.FileCardExtension = FileCardExtension;
