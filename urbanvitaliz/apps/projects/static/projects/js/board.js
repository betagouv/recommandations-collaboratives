function configureBoardApp(app, options) {
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    const configuredApp = {
        data: [],
        isBusy: false,
        async getData() {
            this.isBusy = true;
            const json = await options.fetchData.call(this);
            const data = json.map(d => Object.assign(d, {
                uuid: generateUUID()
            }));

            options.postProcessData.call(this, data);

            this.isBusy = false;
            this.data = data;
        },
        get view() {
            return this.data.filter(options.filterFn.bind(this)).sort(options.sortFn.bind(this));
        },
        column(status) {
            return this.view.filter(d => d.status === status);
        },
        onDragStart(event, uuid) {
            this.dragCounter = 0;
            event.dataTransfer.setData('text/plain', uuid);
            event.dataTransfer.effectAllowed = "move";
            event.target.classList.add('drag-dragging');
        },
        onDragEnd(event) {
            event.target.classList.remove('drag-dragging');
            this.$nextTick(() => document.querySelectorAll(".drag-target").forEach(e => e.classList.remove("drag-target")));
        },
        onDragOver(event) {
            event.preventDefault();
            event.dropEffect = "move";
        },
        onDragEnter(event) {
            if (this.dragCounter <= 0) {
                event.currentTarget.classList.add('drag-target');
            }
            this.dragCounter += 1;
        },
        onDragLeave(event) {
            this.dragCounter -= 1;
            if (this.dragCounter <= 0) {
                event.currentTarget.classList.remove('drag-target');
            }
        },
        async onDrop(event, status, targetUuid) {
            this.$nextTick(() => document.querySelectorAll(".drag-target").forEach(e => e.classList.remove("drag-target")));
            const uuid = event.dataTransfer.getData("text/plain");
            event.dataTransfer.clearData();

            const data = this.data.find(d => d.uuid === uuid);
            const nextData = this.data.find(d => d.uuid === targetUuid);

            this.isBusy = true;
            await options.patchData.call(this, data, status, nextData);
            this.isBusy = false;

            await this.getData();
        }
    };

    return Object.assign(configuredApp, app);
}

function truncate(input, size = 30) {
    return input.length > size ? `${input.substring(0, size)}...` : input;
}

function formatDateDisplay(date) {
    return new Date(date).toLocaleDateString('fr-FR');
}

