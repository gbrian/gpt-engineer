import axios from 'axios'

export default {
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