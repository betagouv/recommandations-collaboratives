function boardTasksApp(projectId) {
    const testData = {
        id: 1,
        intent: "Ressource 2",
        content: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu ullamcorper tellus, eu iaculis dui. Integer malesuada mi sit amet feugiat finibus. Integer fringilla nunc in lorem interdum, at consectetur turpis mattis. Vestibulum sollicitudin convallis turpis non fermentum. Ut sit amet fermentum neque. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Maecenas quis nisl mi.",

        created_by: {
            email: "kalfane.rahman@gmail.com",
            fisrt_name: "Rahman",
            last_name: "Kalfane",
            org_name: "UrbanVitaliz"
        },

        deadline: new Date(),

        resource_id: 2,

        public: true,
        status: 0,
        visited: true,
        priority: 0,

        created_on: new Date(),
        updated_on: new Date(),

        reminders: [
            {
                deadline: new Date(),
                recipient: "kalfane.rahman@gmail.com"
            }
        ],

        followups: [
            {
                who: {
                    email: "kalfane.rahman@gmail.com",
                    first_name: "Rahman",
                    last_name: "Kalfane",
                    org_name: "UrbanVitaliz"
                },
                comment: "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc eu ullamcorper tellus, eu iaculis dui. Integer malesuada mi sit amet feugiat finibus. Integer fringilla nunc in lorem interdum, at consectetur turpis mattis. Vestibulum sollicitudin convallis turpis non fermentum. Ut sit amet fermentum neque. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Maecenas quis nisl mi.",
                timestamp: new Date()
            }
        ]
    }

    const db = Array(10).fill().map((_, i) => Object.assign({}, testData, { id: i, intent: `Ressource ${i}`, priority: i }));

    const options = {
        async fetchData() {
            return db
        },
        async patchData(data, status, nextData) {
            const patch = { status };
            if (nextData) {
                patch.priority = nextData.priority + 1;
            }
            const index = db.findIndex(d => d.uuid == data.uuid);
            db[index] = Object.assign(db[index], patch);
        },
        sortFn(a, b) {
            return b.priority - a.priority;
        },
        filterFn(d) {
            return true;
        },
        postProcessData(data) { }
    };

    const app = {
        boards: [
            { status: 0, title: "Nouvelles ", color_class: 'border-primary' },
            { status: 1, title: "En cours", color_class: 'border-secondary' },
            { status: 2, title: "En attente", color_class: 'border-warning' },
            { status: 3, title: "Archivées", color_class: 'border-error' }
        ],
        getTask(uuid) {
            const datum = this.data.find(d => d.uuid === uuid);
            return this.data.find(d => d.uuid === uuid);
        },
        currentTask: null,
        modalHandle: new bootstrap.Modal(document.getElementById("task-preview")),
        onPreviewClick(event, uuid) {
            this.currentTask = this.getTask(uuid);
            console.log(this.currentTask);
            this.$nextTick(() => this.modalHandle.show());
        }
    };

    return configureBoardApp(app, options);
}

function resourcePreviewUrl(id) {
    return `/ressource/${id}`;
}