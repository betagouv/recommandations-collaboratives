import Alpine from 'alpinejs'

function NewTasksPreviewModal() {
    return {
        index: 0,

        get newTasks() {
            return this.$store.tasksData.newTasks
        },
        
        get currentTaskId() {
            return this.newTasks[this.index]
        },
        
        next() {
            if (this.index < this.newTasks.length) {
                this.index++    
            }
            this.$store.taskModal.currentTaskId = this.currentTaskId
        },

        previous() {
            if (this.index > 0) {
                this.index--            
            }
            this.$store.taskModal.currentTaskId = this.currentTaskId
        },

        init() {
            this.$store.taskModal.currentTaskId = this.currentTaskId
        }
    }
}

Alpine.data("NewTasksPreviewModal", NewTasksPreviewModal)
