function boardProjectsApp() {
    const options = {
        async getData() {
            const response = await fetch('/api/projects/');
            return response.json();
        },
        async onDrop(data, status, nextData) {
            await fetch(`/api/projects/${data.id}/`, {
                method: "PATCH",
                cache: "no-cache",
                mode: "same-origin",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": Cookies.get("csrftoken"),
                },
                body: JSON.stringify({ status: status })
            });
        },
        sortFn(a, b) {
            if (b.notifications.count - a.notifications.count)
                return b.notifications.count - a.notifications.count;
            else {
                return b.created_on - a.created_on;
            }
        },
        filterFn(d) {
            if (this.selectedDepartment && this.selectedDepartment !== "") {
                return d.commune && (d.commune.department.code == this.selectedDepartment)
            } else {
                return true
            }
        },
        postProcessData(data) {
            const departments = [];
            data.forEach(d => {
                if (d.commune != null) {
                    const dept = {
                        code: d.commune.department.code,
                        name: d.commune.department.name,
                    };
                    const index = departments.findIndex(obj => obj.code == dept.code);
                    if (index === -1) {
                        departments.push(dept);
                    }
                }
            });
            departments.sort((a, b) => a.name.localeCompare(b.name));
            this.departments = departments;
        }
    };

    const app = {
        selectedDepartment: null,
        departments: [],
        boards: [
            { code: 'TO_PROCESS', title: 'À traiter', color_class: 'border-secondary' },
            { code: 'READY', title: 'En attente', color_class: 'border-info' },
            { code: "IN_PROGRESS", title: "En cours", color_class: 'border-primary' },
            { code: "DONE", title: "Traité", color_class: 'border-success' },
            { code: "STUCK", title: "Conseil interrompu", color_class: 'border-dark' },
        ]
    };

    return configureBoardApp(app, options);
}
