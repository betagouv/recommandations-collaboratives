import axios from 'axios';
import Cookies from 'js-cookie';

import appStore from '../store/app';

const instance = axios.create({
  cache: 'no-cache',
  mode: 'same-origin',
  credentials: 'same-origin',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': Cookies.get('csrftoken'),
  },
});

instance.interceptors.request.use(
  function (config) {
    appStore.isLoading = true;
    return config;
  },
  function (error) {
    appStore.isLoading = false;
    return Promise.reject(error);
  }
);

instance.interceptors.response.use(
  (response) => {
    appStore.isLoading = false;
    return response;
  },
  (error) => {
    appStore.isLoading = false;
    return Promise.reject(error);
  }
);

export default instance;

export function projectsUrl({
  searchText = '',
  departments = [],
  lastActivity = 1460,
  limit = 2000,
  offset = 0,
  page = 1,
  status = [
    'PRE_DRAFT',
    'DRAFT',
    'TO_PROCESS',
    'STUCK',
    'READY',
    'IN_PROGRESS',
    'DONE',
    'REJECTED',
  ],
} = {}) {
  // if search with tags, make a different url
  let url;
  if (searchText.includes('#')) {
    searchText = searchText.substring(1);
  }
  const params = new URLSearchParams({
    search: searchText,
    last_activity: lastActivity,
    limit,
    offset,
    page,
  });

  url = '/api/projects/?' + params.toString();

  if (departments.length) {
    departments = departments.map((code) => `departments=${code}`).join('&');
    url = url + '&' + departments;
  }
  if (status.length) {
    status = status.map((status) => `status=${status}`).join('&');
    url = url + '&' + status;
  }
  return url;
}

export function projectUrl(projectId) {
  return `/api/projects/${projectId}/`;
}

export function projectsProjectSitesUrl() {
  return '/api/projects/projectsites/';
}

export function userProjectStatusUrl() {
  return '/api/userprojectstatus/';
}

// Sites :
export function sitesConfigUrl() {
  return '/api/sites/';
}

// Organization
export function searchOrganizationsUrl(search) {
  return `/api/addressbook/organizations/?search=${search}`;
}

export function getOrganizationById(id) {
  return `/api/addressbook/organizations/${id}/`;
}

export function organizationsUrl() {
  return `/api/addressbook/organizations/`;
}

// Organization Group
export function searchOrganizationGroupsUrl(search) {
  return `/api/addressbook/organizationgroups/?search=${search}`;
}
export function organizationGroupsUrl() {
  return `/api/addressbook/organizationgroups/`;
}
// department
export function departmentsUrl() {
  return `/api/departments/`;
}
// Contacts
export function searchContactsUrl(
  search,
  orgaFirstLetter,
  departments = [],
  limit = 500
) {
  let url;
  const params = new URLSearchParams({ search, limit });
  if (orgaFirstLetter) {
    params.append('orga-startswith', orgaFirstLetter);
  }
  url = `/api/addressbook/contacts/?${params}`;
  if (departments.length) {
    departments = departments.map((code) => `departments=${code}`).join('&');
    url = url + '&' + departments;
  }
  return url;
}

export function contactsUrl(limit = 500) {
  if (limit) {
    const params = new URLSearchParams({
      limit: limit,
    });
    return `/api/addressbook/contacts/?${params}`;
  }
  return `/api/addressbook/contacts/`;
}

export function contactUrl(contactId) {
  return `/api/addressbook/contacts/${contactId}/`;
}

// Topic
export function searchTopicsUrl(search, restrict_to) {
  return `/api/topics/?search=${search}&restrict_to=${restrict_to}`;
}

// Tasks :
export function taskUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/`;
}

export function tasksUrl(projectId) {
  return `/api/projects/${projectId}/tasks/`;
}
/**
 * Params:
 * - projectId
 * - taskId
 * Payload:
 * - "above"/"below" with the id of the task to move above/below
 * - "top"/"bottom" set to true to move the task to the top/bottom of the list
 */
export function moveTaskUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/move/`;
}

export function taskNotificationsUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/notifications/`;
}

export function markTaskNotificationsAsReadUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/notifications/mark_all_as_read/`;
}

export function markTaskNotificationAsVisited(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/mark_visited/`;
}

export function notificationsMarkAsReadByIdUrl(notificationId) {
  return `/api/notifications/mark-one-as-read/${notificationId}/`;
}

export function markAllNotificationsAsReadUrl() {
  return '/api/notifications/mark-all-as-read';
}

export function followupsUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/followups/`;
}

export function followupUrl(projectId, taskId, followupId) {
  return `/api/projects/${projectId}/tasks/${taskId}/followups/${followupId}/`;
}

// Resources :
export function resourcePreviewUrl(resourceId, taskId) {
  if (taskId) {
    return `/ressource/${resourceId}/embed?task_id=${taskId}`;
  }
  return `/ressource/${resourceId}/embed/`;
}

export function resourcesUrl({
  search = '',
  category = [],
  status = [],
  limit = 50,
  offset = 0,
} = {}) {
  const params = new URLSearchParams();
  if (search) params.set('search', search);
  if (limit) params.set('limit', limit);
  if (offset) params.set('offset', offset);
  // category is multi-value: ?category=1&category=2
  if (category) {
    category.forEach((c) => {
      params.append('category', c);
    });
  }
  // status is multi-value: ?status=0&status=2
  if (status) {
    status.forEach((s) => {
      params.append('status', s);
    });
  }
  const paramStr = params.toString();
  let url = '/api/resources/';
  if (paramStr) url += '?' + paramStr;
  console.log(url);
  return url;
}

export function postExternalRessourceUrl() {
  return `/api/resources/import_from_uri/`;
}

// Regions :
export function regionsUrl() {
  return `/api/regions/`;
}

// Communes :
export function communesUrl() {
  return `/api/communes/`;
}

// Challenges
export function challengeUrl(code) {
  return `/api/challenges/${code}/`;
}

// Challenges Definitions
export function challengeDefinitionUrl(code) {
  return `/api/challenges/definitions/${code}`;
}

// Hitcount
export function hitcountUrl() {
  return '/hit/';
}

// Non API routes
// TODO : Make them into proper endpoints
export function editTaskUrl(taskId, next = null) {
  return next
    ? `/task/${taskId}/update/?next=${next}`
    : `/task/${taskId}/update/`;
}

export function deleteTaskUrl(taskId) {
  return `/task/${taskId}/delete/`;
}

export function deleteTaskReminderUrl(taskId) {
  return `/task/${taskId}/remind-delete/`;
}

export function editReminderUrl(taskId) {
  return `/task/${taskId}/remind/`;
}

// Conversations
export function conversationsMessagesUrl(projectId) {
  return `/api/projects/${projectId}/conversations/messages/`;
}

export function conversationsMessageUrl(projectId, messageId) {
  return `/api/projects/${projectId}/conversations/messages/${messageId}/`;
}

export function conversationsActivitiesUrl(projectId) {
  return `/api/projects/${projectId}/conversations/activities/`;
}

export function conversationsParticipantsUrl(projectId) {
  return `/api/projects/${projectId}/conversations/participants/`;
}

export function conversationsMessageMarkAsReadUrl(projectId, messageId) {
  return `/api/projects/${projectId}/conversations/messages/${messageId}/mark_as_read/`;
}

// Documents
export function documentsUrl(projectId) {
  return `/api/projects/${projectId}/documents/`;
}
export function documentUrl(projectId, documentId) {
  return `/api/projects/${projectId}/documents/${documentId}/`;
}
