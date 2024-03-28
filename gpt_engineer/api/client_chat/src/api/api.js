import axios from 'axios'

import chatManager from './chatManager';

const gpteng_key = window.location.search
                    .slice(1).split("&")
                    .map(p => p.split("="))
                    .find(([k, v]) => k === "gpteng_path")
const gpteng_path = decodeURIComponent(gpteng_key ? gpteng_key[1] : "")

const readLastSettings = () => {
  if (gpteng_path) {
    return {
      gpteng_path
    }
  }
  const settings = localStorage.getItem("API_SETTINGS")
  try {
    return JSON.parse(settings)
  } catch {}
  return null
}
const query = () => `gpteng_path=${encodeURIComponent(API.lastSettings?.gpteng_path)}`
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
    lastSettings: readLastSettings(),
    chatManager,
    project: {
      create() {
        return API.get('/api/project/create?' + query())
      },
      watch () {
        return API.get('/api/project/watch?' + query())
      },
      unwatch () {
        return API.get('/api/project/unwatch?' + query())
      }
    },
    settings: {
      async read () {
        const res = await API.get('/api/settings?' + query())
        API.lastSettings = res.data
        if (API.lastSettings) {
          localStorage.setItem("API_SETTINGS", JSON.stringify(API.lastSettings))
        }
        return res
      },
      write (settings) {
        return API.put('/api/settings?' + query(), settings)
      }
    },
    knowledge: {
      status () {
        return API.get('/api/knowledge/status?' + query())
      },
      reload () {
        return API.get('/api/knowledge/reload?' + query())
      },
      reloadFolder (path) {
        return API.post(`/api/knowledge/reload-path?` + query(), { path })
      },
      search ({ 
          searchTerm: search_term,
          searchType: search_type,
          documentSearchType: document_search_type,
          cutoffScore: document_cutoff_score,
          documentCount: document_count
      }) {
        return API.post(`/api/knowledge/reload-search?` + query(), {
            search_term,
            search_type,
            document_search_type,
            document_cutoff_score,
            document_count
        })
      },
      delete (sources) {
        return API.post(`/api/knowledge/delete?` + query(), { sources })  
      }
    },
    chat: {
      message (chat) {
        return API.post('/api/chat?' + query(), chat)
      }
    },
    run: {
      improve (chat) {
        return API.post('/api/run/improve?' + query(), chat)
      },
      edit (chat) {
        return API.post('/api/run/edit?' + query(), chat)
      }
    },
    profiles: {
      list () {
        return API.get('/api/profiles?' + query())
      },
      load (name) {
        return API.get(`/api/profiles/${name}?` + query())
      },
      save (profile) {
        return API.post(`/api/profiles?` + query(), profile)
      },
      delete (name) {
        return API.delete(`/api/profiles/${name}?` + query())
      }
    }
  }

  window.API = API