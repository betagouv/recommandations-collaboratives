import Alpine from 'alpinejs'
import List from 'list.js'

Alpine.data("Files", Files)

function Files() {
    return {
        init() {
            const options = {
                valueNames: ['name', 'description']
            };

            const fileList = new List('filesId', options);
        }
    }
}

