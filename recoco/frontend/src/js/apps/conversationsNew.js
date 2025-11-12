import '../store/tasksData.js';
import '../store/tasks.js';
import '../store/idbObjectStoreMgmt.js';

import '../utils/htmx.js';
import { renderMarkdown } from '../utils/markdown.js';

import '../components/Task.js';
import '../components/TaskModal.js';
import '../components/TaskStatus.js';
import '../components/TaskStatusSwitcherConversations.js';
import '../components/NotificationEater.js';
// import '../components/ConversationTopicSwitch.js';
import '../components/FeatureConversations/Conversations.js';

import { tiptapParserJSONToHTML } from '../utils/tiptapParser.js';

window.tiptapParserJSONToHTML = tiptapParserJSONToHTML;
window.renderMarkdown = renderMarkdown;
