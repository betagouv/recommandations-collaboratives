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

export function statusToColor(status) {

    if (!STATUSES[status]) return '#ffffff'

    return STATUSES[status].color
}

export function statusToColorClass(status) {

    if (!STATUSES[status]) return "bg-white"

    return STATUSES[status].colorClass
}

export function statusToText(status) {

    if (!STATUSES[status]) return "unknown"

    return STATUSES[status].title
}
