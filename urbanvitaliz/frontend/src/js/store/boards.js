import Alpine from 'alpinejs'

Alpine.store('boards', {
    data: [
        { status: STATUSES.PROPOSED, title: "Nouvelles ", color_class: "border-primary" },
        { status: STATUSES.INPROGRESS, title: "En cours", color_class: "border-secondary" },
        { status: STATUSES.BLOCKED, title: "En attente", color_class: "border-warning" },
        { status: [STATUSES.DONE, STATUSES.NOT_INTERESTED, STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error" },
    ],
})

export default Alpine.store('boards')


