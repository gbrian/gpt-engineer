import axios from 'axios'

import chatManager from './chatManager';

const query = window.location.search.slice(1)
export const API = {
    liveRequests: 0,
    get (url) {
      API.liveRequests++
      return axios.get(url)
        .catch(console.error)
        .finally(() => API.liveRequests--)
    },
    post (url, data) {
      API.liveRequests++
      return axios.post(url, data)
      .catch(console.error)
      .finally(() => API.liveRequests--)
    },
    put (url, data) {
      API.liveRequests++
      return axios.put(url, data)
      .catch(console.error)
      .finally(() => API.liveRequests--)
    },
    lastSettings: null,
    chatManager,
    project: {
      create() {
        return API.get('/api/project/create?' + query)
      }
    },
    settings: {
      async read () {
        API.lastSettings = null
        const res = await API.get('/api/settings?' + query)
        API.lastSettings = res.data
        return res
      },
      write (settings) {
        return API.put('/api/settings?' + query, settings)
      }
    },
    knowledge: {
      status () {
        return API.get('/api/knowledge/status?' + query)
      },
      reload () {
        return API.get('/api/knowledge/reload?' + query)
      },
      reloadFolder (path) {
        return API.post(`/api/knowledge/reload-path?` + query, { path })
      },
      search ({ searchTerm: search_term, searchType: search_type }) {
        return API.post(`/api/knowledge/reload-search?` + query, { search_term, search_type })
      },
      delete (sources) {
        return API.post(`/api/knowledge/delete?` + query, { sources })  
      }
    },
    chat: {
      message (chat) {
        return API.post('/api/chat?' + query, chat)
      }
    },
    run: {
      improve (chat) {
        return API.post('/api/run/improve?' + query, chat)
      },
      edit (chat) {
        return API.post('/api/run/edit?' + query, chat)
      }
    }
  }

  window.API = API