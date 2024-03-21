<script setup>
import { API } from './api/api'
import ChatViewVue from "./views/ChatView.vue";
import KnowledgeViewVue from './views/KnowledgeView.vue';
import ProjectSettingsVue from "./views/ProjectSettings.vue";
</script>

<template>
  <div class="w-full h-screen max-w-screen flex flex-col bg-base-300 p-2">
    <div class="badge badge-xs my-2 flex gap-2 badge-primary badge-ouline p-2" v-if="gptengPath">
      <i class="fa-solid fa-location-dot"></i> {{ gptengPath }}
    </div>
    <progress :class="['progress progress-success w-full', liveRequests ? '': 'opacity-0']"></progress>
    <div class="alert alert-warning flex gap-2 justify-center" v-if="!lastSettings">
      No project found at <span class="">"{{gptengPath}}"</span>
      <button class="btn btn-sm" v-if="gptengPath" @click="createNewProject">
        <i class="fa-solid fa-plus"></i> New
      </button>
      <button class="btn btn-sm" @click="showOpenProjectModal = true">
        <i class="fa-regular fa-folder-open"></i> Open
      </button>
    </div>
    <div role="tablist" class="tabs tabs-lifted bg-base-100 rounded-md" v-if="lastSettings">
      <a role="tab" :class="['tab', tabIx === 0 && 'tab-active']"
        @click="tabIx = 0"
      >
        <div class="font-medium flex gap-2 items-center">
          <i class="fa-regular fa-comments"></i>
          Tasks
        </div>
      </a>
      <a role="tab" :class="['tab flex items-center gap-2', tabIx === 1 && 'tab-active']"
        @click="tabIx = 1"
      >
        <i class="fa-solid fa-book"></i>
        Knowledge
      </a>
      <a role="tab" :class="['tab flex items-center gap-2', tabIx === 1 && 'tab-active']"
        @click="tabIx = 2"
      >
        <i class="fa-solid fa-brain"></i>
        GPT Settings
      </a>
      <a class="tab">
        <div>
          <label for="my_modal_6" class="btn btn-sm btn-warning" @click="showOpenProjectModal = true">
            <i class="fa-regular fa-folder-open"></i>
          </label>
        </div>
      </a>
    </div>
    <div class="grow relative overflow-auto bg-base-100 px-4 py-2 " v-if="lastSettings">
      <ChatViewVue v-if="tabIx === 0" />
      <KnowledgeViewVue class="abolsute top-0 left-0 w-full" v-if="tabIx === 1" />
      <ProjectSettingsVue class="abolsute top-0 left-0 w-full" v-if="tabIx === 2" />
    </div>
    <div class="modal modal-open" role="dialog" v-if="showOpenProjectModal">
      <div class="modal-box">
        <h3 class="font-bold text-lg">Open project</h3>
        <input type="text" class="input input-bordered w-full"
          :placeholder="gptengPath || 'Project\'s absolute path'" v-model="newProject" />
        <div class="modal-action">
          <label for="my_modal_6" class="btn" @click="onOpenProject">
            Open
          </label>
          <label class="modal-backdrop" for="my_modal_6">Close</label>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  data () {
    return {
      tabIx: 0,
      newProject: null,
      gptengPath: null,
      showOpenProjectModal: false,
      liveRequests: null,
      lastSettings: null
    }
  },
  async created () {
    await this.init()
    setInterval(() => {
      this.liveRequests = API.liveRequests
      this.lastSettings = API.lastSettings
    }, 200)
  },
  computed: {
  },
  methods: {
    async init () {
      this.gptengPath = this.getProjectPath()
      try {
        await API.settings.read()
      } catch {}
      if (!API.lastSettings || API.lastSettings.gpteng_path !== this.gptengPath) {
        this.tabIx = 1
      }
    },
    getProjectPath () {
      const gptengPath = window.location.search
              .slice(1).split("&")
              .map(p => p.split("="))
              .find(([k, v]) => k === "gpteng_path")
      return gptengPath ? decodeURIComponent(gptengPath[1]) : null
    },
    onOpenProject () {
      window.location = `${window.location.origin}?gpteng_path=${encodeURIComponent(this.newProject)}`
    },
    async createNewProject () {
      await API.project.create()
      window.location.reload()
    }
  }

}
</script>