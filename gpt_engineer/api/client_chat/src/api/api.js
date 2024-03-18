import axios from 'axios'

import chatManager from './chatManager';

export default (query) => {
  return {
    chatManager,
    settings: {
      read () {
        return axios.get('/api/settings?' + query)
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
}