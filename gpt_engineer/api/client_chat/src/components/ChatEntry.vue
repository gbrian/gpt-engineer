<template>
  <div :class="['mb-4 relative w-full relative px-2 hover:bg-base-300 hover:rounded-md',
      message.role === 'user' ? 'chat-start': 'chat-end',
    ]" >
    <div :class="['px-2 max-w-full group w-full prose -mx-2',
      message.improvement ? 'border-green-300/20 bg-green-900' : 'border-slate-300/20',
      message.role === 'user' ? '': '',
      message.collapse ? 'max-h-40 overflow-hidden': 'h-fit',
      message.hide ? 'text-slate-200/20': ''
    ]"
    >
      <div>
        <div class="flex gap-2">
          <div class="py-2 px-1 font-bold text-xs bg-base-300 rounded-md">
            <span v-if="message.hide">
              <i class="fa-solid fa-eye-slash"></i>
            </span>
            <div v-if="message.role ==='user'">You ({{ message.role }})</div>
            <div v-else>gpt-engineer ({{ message.role }})</div>
          </div>
          <div class="hidden group-hover:block">
            <button class="btn btn-xs" @click="message.collapse = !message.collapse">
              <span v-if="message.collapse">
                <i class="fa-solid fa-chevron-up"></i>
              </span>
              <span v-else>
                <i class="fa-solid fa-chevron-down"></i>
              </span>
            </button>
            <button class="btn btn-xs" @click="$emit('copy')">
              <i class="fa-solid fa-copy"></i>
            </button>      
            <button class="btn btn-error btn-xs" @click="$emit('remove')">
              <i class="fa-solid fa-trash"></i>
            </button>
            <button class="btn btn-xs" @click="$emit('edit')">
              <i class="fa-solid fa-pencil"></i>
            </button>
            <button class="btn btn-info btn-xs" @click="showDoc = !showDoc">
              <i class="fa-solid fa-code"></i>
            </button>
            <button class="btn btn-xs" @click="$emit('hide')">
              <span v-if="message.hide">
                <i class="fa-solid fa-eye"></i>
              </span>
              <span v-else>
                <i class="fa-solid fa-eye-slash"></i>
              </span>
            </button>      
          </div>
        </div>
        <div class="text-md text-wrap -my-2" v-html="html"></div>
      </div>
    </div>
    <button class="btn btn-sm btn-warning abolsute right-2 top-2"
        v-for="code in codeBlocks" :key="code.id" ref="runButton" @click="onRunEdit(code)">
      Run
    </button>
  </div>
</template>
<script>
import { full as emoji } from 'markdown-it-emoji'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true
})
md.use(emoji)

export default {
  props: ['message'],
  data () {
    return {
      codeBlocks: [],
      showDoc: false
    }
  },
  mounted () {
    const codeBlocks = [...this.$el.querySelectorAll("pre")]
    this.codeBlocks = codeBlocks.filter(c => c.innerText.indexOf("<<<<<<< HEAD") !== -1)
    setTimeout(() => {
      console.log("Run buttons", this.$refs.runButton)
      this.$refs.runButton?.forEach((b, ix) => {
        const codeBlock = codeBlocks[ix]
        codeBlock.classList.add("relative")
        codeBlock.appendChild(b)
      })
    }, 300)
  },
  computed: {
    html () {
      if (!this.showDoc) {
        try {
          return md.render(this.message.content)
        } catch (ex) {
          console.error("Message can't be rendered", this.message)
        }
      }
      return this.showDocPreview
    },
    showDocPreview () {
      return md.render("```json\n" + JSON.stringify(this.message, null, 2) + "\n```")
    }
  },
  methods: {
    onRunEdit (preNone) {
      const codeNode = preNone.querySelector('code')
      const codeText = codeNode.innerText
      const codeLang = [...codeNode.classList.values()].find(c => c.startsWith("language-"))||"language-code"
      const codeSnipped = "```" + codeLang.split("language-")[1] + "\n" + codeText + "\n```"
      this.$emit('run-edit', codeSnipped)
    }
  }
}
</script>