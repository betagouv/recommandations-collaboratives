import Alpine from 'alpinejs'
import api, { tasksUrl } from '../utils/api'
import { generateUUID } from '../utils/uuid'

Alpine.store('tasks', {
    title:'',
    init() {
        console.log('store init');
        this.title = "title"
        console.log('title : ', this.title);
    },
    data: [],
    async getData(projectId) {
        console.log('store : tasks : get data')
        const json = await api.get(tasksUrl(projectId))

        const data = json.data.map(d => Object.assign(d, {
            uuid: generateUUID()
        }));

        this.data = data;
    },
    patchTask() {

    },
    moveAbove() {

    },
    moveBelow() {

    }

})

export default Alpine.store('tasks')
