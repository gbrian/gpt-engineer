<script setup>
import VueMermaidString from 'vue-mermaid-string'
</script>

<template>
  <main class="w-full h-full flex gap-2">
    <textarea class="w-1/3 h-full" v-model="diagram" v-if="showEditor">
    </textarea>
    <div class="grow">
      <vue-mermaid-string :value="diagram" />
    </div>
  </main>
</template>
<script>
export default {
  props: ['showEditor', 'diagram']
}
</script>
