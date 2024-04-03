<script setup>
import ChatEntry from '@/components/ChatEntry.vue'
</script>
<template>
  <div class="flex flex-col gap-2 h-full justify-between" v-if="chat">
    <div class="text-xl flex gap-2 items-center px-2">
      CODX
      <input type="text" class="input input-xs input-bordered w-40" v-model="chat.name" />
      <div class="dropdown">
        <div tabindex="0" role="button" class="btn btn-sm m-1">Add profiles</div>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li @click="addProfile(p)" v-for="p in profiles" :key="p"
            ><a><i class="fa-solid fa-plus"></i> {{ p }}</a>
          </li>
        </ul>
      </div>
      <button class="btn btn-primary btn-xs" @click="newChat">
        <i class="fa-solid fa-plus"></i>
      </button>
      <button class="btn btn-xs" @click="saveChat">
        <i class="fa-solid fa-floppy-disk"></i>
      </button>
      <button class="btn btn-xs btn-error" @click="deleteChat">
        <i class="fa-solid fa-trash"></i>
      </button>
      <div class="grow"></div>
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button btn-sm" class="btn btn-xs">
          <i class="fa-solid fa-folder-tree"></i>
        </div>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li v-for="openChat in chats" :key="openChat" @click="loadChat(openChat)" >
            <a>{{ openChat }}</a>
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
              @copy="onCopy(message)"
            />
          </div>
          <div class="anchor" ref="anchor"></div>
        </div>
      </div>
      <div class="badge my-2 animate-pulse" v-if="waiting">typing ...</div>
      <div class="p-2" v-if="chat.file_list?.length || chat.profiles?.length">
        <span class="cursor-pointer mr-2 hover:underline group text-primary"
          v-for="file in chat.profiles" :key="file" :title="file"
          @click="showFile = file"
        >
          <i class="fa-solid fa-rectangle-list"></i>
          {{ file.split("/").reverse()[0] }}
        </span>

        <span class="cursor-pointer mr-2 hover:underline group text-secondary"
          v-for="file in chat.file_list" :key="file" :title="file"
          @click="showFile = file"
        >
          <i class="fa-solid fa-file"></i>
          {{ file.split("/").reverse()[0] }}
        </span>
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
        <button class="btn btn-info btn-sm btn-circle mb-1" @click="sendMessage">
          <i class="fa-solid fa-comment"></i>
        </button>
        <button class="btn btn-warning btn-sm mb-1" @click="improveCode">
          <i class="fa-solid fa-code"></i> Code
        </button>
      </div>
    </div>
    <div class="modal modal-open" role="dialog" v-if="showFile">
      <div class="modal-box flex flex-col gap-4 p-4">
        <h3 class="font-bold text-lg">
          This file belongs to the task context:
          <div class="font-thin">{{ showFile }}</div>
        </h3>
        <div class="flex gap-2 justify-center">
          <button class="btn btn-error" @click="removeFileFromContext">
            Remove
          </button>
          <button class="btn" @click="showFile = null">
            Close
          </button>
        </div>
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
      chats: [],
      profiles: null,
      showFile: null
    }
  },
  async created () {
    this.chats = await API.chats.list()
    if (this.chats.length) {
      this.chat = await API.chats.loadChat(this.chats.reverse()[0])
    } else {
      this.chat = await API.chats.newChat()
      this.chats.push(this.chat.name)
    }
    this.loadProfiles()
  },
  computed: {
    editor () {
      return this.$refs.editor
    },
  },
  methods: {
    async loadProfiles () {
      try {
        const { data } = await API.profiles.list()
        this.profiles = data
      } catch {}
    },
    newChat () {
      this.chat = API.chatManager.newChat()
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
    onMessageChange (ev) {
      this.editMessage = ev.target.innerText
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
        await this.loadChat(this.chat.name)
        this.$refs.anchor.scrollIntoView()
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
      this.saveChat()
    },
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
    async saveChat () {
      return API.chats.save(this.chat)
    },
    deleteChat () {
      API.chatManager.deleteChat(this.chat)
      this.chats = API.chatManager.getChats()
      this.newChat()
    },
    onContentPaste (ev) {
    },
    async loadChat (newChat) {
      this.chat = await API.chats.loadChat(newChat)
    },
    onCopy (message) {
      navigator.permissions.query({name: "clipboard-read"}).then(result => {
          if (result.state == "granted" || result.state == "prompt") {
            navigator.clipboard.writeText(message.content)
          }
      })
      .catch(console.error);
    },
    async removeFileFromContext () {
      this.chat.profiles = this.chat.profiles.filter(f => f !== this.showFile) 
      this.chat.file_list = this.chat.file_list.filter(f => f !== this.showFile)
      await this.saveChat()
      await this.loadChat(this.chat.name)
      this.showFile = null
    },
    async addProfile (profile) {
      if (this.chat.profiles.find(f => f.endsWith(profile))) {
        return
      }
      this.chat.profiles = [...this.chat.profiles, profile]
      await this.saveChat()
      await this.loadChat(this.chat.name)
    }
  }
}
</script>