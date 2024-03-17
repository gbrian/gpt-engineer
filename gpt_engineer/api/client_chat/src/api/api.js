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
  improve (messages) {
    return axios.post('/api/improve', { messages })
  }
}