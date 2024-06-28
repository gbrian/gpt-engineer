<script setup>
import { API } from './api/api'
import ChatViewVue from "./views/ChatView.vue";
import KnowledgeViewVue from './views/KnowledgeView.vue';
import ProfileViewVue from './views/ProfileView.vue';
import ProjectSettingsVue from "./views/ProjectSettings.vue";
</script>

<template>
  <div class="w-full h-screen max-w-screen flex flex-col bg-base-300 p-2 dark relative" data-theme="dark">
    <div class="alert alert-error text-xs font-bold text-white" v-if="!lastSettings?.openai_api_key">
      Please fix your settings. No AI key present
    </div>
    <div class="flex gap-2 items-center justify-between">
      <div v-if="validProject">
        <div class="flex gap-2 items-center">
          <div class="click badge badge-xs my-2 flex gap-2 badge-warning badge-ouline p-2"
            @click="openProject(lastSettings.parent_project + '/.gpteng')"
            v-if="lastSettings.parent_project">
            <i class="fa-solid fa-caret-up"></i> {{ lastSettings.parent_project.split("/").reverse()[0] }} 
          </div>
          <div>CODX</div>
          <div class="badge my-2 flex gap-2 badge-primary badge-ouline p-2 flex gap-2 items-center">
            <i class="fa-regular fa-folder-open"></i>
            <div class="-mt-1">
              {{ gptengPath.split("/").reverse()[1] }}
            </div> 
          </div>
        </div>
        <div class="flex gap-2" v-if="subProjects">
          <div tabindex="0" class="click badge badge-info text-white flex gap-1 items-center"
            v-for="project in subProjects" :key="project"
              @click="openProject(project + '/.gpteng')"
          >
            <i class="fa-solid fa-folder"></i>
            {{ project.split("/").reverse()[0] }} 
          </div>
        </div>
      </div>
      <div class="flex gap-2 items-center">
        <div>
          <label for="my_modal_6" class="btn btn-sm btn-warning" @click="showOpenProjectModal = true">
            <i class="fa-regular fa-folder-open"></i>
          </label>
        </div>
      </div>
    </div>
    <progress :class="['progress progress-success w-full', liveRequests ? '': 'opacity-0']"></progress>
    <div class="alert alert-warning flex gap-2 justify-center" v-if="!validProject">
      No project found at <span class="">"{{gptengPath}}"</span>
      <button class="btn btn-sm" v-if="gptengPath" @click="createNewProject">
        <i class="fa-solid fa-plus"></i> New
      </button>
      <button class="btn btn-sm" @click="showOpenProjectModal = true">
        <i class="fa-regular fa-folder-open"></i> Open
      </button>
    </div>
    <div role="tablist" class="tabs tabs-lifted bg-base-100 rounded-md" v-if="validProject">
      <a role="tab" :class="['tab flex items-center gap-2', tabIx === 0 ? tabActive: tabInactive]"
        @click="tabIx = 0"
      >
        <div class="font-medium flex gap-2 items-center">
          <i class="fa-solid fa-comments"></i>
          Chat
        </div>
      </a>
      <a role="tab" :class="['tab flex items-center gap-2', tabIx === 1 ? tabActive: tabInactive]"
        @click="tabIx = 1"
      >
        <i class="fa-solid fa-book"></i>
        Knowledge
      </a>
      <a role="tab" :class="['tab flex items-center gap-2', tabIx === 2 ? tabActive: tabInactive]"
        @click="tabIx = 2"
      >
        <i class="fa-solid fa-brain"></i>
        Setting
      </a>
      <a role="tab" :class="['tab flex items-center gap-2', tabIx === 3 ? tabActive: tabInactive]"
        @click="tabIx = 3"
      >
      <i class="fa-solid fa-id-card-clip"></i>
        Profiles
      </a>
    </div>
    <div class="grow relative overflow-auto bg-base-100 px-4 py-2 " v-if="validProject">
      <ChatViewVue v-if="tabIx === 0" />
      <KnowledgeViewVue class="abolsute top-0 left-0 w-full" v-if="tabIx === 1" />
      <ProjectSettingsVue class="abolsute top-0 left-0 w-full" v-if="tabIx === 2" />
      <ProfileViewVue class="abolsute top-0 left-0 w-full" v-if="tabIx === 3" />
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
    <div class="toast toast-end">
      <div class="bg-error text-white overflow-auto rounded-md p-2 max-w-96 max-h-60 text-xs"
        v-if="lastError" @click="lastError = null">
        <pre><code>ERROR: {{ lastError }}</code></pre>
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
      lastSettings: null,
      tabActive: 'text-info bg-base-100',
      tabInactive: 'text-warning bg-base-300 opacity-50 hover:opacity-100',
      lastError: null
    }
  },
  async created () {
    API.axiosRequest.interceptors.response.use(
      (response) => response,
      (error) => {
        this.lastError = error.response.data.join("\n")
        console.error("API ERROR:", this.lastError);
      });
    await this.init()
    setInterval(() => {
      this.liveRequests = API.liveRequests
      this.lastSettings = API.lastSettings
    }, 200)
  },
  computed: {
    validProject () {
      return this.lastSettings?.gpteng_path &&
        this.lastSettings?.project_path
    },
    subProjects () {
      if (!Array.isArray(this.lastSettings?.sub_projects)) {
        return this.lastSettings?.sub_projects?.split(",")
      }
      return this.lastSettings?.sub_projects
    }
  },
  methods: {
    async init () {
      this.gptengPath = this.getProjectPath()
      try {
        await API.settings.read()
      } catch {}
      if (!API.lastSettings ||
          API.lastSettings.gpteng_path !== this.gptengPath ||
          !API.lastSettings?.openai_api_key 
      ) {
        this.tabIx = 2
      }
    },
    getProjectPath () {
      return API.lastSettings?.gpteng_path
    },
    onOpenProject () {
      if (!this.newProject.endsWith("/.gpteng")) {
        this.newProject += "/.gpteng"
      }
      this.openProject(this.newProject)
    },
    openProject (path) {
      window.location = `${window.location.origin}?gpteng_path=${encodeURIComponent(path)}`
    },
    async createNewProject () {
      const { data: { gpteng_path } } = await API.project.create(this.getProjectPath())
      this.openProject(gpteng_path)
    }
  }

}
</script>