import Alpine from 'alpinejs'

function TasksInline() {
    return {
        init() {
            console.log('tasks inline ready')
            console.log(this.$store.app.title)
        },
        get tasks() {
            return this.$store.app.data
        },
        get isLoading() {
            return this.$store.app.isLoading
        }
    }
}

Alpine.data("TasksInline", TasksInline)
