<script setup>
import { API } from './api/api'
import ChatViewVue from "./views/ChatView.vue";
import ProjectSettingsVue from "./views/ProjectSettings.vue";
</script>

<template>
  <div class="w-full h-screen max-w-screen flex flex-col">
    <div class="alert alert-sm text-xs alert-error" v-if="projectPathError">
      {{ projectPathError }}
    </div>
    <div class="grow flex flex-col" v-if="projectPath">
      <div role="tablist" class="tabs tabs-lifted">
        <a role="tab" :class="['tab', tabIx === 0 && 'tab-active']"
          @click="tabIx = 0"
        >
          <div class="font-medium flex gap-2 items-center">
            <i class="fa-regular fa-comments"></i>
          </div>
        </a>
        <a role="tab" :class="['tab flex items-center gap-2', tabIx === 1 && 'tab-active']"
          @click="tabIx = 1"
        >
          <i class="fa-solid fa-brain"></i>
          {{ projectPath }}
        </a>
        <a class="tab">
          <div>
            <label for="my_modal_6" class="btn btn-sm btn-warning">
              <i class="fa-regular fa-folder-open"></i>
            </label>

            <!-- Put this part before </body> tag -->
            <input type="checkbox" id="my_modal_6" class="modal-toggle" />
            <div class="modal" role="dialog">
              <div class="modal-box">
                <h3 class="font-bold text-lg">Open project</h3>
                <input type="text" class="input input-bordered w-full" v-model="newProject" />
                <div class="modal-action">
                  <label for="my_modal_6" class="btn" @click="onOpenProject">
                    Open
                  </label>
                  <label class="modal-backdrop" for="my_modal_6">Close</label>
                </div>
              </div>
            </div>
          </div>
        </a>
      </div>
      <div class="grow relative overflow-auto">
        <ChatViewVue v-if="tabIx === 0" />
        <ProjectSettingsVue class="abolsute top-0 left-0 w-full" v-if="tabIx === 1" />
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
      projectPathError: null
    }
  },
  async created () {
    this.projectPath = this.getProjectPath() 
    this.newProject = this.projectPath
    await API.settings.read()
    if (API.lastSettings.project_path !== this.projectPath) {
      this.projectPathError = "Fix project 'project_path' in settings to match " + this.projectPath
      this.tabIx = 1
    }
  },
  methods: {
    getProjectPath () {
      const projectPath = (window.location.search
              .slice(1).split("&")
              .map(p => p.split("="))
              .find(([k, v]) => k === "project_path")||[])[1]|| "No project selected"
      return decodeURIComponent(projectPath)
    },
    onOpenProject () {
      window.location = `${window.location.origin}?project_path=${this.newProject}`
    }
  }

}
</script>