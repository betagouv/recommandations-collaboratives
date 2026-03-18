import '../store/tasksData.js';
import '../store/tasks.js';
import '../store/idbObjectStoreMgmt.js';
import '../store/editor.js'
import '../store/resourcePreviewPanel.js';
import '../store/sharedContentsPanel.js';

import { renderMarkdown } from '../utils/markdown.js';
import { stringToColor } from '../utils/stringToColor.js';
import { gravatar_url } from '../utils/gravatar.js';

import '../components/Task.js';
import '../components/TaskModal.js';
import '../components/TaskStatus.js';
import '../components/TaskStatusSwitcherConversations.js';
import '../components/NotificationEater.js';
import '../components/FeatureConversations/Conversations.js';
import '../components/SharedContentsFileCard.js';
import '../components/User.js';

window.stringToColor = stringToColor;
window.gravatar_url = gravatar_url;
import { tiptapParserJSONToHTML } from '../utils/tiptapParser.js';

window.tiptapParserJSONToHTML = tiptapParserJSONToHTML;
window.renderMarkdown = renderMarkdown;
