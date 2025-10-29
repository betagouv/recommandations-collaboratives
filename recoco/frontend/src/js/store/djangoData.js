import Alpine from '../utils/globals';

document.addEventListener('alpine:init', () => {
  Alpine.store('djangoData', {
    projectId: getDjangoData('djangoProjectId'),
    isAdvisor:
      getDjangoData('isSwitchtender') ||
      getDjangoData('isObserverOnProject') ||
      getDjangoData('isAdvisorOnProject'),
    userEmail: getDjangoData('userEmail'),
    canAdministrate: getDjangoData('canAdministrate'),
    canManageDocuments: getDjangoPermsData(
      'userProjectPerms',
      'manage_documents'
    ),
    canUseTasks: getDjangoPermsData('userProjectPerms', 'use_tasks'),
    canManageTasks: getDjangoPermsData('userProjectPerms', 'manage_tasks'),
    isProjectOwner: getDjangoData('isProjectOwner'),
    currentUser: {
      id: getDjangoData('djangoCurrentUserId'),
      first_name: getDjangoData('djangoCurrentUserFirstName'),
      last_name: getDjangoData('djangoCurrentUserLastName'),
      email: getDjangoData('djangoCurrentUserEmail'),
      is_active: true,
      profile: {
        organization_position: getDjangoData(
          'djangoCurrentUserOrganizationPosition'
        ),
        organization: {
          name: getDjangoData('djangoCurrentUserOrganizationName'),
        },
      },
    },
  });
});

function getDjangoData(id) {
  const value = document.getElementById(id)?.innerHTML;
  if (value) {
    return JSON.parse(value);
  }
}

function getDjangoPermsData(id, perm) {
  const userProjectPerms = document.getElementById(id)?.textContent;

  if (userProjectPerms) {
    return userProjectPerms.indexOf(perm) > -1;
  }
}
