import axios from 'axios'

import chatManager from './chatManager';

export default {
  chatManager,
  knowledge: {
    status () {
      return axios.get('/api/knowledge/status')
    },
    reload () {
      return axios.get('/api/knowledge/reload')
    }
  },
  chat: {
    message (messages) {
      return axios.post('/api/chat', { messages })
    }
  },
  run: {
    improve (messages) {
      return axios.post('/api/run/improve', { messages })
    },
    edit (messages) {
      return axios.post('/api/run/edit', { messages })
    }
  }
}