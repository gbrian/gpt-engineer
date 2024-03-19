<template>
  <div class="text-md text-wrap" v-html="html"></div>
</template>
<script>
import { full as emoji } from 'markdown-it-emoji'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true
})
md.use(emoji)

export default {
  props: ['text'],
  computed: {
    html () {
      try {
        return md.render(this.text)
      } catch {
      }
      return this.text
    }

  }
}
</script>