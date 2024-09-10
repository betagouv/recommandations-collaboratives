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

// Projects :
export function projectsUrl() {
  return '/api/projects/';
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
  return `/api/organizations/?search=${search}`;
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

export function resourcePreviewUrl(resourceId, taskId) {
  if (taskId) {
    return `/ressource/${resourceId}/embed?task_id=${taskId}`;
  }
  return `/ressource/${resourceId}/embed/`;
}

// Regions :
export function regionsUrl() {
  return `/api/regions/`;
}

// Challenges
export function challengeUrl(code) {
  return `/api/challenges/${code}/`;
}

// Challenges Definitions
export function challengeDefinitionUrl(code) {
  return `/api/challenges/definitions/${code}`;
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
