import Alpine from "alpinejs";

Alpine.data("Crm", Crm)

function Crm() {
    return {
        noteIsOpen: false,
        init() {
            // Sidebar behaviour
            const sidebar = this.$refs.sidebar;
            const sidebarHeight = sidebar.offsetHeight;
            const windowHeight = window.innerHeight;

            if (sidebarHeight > windowHeight) {
                sidebar.classList.remove('crm-sticky')
                sidebar.classList.add('crm-relative')
            }

            // Note behavior
            const note = this.$refs.note;
            const noteToggleButton = this.$refs.noteToggleButton
            if (note.offsetHeight < 200) {
                note.classList.add('is-small')
                console.log(noteToggleButton.classList.add('hidden'));
            }
        },
    }
}
