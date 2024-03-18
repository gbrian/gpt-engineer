import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')

import API from './api/api'
const api = API(window.location.search.slice(1))

app.mixin({
  computed: {
    api () {
      return api
    }
  }
})
