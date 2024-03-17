<script setup>
</script>
<template>
  <div class="p-8 flex flex-col">
    <div class="text-xl">CODX GPT-ENGINEER</div>
    <div v-if="chat">
      
    </div>
    <button class="btn btn-wide" @click="newChat">
      New chat
    </button>
  </div>
</template>
<script>
export default {
  data() {
    return {
      chat: null
    }
  },
  methods: {
    newChat () {
      this.chat = {}
    }
  }
}
</script>