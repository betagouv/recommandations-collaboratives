import '../store/tasks.js';
import '../store/tasksData.js';

import '../utils/htmx.js';

import '../components/Task.js';
import '../components/TaskModal.js';
import '../components/TaskStatus.js';
import '../components/TaskStatusSwitcherConversations.js';
import '../components/NotificationEater.js';
import '../components/ConversationTopicSwitch.js';

import { tiptapParserJSONToHTML } from '../utils/tiptapParser.js';

window.tiptapParserJSONToHTML = tiptapParserJSONToHTML;
