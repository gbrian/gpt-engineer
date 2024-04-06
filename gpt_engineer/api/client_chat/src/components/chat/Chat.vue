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
    }
  },
  computed: {
    editor () {
      return this.$refs.editor
    },
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
      this.chat.messages = this.chat.messages.filter((m, i) => i !== ix)
      this.saveChat()
    },
  }
}
</script>