const STATUSES = {
    TO_PROCESS: {
        title: 'A traiter',
        color: "#6c757d",
        colorClass: 'bg-secondary',
    },
    QUESTIONS: {
        title: 'En attente',
        color: "#ffc107",
        colorClass: 'bg-warning',
    },
    READY: {
        title: 'Prêt à aiguiller',
        color: "#0dcaf0",
        colorClass: 'bg-info',
    },
    IN_PROGRESS: {
        title: 'Recommandations en cours',
        color: "#0d6efd",
        colorClass: 'bg-primary',
    },
    REVIEW_REQUEST: {
        title: 'Demande de relecture',
        color: "#ffc107",
        colorClass: 'bg-warning',
    },
    DONE: {
        title: 'Aiguillage terminé',
        color: "#198754",
        colorClass: 'bg-success',
    },
    STUCK: {
        title: 'En Attente/Bloqué',
        color: "#212529",
        colorClass: 'bg-dark',
    }
}

// { code: 'TO_PROCESS', title: 'A traiter', color_class: 'border-secondary' },
// { code: 'QUESTIONS', title: 'En attente', color_class: 'border-warning' },
// { code: 'READY', title: 'Prêt à aiguiller', color_class: 'border-info' },
// { code: "IN_PROGRESS", title: "Recommandations en cours", color_class: 'border-primary' },
// { code: "REVIEW_REQUEST", title: "Demande de relecture", color_class: 'border-warning' },
// { code: "DONE", title: "Aiguillage terminé", color_class: 'border-success' },
// { code: "STUCK", title: "En Attente/Bloqué", color_class: 'border-dark' },

export function statusToColor(status) {

    if (!STATUSES[status]) return

    return STATUSES[status].color
}

export function statusToColorClass(status) {

    if (!STATUSES[status]) return

    return STATUSES[status].colorClass
}

export function statusToText(status) {

    if (!STATUSES[status]) return

    return STATUSES[status].title
}
