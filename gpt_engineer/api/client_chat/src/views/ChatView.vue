<script setup>
import ChatEntry from '@/components/ChatEntry.vue'
</script>
<template>
  <div class="flex flex-col h-full justify-between">
    <div class="text-xl flex gap-2 items-center">
      CODX
      <input type="text" class="input input-xs input-bordered" v-model="chat.name" />
      <button class="btn btn-sm" @click="saveChat">
        <i class="fa-solid fa-floppy-disk"></i>
      </button>
      <button class="btn btn-sm btn-error" @click="deleteChat">
        <i class="fa-solid fa-trash"></i>
      </button>
      <div class="grow"></div>
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button btn-sm" class="btn m-1">
          <i class="fa-solid fa-folder-tree"></i>
        </div>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li v-for="openChat in chats" :key="openChat.id" @click="loadChat(openChat)" >
            <a>{{ openChat.name }}</a>
          </li>
        </ul>
      </div>
    </div>
    <div class="flex flex-col grow" v-if="chat">
      <div class="grow overflow-auto relative">
        <div class="absolute top-0 left-0 w-full h-full scroller">
          <div v-for="message, ix in chat.messages" :key="message.id">
            <ChatEntry :message="message"
              @edit="onEditMessage(ix)"
              @remove="removeMessage(ix)"
              @hide="toggleHide(ix)"
              @run-edit="runEdit"
            />
          </div>
          <div class="anchor"></div>
        </div>
      </div>
      <div class="badge my-2 animate-pulse" v-if="waiting">typing ...</div>
  
      <div class="flex gap-2 justify-between my-2">
        <div class="flex gap-2">
          <button class="btn btn-primary btn-sm" @click="newChat">
            <i class="fa-solid fa-plus"></i> New chat
          </button>
        </div>
      </div>
      <div class="flex gap-2 items-end">
        <div :class="['max-h-40 border rounded-md grow px-2 py-1 overflow-auto text-wrap',
          editMessageId !== null ? 'border-error': ''
        ]" contenteditable="true"
          ref="editor" @input="onMessageChange"
          @keydown.esc="onResetEdit"
          @paste="onContentPaste"
        >
        </div>
        <button class="btn btn-info btn-sm btn-circle mb-1" @click="sendMessage" :disabled="!editMessage">
          <i class="fa-solid fa-comment"></i>
        </button>
        <button class="btn btn-warning btn-sm mb-1" @click="improveCode">
          <i class="fa-solid fa-code"></i> Code
        </button>
      </div>
    </div>
  </div>
</template>
<script>
import { API } from '../api/api'
const defFormater = d => JSON.stringify(d, null, 2)

export default {
  data() {
    return {
      chat: null,
      waiting: false,
      editMessage: null,
      editMessageId: null,
      chats: []
    }
  },
  async created () {
    this.chats = API.chatManager.getChats()
    this.chat = this.chats.reverse()[0]
    if (!this.chat) {
      this.chat = API.chatManager.newChat()
    }
  },
  computed: {
    editor () {
      return this.$refs.editor
    },
  },
  methods: {
    newChat () {
      this.chat = API.chatManager.newChat()
    },
    addMessage (msg) {
      this.chat.messages = [
        ...this.chat.messages||[],
        msg
      ]
      this.saveChat()
    },
    postMyMessage () {
      if (this.editMessage) {
        this.addMessage({
          role: 'user',
          content: this.editMessage
        })
        this.editMessage = null
        this.editor.innerText = ""
      }
    },
    async sendMessage () {
      if (this.editMessageId !== null) {
        this.onUpdateMessage()
        return
      }
      this.postMyMessage()
      this.sendApiRequest(
        () => API.chat.message(this.chat),
        ({ message, search_results }) => {
          return `${message}
            ${search_results.map(r => JSON.stringify(r))}
          `
        }
      )
    },
    onMessageChange (ev) {
      this.editMessage = ev.target.innerText
    },
    refreshKnowledge () {
      this.sendApiRequest(() => API.knowledge.reload())
    },
    readKnowledgeStatus () {
      this.sendApiRequest(
        () => API.knowledge.status(),
        data => ['### last update',
                  data.last_update,
                  '### Files',
                  data.pending_files.map(file => ` * ${file}`).join("\n"),
                ].join("\n")
      )
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
    async sendApiRequest (apiCall, formater = defFormater) {
      try {
        this.waiting = true
        const { data } = await apiCall()
        this.addMessage({
          role: 'assistent',
          content: formater(data),
          data
        })
      } catch (ex) {
        this.addMessage({
          role: 'assistant',
          content: ex.message
        }) 
      }
      this.waiting = false
    },
    removeMessage(ix) {
      this.chat.messages = this.chat.messages.filter((m, i) => i !== ix)
    },
    onEditMessage (ix) {
      const message = this.chat.messages[ix]
      this.editMessage = message.content
      this.editor.innerText = this.editMessage
      this.editMessageId = ix
      this.saveChat()
    },
    toggleHide(ix) {
      const message = this.chat.messages[ix]
      message.hide = !message.hide 
      this.saveChat()
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
    saveChat () {
      API.chatManager.saveChat(this.chat)
      this.chats = API.chatManager.getChats()
    },
    deleteChat () {
      API.chatManager.deleteChat(this.chat)
      this.chats = API.chatManager.getChats()
      this.newChat()
    },
    onContentPaste (ev) {
      // Reset format
      requestAnimationFrame(() => {
        const text = this.editor.innerText
        this.editor.innerHTML = ""
        this.editor.innerText = text
      })
    },
    loadChat (newChat) {
      this.chat = newChat
    }
  }
}
</script>