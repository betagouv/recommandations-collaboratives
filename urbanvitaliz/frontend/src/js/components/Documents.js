import Alpine from 'alpinejs'
import List from 'list.js'

Alpine.data("Files", Files)

function Files(nbDocuments) {
    return {
        init() {

            if (!nbDocuments > 0) return
            
            const options = {
                valueNames: ['name', 'description']
            };

            new List('filesId', options);
        }
    }
}

