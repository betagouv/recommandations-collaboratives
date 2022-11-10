import 'vite/modulepreload-polyfill';
import './utils/globals'

import './store/app'

//Global reused component
import './components/Notification'
import './components/Editor'

//Global CSS
import '../css/buttons.css'
import '../css/typography.css'
import '../css/hover.css'
import '../css/colors.css'
import '../css/text-colors.css'

//Global reused component CSS
import '../css/flags.css'
import '../css/callout.css'



console.log('js main added');
