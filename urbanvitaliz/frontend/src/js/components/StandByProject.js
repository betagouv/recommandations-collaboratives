import Alpine from 'alpinejs'

function StandByProject() {
    return {
        initStandByProjectConfirmationModal() {
            const element = document.getElementById("stand-by-project-confirmation-modal");
            this.StandByProjectConfirmationModal = new bootstrap.Modal(element);
        },
        openStandByProjectConfirmationModal() {
            this.StandByProjectConfirmationModal.show();
        },
    }
}

Alpine.data("StandByProject", StandByProject)
