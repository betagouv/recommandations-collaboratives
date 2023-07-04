import Alpine from "../utils/globals"

document.addEventListener('alpine:init', () => {
    Alpine.store('djangoData', {
        projectId: getDjangoData('djangoProjectId'),
    })
})

function getDjangoData(id) {
    return document.getElementById(id)?.innerHTML
}
