import Alpine from "../utils/globals"

document.addEventListener('alpine:init', () => {
    Alpine.store('djangoData', {
        projectId: getDjangoData('djangoProjectId'),
        isAdvisor: getDjangoData('isSwitchtender'),
        userEmail: getDjangoData('userEmail'),
        canAdministrate: getDjangoData('canAdministrate'),
        canUseTasks: getDjangoPermsData('userProjectPerms', 'use_tasks'),
        canManageTasks: getDjangoPermsData('userProjectPerms', 'manage_tasks'),
    })
})

function getDjangoData(id) {
    const value = document.getElementById(id)?.innerHTML;

    if (value) {
        return JSON.parse(value)
    }
}

function getDjangoPermsData(id, perm) {
    const userProjectPerms = document.getElementById(id)?.textContent;

    if (userProjectPerms) {
        return (userProjectPerms.indexOf(perm) > -1)
    }
}
