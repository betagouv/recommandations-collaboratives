function boardTasksApp(projectId) {
  const options = {
    async fetchData() {
      const response = await fetch(`/api/projects/${projectId}/tasks`);
      return response.json();
    },
    async patchData(data, status, nextData) {
      await fetch(`/api/projects/${projectId}/tasks/${data.id}/`, {
        method: "PATCH",
        cache: "no-cache",
        mode: "same-origin",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify({ status }),
      });

      if (nextData) {
        await fetch(`/api/projects/${projectId}/tasks/${data.id}/move/`, {
          method: "POST",
          cache: "no-cache",
          mode: "same-origin",
          credentials: "same-origin",
          headers: {
            "X-CSRFToken": Cookies.get("csrftoken"),
          },
          body: new URLSearchParams(`above=${nextData.id}`),
        });
      }
    },
    sortFn(a, b) {
      return a.order - b.order;
    },
    filterFn(d) {
      return true;
    },
    postProcessData(data) {},
  };

  const app = {
    boards: [
      { status: 0, title: "Nouvelles ", color_class: "border-primary" },
      { status: 1, title: "En cours", color_class: "border-secondary" },
      { status: 2, title: "En attente", color_class: "border-warning" },
      { status: 3, title: "Archivées", color_class: "border-error" },
    ],
    currentTaskId: null,
    currentReminderTaskId: null,
    notifications: [],
    isSwitchtender: false,
    loadNotifications() {
      const notificationData = document.getElementById("notificationData").textContent;
      this.notifications = JSON.parse(notificationData);
    },
    loadSwitchtender() {
      const switchtenderData = document.getElementById("switchtenderData").textContent;
      this.isSwitchtender = JSON.parse(switchtenderData);     
    },
    initPreviewModal() {
      const element = document.getElementById("task-preview");
      this.previewModalHandle = new bootstrap.Modal(element);
      element.addEventListener("shown.bs.modal", () => {
        this.scrollToLastElement();
      });
    },
    initReminderModal() {
      const element = document.getElementById("reminder-modal");
      this.reminderModalHandle = new bootstrap.Modal(element);
    },
    initTooltips() {
      new bootstrap.Tooltip(this.$el, { 
        selector: "[data-bs-toggle='tooltip']"
      })
    },
    async onPreviewClick(id) {
      this.currentTaskId = id;
      this.previewModalHandle.show();

      await fetch(`/api/projects/${projectId}/tasks/${id}/`, {
        method: "PATCH",
        cache: "no-cache",
        mode: "same-origin",
        credentials: "same-origin",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: JSON.stringify({ visited: true }),
      });

      await this.getData();
    },
    onReminderClick(id) {
      this.currentReminderTaskId = id;
      this.reminderModalHandle.show();
    },
    pendingComment: "",
    async onSubmitComment() {
      await fetch(sendCommentUrl(this.currentTask.id), {
        method: "POST",
        cache: "no-cache",
        mode: "same-origin",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": Cookies.get("csrftoken"),
        },
        body: new URLSearchParams({ comment: this.pendingComment }),
      });
      this.pendingComment = "";
      await this.getData();
    },
    scrollToLastElement() {
      const nodes = this.$root.querySelectorAll(".message");
      if (nodes.length > 0) {
        this.$nextTick(() => {
          nodes[nodes.length - 1].scrollIntoView();
        });
      }
    },
    pendingReminderDate: formatReminderDate(daysFromNow(15)),
    onSubmitReminder() {
      const form = this.$refs.reminderForm;
      const dateInput = form.querySelector('#reminder-date');
      const daysInput = form.querySelector('#reminder-days');
      daysInput.value = Math.ceil((new Date(dateInput.value) - new Date())  / 86400000);
      form.submit();
    },
    updatePendingReminderDate(days) {
      this.pendingReminderDate = formatReminderDate(daysFromNow(days));
    }
  };

  return configureBoardApp(app, options);
}

function resourcePreviewUrl(resourceId) {
  return `/ressource/${resourceId}/embed`;
}

function editTaskUrl(taskId) {
  return `/task/${taskId}/update/`;
}

function deleteTaskReminderUrl(taskId) {
  return `/task/${taskId}/remind-delete/`;
}

function sendCommentUrl(taskId) {
  return `/task/${taskId}/followup/`;
}

function editReminderUrl(taskId) {
  return `/task/${taskId}/remind/`;
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleString();
}

function renderMarkdown(content) {
  return marked.parse(content);
}

function daysFromNow(days) {
  return new Date((new Date()).getTime() + (days * 86400000 /* seconds in a day */))
}

function formatReminderDate(date) {
  return date.toISOString().substring(0, 10);
}

function reminderTooltip(task) {
  if (task.reminders.length > 0) {
    const reminder = task.reminders[0];
    return `Rappel pour ${reminder.recipient} prévu le ${reminder.deadline}`
  } else {
    return "Aucun rappel prévu"
  }
}

function generateGravatarUrl(person, size=50) {
  const hash = md5(person.email);
  let name = `${person.first_name}+${person.last_name}`;
  if (name.trim() === "+") name = "Inconnu";
  const  encoded_fallback_uri = encodeURIComponent(`https://ui-avatars.com/api/${name}/${size}`);
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${encoded_fallback_uri}`
}
