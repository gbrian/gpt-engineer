<script setup>
import hljs from 'highlight.js';
import CodeEditor from 'simple-code-editor';
</script>
<template>
  <CodeEditor
    line-nums 
    :value="codeText"
    :languages="languages"
    width="100%"
    theme="github-dark"
  ></CodeEditor>
</template>
<script>
export default {
  props: ['code'],
  data () {
    return {
      codeText: null,
      languages: null
    }
  },
  created () {
    const language = this.code.attributes["class"].value.split("-").reverse()[0]
    this.languages = [[ language, language.toUpperCase() ]]
    this.codeText = this.code.innerText
    console.log("Code block created", language)
  },
  mounted () {
    this.code.parentNode.after(this.$el)
    this.code.parentNode.remove()
  }
}
</script>

