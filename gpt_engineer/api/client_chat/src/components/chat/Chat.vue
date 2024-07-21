<script setup>
import ChatEntry from '@/components/ChatEntry.vue'
</script>
<template>
    <div class="flex flex-col grow">
      <div class="grow overflow-auto relative">
        <div class="absolute top-0 left-0 w-full h-full scroller">
          <div v-for="message, ix in chat.messages" :key="message.id">
            <ChatEntry :message="message"
              @edit="onEditMessage(ix)"
              @remove="removeMessage(ix)"
              @hide="toggleHide(ix)"
              @run-edit="runEdit"
              @copy="onCopy(message)"
            />
          </div>
          <div class="anchor" ref="anchor"></div>
        </div>
      </div>
      <div class="badge my-2 animate-pulse" v-if="waiting">typing ...</div>
      <div class="dropdown dropdown-top dropdown-open mb-1" v-if="showTermSearch">
        <div tabindex="0" role="button" class="rounded-md bg-base-300 w-fit p-2">
          <div class="flex p-1 items-center text-sky-600">
            <i class="fa-solid fa-at"></i>
            <input type="text" v-model="termSearchQuery"
              ref="termSearcher"
              class="-ml-1 input input-xs text-lg bg-transparent" placeholder="search term..."
              @keydown.down.stop="onSelNext"
              @keydown.up.stop="onSelPrev"
              @keydown.enter.stop="addSerchTerm(searchTerms[searchTermSelIx])"
              @keydown.esc="closeTermSearch"
            />
            <button class="btn btn-xs btn-circle btn-outline btn-error"
              @click="termSearchQuery = null"            
              v-if="termSearchQuery">
              <i class="fa-solid fa-circle-xmark"></i>
            </button>
          </div>
        </div>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-300 rounded-box w-fit" v-if="searchTerms">
          <li v-for="term, ix in searchTerms" :key="term.key">
            <a @click="addSerchTerm(term)">
              <div :class="[searchTermSelIx === ix ? 'underline':'']">
                <span class="text-sky-600 font-bold">@{{ term.key }}</span> <span class="text-xs">({{ term.file.split("/").reverse()[0] }})</span>
              </div>
            </a>
          </li>
        </ul>
      </div>
      <div class="flex gap-2 items-end mt-2">
        <div :class="['max-h-40 border rounded-md grow px-2 py-1 overflow-auto text-wrap',
          editMessageId !== null ? 'border-error': ''
        ]" contenteditable="true"
          ref="editor" @input="onMessageChange"
          @paste="onContentPaste"
        >
        </div>
        <button class="btn btn-info btn-sm btn-circle mb-1" @click="sendMessage">
          <i class="fa-solid fa-comment"></i>
        </button>
        <button class="btn btn-neutral btn-sm btn-circle mb-1" @click="askKnowledge">
          <i class="fa-solid fa-book"></i>
        </button>
        <button class="btn btn-warning btn-sm mb-1" @click="improveCode">
          <i class="fa-solid fa-code"></i> Code
        </button>
      </div>
    </div>
</template>
<script>
import { API } from '@/api/api'
const defFormater = d => JSON.stringify(d, null, 2)

export default {
  props: ['chat'],
  data () {
    return {
      waiting: false,
      editMessage: null,
      editMessageId: null,
      termSearchQuery: null,
      searchTerms: null,
      searchTermSelIx: -1,
      showTermSearch: false
    }
  },
  computed: {
    editor () {
      return this.$refs.editor
    },
  },
  watch: {
    termSearchQuery (newVal) {
      if (newVal?.length > 2) {
        this.searchKeywords()
      } else {
        this.searchTerms = null
      }
    }
  },
  methods: {
    onEditMessage (ix) {
      const message = this.chat.messages[ix]
      this.editMessage = message.content
      this.editor.innerText = this.editMessage
      this.editMessageId = ix
    },
    toggleHide(ix) {
      const message = this.chat.messages[ix]
      message.hide = !message.hide 
      this.saveChat()
    },
    onCopy (message) {
      navigator.permissions.query({name: "clipboard-read"}).then(result => {
          if (result.state == "granted" || result.state == "prompt") {
            navigator.clipboard.writeText(message.content)
          }
      })
      .catch(console.error);
    },
    onMessageChange (ev) {
      this.editMessage = ev.target.innerText
      return
      if (this.editMessage[this.editMessage.length-1] === '@') {
        this.showTermSearch = true
        requestAnimationFrame(() => 
        this.$refs.termSearcher.focus())
      }
    },
    improveCode () {
      this.postMyMessage()
      this.sendApiRequest(
        () => API.run.improve(this.chat),
        data => ['### Changes done',
                  data.messages.reverse()[0].content,
                  '### Edits done',
                  data.edits.map(edit => "```json\n"
                      + JSON.stringify(edit, 2, null) + 
                    "\n```"),
                  "### Error",
                  JSON.stringify(data.errors, 2, null)
                ].join("\n")
      )
    },
    runEdit (codeSnipped) {
      this.sendApiRequest(
        () => API.run.edit({ id: "", messages: [{ role: 'user', content: codeSnipped }] }),
        data => [
                  data.messages.reverse()[0].content,
                  "\n\n",
                  ...data.errors.map(e => ` * ${e}\n`)
                ].join("\n")
      )
    },
    addMessage (msg) {
      this.chat.messages = [
        ...this.chat.messages||[],
        msg
      ]
    },
    postMyMessage () {
      if (this.editMessage) {
        this.addMessage({
          role: 'user',
          content: this.editMessage
        })
        this.editMessage = null
        this.editor.innerText = ""
        this.$refs.anchor.scrollIntoView()
      }
    },
    async sendMessage () {
      if (this.editMessageId !== null) {
        this.onUpdateMessage()
        return
      }
      this.postMyMessage()
      this.sendApiRequest(
        () => API.chats.message(this.chat),
        ({ content } = {}) => {
          return `${ content }`
        }
      )
    },
    getSendMessage() {
      return this.editMessage ||
                this.chat.messages[this.chat.messages.length - 1].content
    },
    async askKnowledge () {
      const searchTerm = this.getSendMessage() 
      const knowledgeSearch = {
          searchTerm,
          searchType: 'embeddings',
          documentSearchType: API.lastSettings.knowledge_search_type,
          cutoffScore: API.lastSettings.knowledge_context_cutoff_relevance_score,
          documentCount: API.lastSettings.knowledge_search_document_count
      }
      this.postMyMessage()
      const { data: { documents } } = await API.knowledge.search(knowledgeSearch)
      documents.map(doc => this.addMessage({
          role: 'assistant',
          content: `#### File: ${doc.metadata.source.split("/").reverse()[0]}\n>${doc.metadata.source}\n\`\`\`${doc.metadata.language}\n${doc.page_content}\`\`\``
        }) 
      )
      // const allSources = documents.map(doc => doc.metadata.source)
      // this.chat.file_list = [...this.chat.file_list||[], ...allSources].filter((v,ix,arr) => arr.findIndex(e => e === v) === ix)
      
      this.saveChat()
    },
    async sendApiRequest (apiCall, formater = defFormater) {
      try {
        this.waiting = true
        await apiCall()
        this.$emit('refresh-chat')
        this.$refs.anchor.scrollIntoView()
      } catch (ex) {
        this.addMessage({
          role: 'assistant',
          content: ex.message
        }) 
      }
      this.waiting = false
    },
    onUpdateMessage () {
      const message = this.chat.messages[this.editMessageId]
      message.content = this.editMessage
      this.onResetEdit()
      this.saveChat()
    },
    onResetEdit() {
      if (this.editMessageId !== null) {
        this.editMessage = null
        this.editor.innerText = ""
        this.editMessageId = null
      }
    },
    removeMessage(ix) {
      this.$emit("delete-message", ix)
    },
    async searchKeywords () {
      const { data } = await API.knowledge.searchKeywords(this.termSearchQuery)
      this.searchTerms = Object.keys(data).map(k => data[k].reduce((acc, term) => {
        acc.push({
          key: term,
          file: k
        })
        return acc
      }, []))
      .reduce((a, b) => a.concat(b), [])
      this.searchTermSelIx = 0
    },
    addSerchTerm(term) {
      let text = this.$refs.editor.innerText
      if (text[text.length-1] === '@') {
        text = text.slice(0, text.length-1)
      }
      text += `@${term.key} `
      this.editMessage = text.trim()
      this.$refs.editor.innerText = this.editMessage
      
      this.$emit('add-file', term.file)
      this.closeTermSearch ();
    },
    closeTermSearch () {
      this.searchTerms = null
      this.termSearchQuery = null
      this.showTermSearch = false
      const target = this.$refs.editor

      const range = document.createRange();
      const sel = window.getSelection();
      range.selectNodeContents(target);
      range.collapse(false);
      sel.removeAllRanges();
      sel.addRange(range);
      target.focus();
      range.detach();
    },
    onSelNext () {
      this.searchTermSelIx++
      if (this.searchTermSelIx === this.searchTerms?.length) {
        this.searchTermSelIx = 0
      }
    },
    onSelPrev () {
      this.searchTermSelIx--
      if (this.searchTermSelIx === -1) {
        this.searchTermSelIx = this.searchTerms?.length - 1
      }
    },
    saveChat () {
      this.$emit('save')
    }
  }
}
</script>