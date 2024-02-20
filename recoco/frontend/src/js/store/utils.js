import Alpine from 'alpinejs'
import { isPlural } from '../utils/isPlural';
import { gravatar_url } from '../utils/gravatar'

Alpine.store('utils', {
    isPlural,
    gravatar_url
})

export default Alpine.store('utils')
