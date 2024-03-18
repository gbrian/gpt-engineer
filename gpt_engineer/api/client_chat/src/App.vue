<script setup>
import ChatViewVue from "./views/ChatView.vue";
import ProjectSettingsVue from "./views/ProjectSettings.vue";
</script>

<template>
  <div class="w-full h-screen max-w-screen flex flex-col">
    <div role="tablist" class="tabs tabs-lifted">
      <a role="tab" :class="['tab', tabIx === 0 && 'tab-active']"
        @click="tabIx = 0"
      >
        <i class="fa-solid fa-house"></i>
      </a>
      <a role="tab" :class="['tab', tabIx === 1 && 'tab-active']"
        @click="tabIx = 1"
      >
        <i class="fa-solid fa-gear"></i>
      </a>
    </div>
    <div class="grow relative overflow-auto">
      <ChatViewVue v-if="tabIx === 0" />
      <ProjectSettingsVue class="abolsute top-0 left-0 w-full" v-if="tabIx === 1" />
    </div>
  </div>
</template>
<script>
export default {
  data () {
    return {
      tabIx: 0
    }
  }
}
</script>