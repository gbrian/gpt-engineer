<script setup>
</script>
<template>
  <div class="px-4 py-2 flex flex-col h-full justify-between">
    <div class="text-xl flex gap-2 items-center">
      CODX GPT-ENGINEER - 
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
          <i class="fa-solid fa-folder-open"></i>
        </div>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li v-for="openChat in chats" :key="openChat.id" @click="chat = openChat" >
            <a>{{ openChat.name }}</a>
          </li>
        </ul>
      </div>
    </div>
    <div class="flex flex-col grow" v-if="chat">
      <div class="grow overflow-auto relative">
        <div class="absolute top-0 left-0 w-full h-full scroller">
          <div v-for="message, ix in chat.messages" :key="message.id">
            <div :class="['mb-4 relative w-full relative',
              message.role === 'user' ? 'chat-start': 'chat-end'
            ]" >
              <div :class="['border border-slate-300/20 p-2 rounded-md prose max-w-full group w-full',
                message.role === 'user' ? '': '',
                message.collapse ? 'h-40 overflow-hidden': 'h-fit'
              ]"
                @dblclick="message.collapse = !message.collapse"
              >
                <div>
                  <div class="absolute right-2 top-2 group-hover:flex gap-2 z-10 hidden">
                    <button class="btn btn-xs" @click="onEditMessage(ix)">
                      <i class="fa-solid fa-pencil"></i>
                    </button>
                    <button class="btn btn-xs" @click="message.collapse = !message.collapse">
                      <span v-if="message.collapse">
                        <i class="fa-solid fa-chevron-up"></i>
                      </span>
                      <span v-else>
                        <i class="fa-solid fa-chevron-down"></i>
                      </span>
                    </button>
                    <button class="btn btn-error btn-xs" @click="removeMessage(ix)">
                      <i class="fa-solid fa-trash"></i>
                    </button>
                  </div>
                  <div class="badge bagde-outline badge-xs font-bold">
                    <div v-if="message.role ==='user'">You</div>
                    <div v-else>gpt-engineer</div>
                  </div>
                  <div class="text-md" v-html="renderMessage(message)"></div>
                </div>
              </div>
            </div>
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
          <button class="btn btn-primary btn-sm" @click="readKnowledgeStatus">
            <i class="fa-solid fa-circle-info"></i> Knowledge status
          </button>
          <button class="btn btn-primary btn-sm" @click="refreshKnowledge">
            <i class="fa-solid fa-book"></i> Refresh knowledge
          </button>
        </div>
      </div>
      <div class="flex gap-2 items-end">
        <div :class="['border rounded-md grow px-2 py-1',
          editMessageId !== null ? 'border-error': ''
        ]" contenteditable="true"
          ref="editor" @input="onMessageChange"
          @keydown.esc="onResetEdit"
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
import api from '../api/api'
const defFormater = d => JSON.stringify(d, null, 2)
import { full as emoji } from 'markdown-it-emoji'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true
})
md.use(emoji)

export default {
  data() {
    return {
      chat: api.chatManager.newChat(),
      waiting: false,
      editMessage: null,
      editMessageId: null,
      chats: api.chatManager.getChats()
    }
  },
  computed: {
    editor () {
      return this.$refs.editor
    },
  },
  methods: {
    newChat () {
      this.chat = api.chatManager.newChat()
    },
    addMessage (msg) {
      this.chat.messages = [
        ...this.chat.messages||[],
        msg
      ]
      this.saveChat()
    },
    async sendMessage () {
      if (this.editMessageId !== null) {
        this.onUpdateMessage()
        return
      }
      this.addMessage({
        role: 'user',
        content: this.editMessage
      })
      this.editMessage = null
      this.editor.innerText = ""
      this.sendApiRequest(
        () => api.chat.message(this.chat.messages),
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
      this.sendApiRequest(() => api.knowledge.reload())
    },
    readKnowledgeStatus () {
      this.sendApiRequest(
        () => api.knowledge.status(),
        data => ['### last update',
                  data.last_update,
                  '### Files',
                  data.pending_files.map(file => ` * ${file}`).join("\n"),
                ].join("\n")
      )
    },
    improveCode () {
      this.sendApiRequest(
        () => api.improve(this.chat.messages),
        data => ['### Changes done',
                  data.messages.reverse()[0].content,
                  '### Edits done',
                  data.edits.map(edit => "```json\n"
                      + JSON.stringify(edit, 2, null) + 
                    "\n```"),
                  "### Error",
                  JSON.stringify(data.error, 2, null)
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
    renderMessage(msg) {
      return md.render(msg.content)
    },
    removeMessage(ix) {
      this.chat.messages = this.chat.messages.filter((m, i) => i !== ix)
    },
    onEditMessage (ix) {
      const message = this.chat.messages[ix]
      this.editMessage = message.content
      this.editor.innerText = this.editMessage
      this.editMessageId = ix
    },
    onUpdateMessage () {
      const message = this.chat.messages[this.editMessageId]
      message.content = this.editMessage
      this.onResetEdit()
    },
    onResetEdit() {
      if (this.editMessageId !== null) {
        this.editMessage = null
        this.editor.innerText = ""
        this.editMessageId = null
      }
    },
    saveChat () {
      api.chatManager.saveChat(this.chat)
      this.chats = api.chatManager.getChats()
    },
    deleteChat () {
      api.chatManager.deleteChat(this.chat)
      this.chats = api.chatManager.getChats()
      this.newChat()
    }
  }
}
</script>