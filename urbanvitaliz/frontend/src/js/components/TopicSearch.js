import Alpine from 'alpinejs'
import api, { searchTopicsUrl } from '../utils/api'

function TopicSearch(currentTopic, restrict_to=null) {
    return {
        topic: '',
        results: [],
        restrict_to: null,
        init() {
            this.topic = currentTopic
            this.restrict_to = restrict_to
        },
        async handleTopicChange(e) {
            e.preventDefault();

            try {
                if (e.target.value.length > 2) {
                    const results = await api.get(searchTopicsUrl(e.target.value, this.restrict_to))

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
