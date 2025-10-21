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
  });
});

function getDjangoData(id) {
  const value = document.getElementById(id)?.innerHTML;
  if (value) {
    return JSON.parse(value);
  }
}

function getDjangoPermsData(id, perm) {
  if (id == 'manage_documents') {
    console.log('manage_documents', perm);
  }
  const userProjectPerms = document.getElementById(id)?.textContent;

  if (userProjectPerms) {
    return userProjectPerms.indexOf(perm) > -1;
  }
}
