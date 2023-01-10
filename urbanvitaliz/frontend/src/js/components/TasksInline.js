import Alpine from 'alpinejs'
import TaskApp from './Tasks'
import { STATUSES } from '../config/statuses';

function TasksInline(projectId) {

    const app = {
        currentStatus: 'all',
        filterIsPublic: false,
        boardsFiltered: [],
        boards: [
            { status: [STATUSES.PROPOSED], title: "Nouvelles", color_class: "border-error", color: "#0d6efd" },
        ],
        filterFn(d) {
            return this.canAdministrate || d.public || !d.public;
        },
        init() {
            this.boardsFiltered = this.boards
        },
        handleStatusFilterClick(status) {

            if (this.currentStatus === status || status === 'all') {
                this.currentStatus = 'all'
                return this.boardsFiltered = this.boards
            }


            this.currentStatus = status

            return this.boardsFiltered = this.boards.filter(board => board.status === status);
        },
        handlePublicFilterClick() {
            console.log('public filter clicked ');

            this.filterIsPublic = !this.filterIsPublic

            console.log(this.filterIsPublic);

            this.data.filter((d) => !d.public);
            
            // this.data.filter((task) => this.filterFn(d)).sort((a, b) => this.sortFn(a, b));
        }
    }

    return TaskApp(app, projectId);
}

Alpine.data("TasksInline", TasksInline)
