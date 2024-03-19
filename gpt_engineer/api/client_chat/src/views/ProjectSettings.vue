<template>
  <div class="form-control w-full">
    <div class="text-xl font-medium my-2">GPT Settings</div>
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
      settings: null,
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