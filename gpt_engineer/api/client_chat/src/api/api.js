import axios from 'axios'

import chatManager from './chatManager';

const query = window.location.search.slice(1)
export const API = {
    lastSettings: null,
    chatManager,
    settings: {
      async read () {
        const res = await axios.get('/api/settings?' + query)
        API.lastSettings = res.data
        return res
      },
      write (settings) {
        return axios.put('/api/settings?' + query, settings)
      }
    },
    knowledge: {
      status () {
        return axios.get('/api/knowledge/status?' + query)
      },
      reload () {
        return axios.get('/api/knowledge/reload?' + query)
      },
      reloadFolder (path) {
        return axios.post(`/api/knowledge/reload-path?` + query, { path })
      }
    },
    chat: {
      message (messages) {
        return axios.post('/api/chat?' + query, { messages })
      }
    },
    run: {
      improve (messages) {
        return axios.post('/api/run/improve?' + query, { messages })
      },
      edit (messages) {
        return axios.post('/api/run/edit?' + query, { messages })
      }
    }
  }

  window.API = API