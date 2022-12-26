import Alpine from 'alpinejs'

Alpine.store('boards', {
    STATUSES: {
        PROPOSED: 0,
        INPROGRESS: 1,
        BLOCKED: 2,
        DONE: 3,
        NOT_INTERESTED: 4,
        ALREADY_DONE: 5,
    },
    data: [],
    init() {
        console.log('board store init');
        this.data = [
            { status: this.STATUSES.PROPOSED, title: "Nouvelles ", color_class: "border-primary", color:"#0d6efd" },
            { status: this.STATUSES.INPROGRESS, title: "En cours", color_class: "border-secondary",color:"#6c757d" },
            { status: this.STATUSES.BLOCKED, title: "En attente", color_class: "border-warning",color:"#ffc107" },
            { status: [this.STATUSES.DONE, this.STATUSES.NOT_INTERESTED, this.STATUSES.ALREADY_DONE], title: "Archivées", color_class: "border-error", color:"#adb5bd" },
        ]
    }
})

export default Alpine.store('boards')


