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
// export function searchProjectUrl(search, departments) {
//   if (search) {
//     search = `search=${search}`;
//   }
//   if (departments.length) {
//     departments = departments.map((code) => `departments=${code}`).join('&');
//   }
//   return `/api/projects/?${search}${search && departments.length > 0 ? '&' : ''}${departments}`;
// }

// export function projectsMyDepartmentsUrl() {
//   return '/api/projects/my_departments';
// }

export function projectsUrl(search, departments, lastActivity) {
  // if search with tags, make a different url
  let url;
  if (search.includes('#')) {
    search = search.substring(1);
  }
  //   search.paragraph.replace(' ', '_');
  //   url = '/api/projects/?tags=' + search.substring(1);
  //   console.log(url);
  // } else {
  const params = new URLSearchParams({
    search: search,
    last_activity: lastActivity,
  });

  url = '/api/projects/?' + params.toString();

  if (departments.length) {
    departments = departments.map((code) => `departments=${code}`).join('&');
    url = url + '&' + departments;
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

export function postExternalRessourceUrl() {
  return `/api/resources/import_from_uri/`;
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
