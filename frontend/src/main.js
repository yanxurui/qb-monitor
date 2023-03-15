import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import Notifications from '@kyvg/vue3-notification'
import vue3GoogleLogin from 'vue3-google-login'
import { createVfm } from 'vue-final-modal'

import './assets/main.css'
import 'vue-final-modal/style.css'

const app = createApp(App)
const pinia = createPinia()
const vfm = createVfm()

app.use(pinia)
app.use(router)
app.use(Notifications)
app.use(vue3GoogleLogin, {
    clientId: '582570402124-u6ntuo1s4ct7p83q2g33dd3ujtimpi4s.apps.googleusercontent.com'
  })
app.use(vfm)

app.mount('#app')
