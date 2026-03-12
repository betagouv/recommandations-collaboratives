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
import '../components/User.js';

window.stringToColor = stringToColor;
window.gravatar_url = gravatar_url;
import { tiptapParserJSONToHTML } from '../utils/tiptapParser.js';

window.tiptapParserJSONToHTML = tiptapParserJSONToHTML;
window.renderMarkdown = renderMarkdown;

// File size formatter for shared contents panel
window.formatFileSize = function (bytes) {
  if (!bytes || bytes === 0) return '';
  const units = ['o', 'Ko', 'Mo', 'Go'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  return Math.round(bytes / Math.pow(1024, i)) + ' ' + units[i];
};
