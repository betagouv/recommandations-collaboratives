import Alpine from "alpinejs";

Alpine.data("Crm", Crm)

function Crm() {
    return {
        init() {
            const sidebar = this.$refs.sidebar;
            const sidebarHeight = sidebar.offsetHeight;
            const windowHeight = window.innerHeight;

            if (sidebarHeight > windowHeight) {
                sidebar.classList.remove('crm-sticky')
                sidebar.classList.add('crm-relative')
            }

        }
    }
}
