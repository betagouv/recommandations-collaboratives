function boardTasksApp(projectId) {
  const moveTask = async (taskId, nextTaskId) => {
    await fetch(moveTaskUrl(projectId, taskId), {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      credentials: "same-origin",
      headers: {
        "X-CSRFToken": Cookies.get("csrftoken"),
      },
      body: new URLSearchParams(`above=${nextTaskId}`),
    });
  }

  const issueFollowup = async (task, status, comment = "") => {
    const body = { comment, status }
    if (task.status !== status) { body.status = status }

    if (body.status === task.status && body.comment === "") return;

    const response = await fetch(followupsUrl(projectId, task.id), {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": Cookies.get("csrftoken"),
      },
      body: JSON.stringify(body),
    });
  }

  const editComment = async (taskId, followupId, comment) => {
    const response = await fetch(followupUrl(projectId, taskId, followupId), {
      method: "PATCH",
      cache: "no-cache",
      mode: "same-origin",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": Cookies.get("csrftoken"),
      },
      body: JSON.stringify({ comment }),
    });
  }

  const patchTask = async (taskId, patch) => {
    const response = await fetch(taskUrl(projectId, taskId), {
      method: "PATCH",
      cache: "no-cache",
      mode: "same-origin",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": Cookies.get("csrftoken"),
      },
      body: JSON.stringify(patch),
    });
  }

  const markAllAsRead = async (taskId) => {
    const response = await fetch(markTaskNotificationsAsReadUrl(projectId, taskId), {
      method: "POST",
      cache: "no-cache",
      mode: "same-origin",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": Cookies.get("csrftoken"),
      },
      body: JSON.stringify({}),
    });
  }

  const options = {
    async getData() {
      const response = await fetch(tasksUrl(projectId));
      return response.json();
    },
    async onDrop(task, status, nextTask) {
      if ([0, 1, 2].indexOf(status) !== -1) {
        await issueFollowup(task, status);
        if (nextTask) await moveTask(task.id, nextTask.id);
      } else {
        this.openFeedbackModal(task);
      }
    },
    sortFn(a, b) {
      return a.order - b.order;
    },
    filterFn(d) {
      return this.isSwitchtender || d.public;
    },
    postProcessData(data) {
      console.log(data);
    },
  };

  const app = {
    // Boards
    boards: [
      { status: 0, title: "Nouvelles ", color_class: "border-primary" },
      { status: 1, title: "En cours", color_class: "border-secondary" },
      { status: 2, title: "En attente", color_class: "border-warning" },
      { status: [3, 4, 5], title: "Archivées", color_class: "border-error" },
    ],

    // Switchtenders
    isSwitchtender: false,
    loadSwitchtender() {
      const switchtenderData = document.getElementById("switchtenderData").textContent;
      this.isSwitchtender = JSON.parse(switchtenderData);
    },

    // UserId
    userId: null,
    loadUserId() {
      const userId = document.getElementById("userId").textContent;
      this.userId = JSON.parse(userId);
    },

    // Tooltips
    initTooltips() {
      new bootstrap.Tooltip(this.$el, {
        selector: "[data-bs-toggle='tooltip']"
      })
    },

    // URL Parsing trickery
    processUrl() {
      const match = location.hash.match(/^#action-(\d+)/);
      if (match) {
        this.currentTaskId = parseInt(match[1], 10);
      }
    },

    // Previews
    currentTaskId: null,
    currentTaskFollowups: null,
    currentTaskNotifications: [],
    async loadFollowups(taskId) {
      const response = await fetch(followupsUrl(projectId, taskId));
      this.currentTaskFollowups = await response.json();
      this.scrollToLastElement();
    },
    async loadNotifications(taskId) {
      const response = await fetch(taskNotificationsUrl(projectId, taskId));
      this.currentTaskNotifications = await response.json();
    },
    initPreviewModal() {
      const element = document.getElementById("task-preview");
      this.previewModalHandle = new bootstrap.Modal(element);
      element.addEventListener("shown.bs.modal", () => {
        this.scrollToLastElement();
      });
      const cleanup = () => {
        this.currentTaskId = null;
        this.currentTaskFollowups = null;
        this.currentTaskNotifications = null;
        location.hash = '';
      }
      element.addEventListener("hidePrevented.bs.modal", cleanup);
      element.addEventListener('hidden.bs.modal', cleanup);

      if (this.currentTaskId) this.openPreviewModal();
    },
    async onPreviewClick(id) {
      this.currentTaskId = id;
      this.openPreviewModal();
    },
    async openPreviewModal() {
      location.hash = `#action-${this.currentTaskId}`;
      this.previewModalHandle.show();

      this.loadFollowups(this.currentTaskId);
      this.loadNotifications(this.currentTaskId);

      if (!this.isSwitchtender) {
        await patchTask(this.currentTaskId, { visited: true });
      }

      await markAllAsRead(this.currentTaskId);
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
    async onSetTaskPublic(id, value) {
      await patchTask(id, { public: value });
      await this.getData();
    },
    hasNotification(followupId) {
      return this.currentTaskNotifications.filter(n => n.action_object.who && n.action_object.id === followupId).length > 0;
    },

    // Comments
    pendingComment: "",
    currentlyEditing: null,
    onEditComment(followup) {
      this.pendingComment = followup.comment;
      this.currentlyEditing = ["followup", followup.id];
      this.$refs.commentTextRef.focus();
    },
    onEditContent() {
      this.pendingComment = this.currentTask.content;
      this.currentlyEditing = ["content", this.currentTask.id];
      this.$refs.commentTextRef.focus();
    },
    async onSubmitComment() {
      if (!this.currentlyEditing) {
        await issueFollowup(this.currentTask, this.currentTask.status, this.pendingComment);
        await this.getData()
        await this.loadFollowups(this.currentTask.id);
      } else {
        const [type, id] = this.currentlyEditing;
        if (type === "followup") {
          await editComment(this.currentTask.id, id, this.pendingComment);
          await this.loadFollowups(this.currentTask.id);
        } else if (type === "content") {
          await patchTask(this.currentTask.id, { content: this.pendingComment });
          await this.getData();
        }
      }
      this.pendingComment = "";
      this.currentlyEditing = null;
    },

    // Reminiders
    currentReminderTaskId: null,
    pendingReminderDate: formatReminderDate(daysFromNow(15)),
    initReminderModal() {
      const element = document.getElementById("reminder-modal");
      this.reminderModalHandle = new bootstrap.Modal(element);
      const cleanup = () => {
        this.currentReminderTaskId = null;
        this.pendingReminderDate = formatReminderDate(daysFromNow(15));
      };
      element.addEventListener("hidePrevented.bs.modal", cleanup);
      element.addEventListener("hidden.bs.modal", cleanup);
    },
    onReminderClick(id) {
      this.currentReminderTaskId = id;
      this.openReminderModal();
    },
    openReminderModal() {
      this.reminderModalHandle.show();
    },
    onSubmitReminder() {
      const form = this.$refs.reminderForm;
      const dateInput = form.querySelector('#reminder-date');
      const daysInput = form.querySelector('#reminder-days');
      daysInput.value = Math.ceil((new Date(dateInput.value) - new Date()) / 86400000);
      form.submit();
    },
    updatePendingReminderDate(days) {
      this.pendingReminderDate = formatReminderDate(daysFromNow(days));
    },

    // Feedback
    feedbackStatus: 3,
    feedbackComment: '',
    feedbackModal: null,
    currentFeedbackTask: null,
    initFeedbackModal() {
      const element = document.getElementById("feedback-modal");
      this.feedbackModal = new bootstrap.Modal(element);
      const cleanup = () => {
        this.feedbackStatus = 3;
        this.feedbackComment = '';
        this.currentFeedbackTask = null;
      }
      element.addEventListener("hidePrevented.bs.modal", cleanup);
      element.addEventListener("hidden.bs.modal", cleanup);
    },
    openFeedbackModal(task) {
      this.currentFeedbackTask = task;
      this.feedbackModal.show();
    },
    async onSubmitFeedback() {
      await issueFollowup(this.currentFeedbackTask, this.feedbackStatus, this.feedbackComment)
      await this.getData();
      this.feedbackStatus = 3;
      this.feedbackComment = '';
      this.currentFeedbackTask = null;
      this.feedbackModal.hide();
    }
  };

  return configureBoardApp(app, options);
}

// URLS
function taskUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/`
}

function tasksUrl(projectId) {
  return `/api/projects/${projectId}/tasks/`
}

function moveTaskUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/move/`
}

function taskNotificationsUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/notifications/`
}

function markTaskNotificationsAsReadUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/notifications/mark_all_as_read/`
}

function followupsUrl(projectId, taskId) {
  return `/api/projects/${projectId}/tasks/${taskId}/followups/`
}

function followupUrl(projectId, taskId, followupId) {
  return `/api/projects/${projectId}/tasks/${taskId}/followups/${followupId}/`
}

function resourcePreviewUrl(resourceId) {
  return `/ressource/${resourceId}/embed`;
}


// Non API routes
// TODO : Make them into proper endpoints
function editTaskUrl(taskId) {
  return `/task/${taskId}/update/`;
}

function deleteTaskReminderUrl(taskId) {
  return `/task/${taskId}/remind-delete/`;
}

function editReminderUrl(taskId) {
  return `/task/${taskId}/remind/`;
}

// Utilities
function isStatusUpdate(followup) {
  return followup.status > 2 || followup.comment === "";
}

const STATUS_TEXT = {
  0: "nouveau",
  1: "en cours",
  2: "en attente",
  3: "faite",
  4: "non applicable",
  5: "faite" // ALREADY_DONE: Legacy status, kind of
}
function statusText(status) {
  return STATUS_TEXT[status];
}

function formatDate(timestamp) {
  return new Date(timestamp).toLocaleDateString("fr-FR");
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

function generateGravatarUrl(person, size = 50) {
  const hash = md5(person.email);
  let name = `${person.first_name}+${person.last_name}`;
  if (name.trim() === "+") name = "Inconnu";
  const encoded_fallback_uri = encodeURIComponent(`https://ui-avatars.com/api/${name}/${size}`);
  return `https://www.gravatar.com/avatar/${hash}?s=${size}&d=${encoded_fallback_uri}`
}
