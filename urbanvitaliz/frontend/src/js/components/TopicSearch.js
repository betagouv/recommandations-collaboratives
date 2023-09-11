import Alpine from 'alpinejs'
import api, { searchTopicsUrl } from '../utils/api'

function TopicSearch(currentTopic) {
    return {
        topic: '',
        results: [],
        init() {
            this.topic = currentTopic
        },
        async handleTopicChange(e) {
            e.preventDefault();

            try {
                if (e.target.value.length > 2) {
                    const results = await api.get(searchTopicsUrl(e.target.value))

                    if (results && results.data) {
                        return this.results = results.data
                    }
                } else {
                    return this.results = []
                }
            }
            catch (errors) {
                console.error('errors in topic search : ', errors)
            }
        },
        handleResultClick(result) {
            this.topic = result
        }
    }
}

Alpine.data("TopicSearch",TopicSearch)
