function action_pusher_app() {
		return {
        isBusy: true,

        truncate(input, size=30) {
            return input.length > size ? `${input.substring(0, size)}...` : input
        },

				formatDateDisplay(date) {
					  if (this.dateDisplay === 'toDateString') return new Date(date).toDateString();
					  if (this.dateDisplay === 'toLocaleDateString') return new Date(date).toLocaleDateString('fr-FR');

					  return new Date().toLocaleDateString('fr-FR');
				},

				async getResources() {
            var tasksFromApi = [];

            this.isBusy = true;

            const response = await fetch('/api/resources/');
            tasksFromApi = await response.json(); //extract JSON from the http response

						this.tasks = [];

            tasksFromApi.forEach(t => {
                this.tasks.push(
							   {
                    uuid: this.generateUUID(),
								    id: t.id,
								    name: this.truncate(t.name),
								    status: t.status,
                    switchtenders: t.switchtenders,
                    is_switchtender: t.is_switchtender,
								    boardCode: t.status,
								    created_on: new Date(t.created_on),
                    organization: this.truncate(t.org_name),
                    commune: t.commune,
                    notifications: t.notifications
							   });
						});

            this.tasks.sort(function(a, b) {
                if (b.notifications.count - a.notifications.count)
                    return (b.notifications.count - a.notifications.count);
                else {
                    return b.created_on - a.created_on;
                }
            });

            this.isBusy = false;
				}
		}
};
