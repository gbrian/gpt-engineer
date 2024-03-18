<template>
  <div class="form-control w-full p-4">
    <div class="flex justify-between mb-2" v-for="(value, key) in settings" :key="key">
      <div class="label-text">{{ key }}</div>
      <div class="w-1/2">
        <input v-if="typeof value === 'boolean'" type="checkbox" v-model="settings[key]" class="toggle" />
        <input v-else type="text" v-model="settings[key]" class="input input-bordered w-full" />
      </div>
    </div>
    <div class="flex gap-2 justify-end">
      <button type="button" @click="reloadSettings" class="btn btn-outline btn-accent">Reload</button>
      <button type="submit" class="btn btn-primary" @click="saveSettings">Save</button>
    </div>
  </div>
</template>

<script>
import { API } from '../api/api'
export default {
  data() {
    return {
      settings: {
        openai_api_key: '',
        openai_api_base: '',
        knowledge_extract_document_tags: false,
        knowledge_search_type: '',
        knowledge_search_document_count: 0,
        temperature: '',
        model: '',
        project_path: '',
        chat_mode: false,
        steps_config: '',
        improve_mode: false,
        update_summary: false,
        api: true,
        role: '',
        lite_mode: false,
        use_git: false,
        prompt: false,
        file_selector: false,
        prompt_file: false,
        verbose: false,
        test: '',
        build_knowledge: false,
        port: '',
        azure_endpoint: '',
        find_files: false,
      },
    };
  },
  async created () {
    this.reloadSettings()
  },
  methods: {
    async reloadSettings() {
      const { data: settings } = await API.settings.read()
      this.settings = settings
    },
    async saveSettings() {
      await API.settings.write(this.settings)
      this.reloadSettings()
    },
  },
};
</script>