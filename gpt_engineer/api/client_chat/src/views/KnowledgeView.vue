<script setup>
import { API } from '../api/api'
</script>
<template>
  <div class="flex flex-col gap-2 h-full justify-between">
    <div class="text-xl font-medium flex justify-between items-center gap-2">
      Knowledge
      <div class="stat-desc flex gap-2 items-center btn btn-sm" @click="reloadStatus">
        <i class="fa-solid fa-rotate-right"></i> Update
      </div>
    </div>
    <div class="stats">
      <div class="stat">
        <div class="stat-figure text-secondary">
          <i class="fa-lg fa-solid fa-file"></i>
        </div>
        <div class="stat-title">Documents</div>
        <div class="stat-value">{{ status?.doc_count }}</div>
        <div class="stat-desc"></div>
      </div>

      <div class="stat">
        <div class="stat-figure text-secondary">
          <i class="fa-lg fa-solid fa-puzzle-piece"></i>
        </div>
        <div class="stat-title">Indexed files</div>
        <div class="stat-value">{{ status?.file_count }}</div>
        <div class="stat-desc"></div>
      </div>

      <div class="stat">
        <div class="stat-figure text-secondary">
          <i class="fa-lg fa-solid fa-clock"></i>
        </div>
        <div class="stat-title">Last refresh</div>
        <div class="stat-value text-wrap text-sm">{{ lastRefresh }}</div>
      </div>
    </div>

    <div class="p-4 flex flex-col gap-2 grow">
      <div class="text-xl font-medium">Pending files</div>
      <div v-if="status?.pending_files?.length">{{ status?.pending_files }}</div>
      <div class="text-xs text-info" v-else>All files indexed</div>
      <div class="flex gap-2" v-if="status?.pending_files?.length">
        <button class="btn btn-primary btn-sm" @click="reloadKnowledge">
          <i class="fa-solid fa-circle-info"></i> Index files now
        </button>
      </div>
      <div class="text-xl">
        Reload folder
      </div>
      <label class="input input-bordered flex items-center gap-2">
        <input type="text" class="grow" placeholder="Search" v-model="folderFilter" />
        <i class="fa-solid fa-magnifying-glass"></i>
      </label>
      <div class="dropdown dropdown-open" v-if="folderResulst && !folderToReload">
        <div class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-fit">
          <ul>
            <li class="" v-for="folder in folderResulst" :key="folder"
              @click="folderToReload = folder"
            >
              <a>{{ folder }}</a></li>
          </ul>
        </div>
      </div>
      <div class="pl-4 flex gap-2 items-center " v-if="folderToReload">
        <i class="fa-2xl fa-solid fa-folder"></i>
        <input type="text" v-model="folderToReload" class="grow input input-md input-bordered" />
        <button class="btn btn-warning" v-if="folderToReload" @click="reloadFolder">
          <i class="fa-solid fa-rotate-right"></i>
      </button>
      </div>
    </div>
    <div class="text-xs font-bold py-2">
      <div class="text-xl">Ignored folders:</div>
      <div class="grid grid-cols-4 gap-2">
        <span class="badge badge-xs badge-warning" v-for="folder, ix in API.lastSettings?.knowledge_file_ignore.split(',')" :key="ix">
          {{ folder }}
        </span>
      </div>
      <div class="text-xs">Change this list on settings</div>
    </div>
  </div>
</template>
<script>
import moment from 'moment'

export default {
  data() {
    return {
      documents: 0,
      embeddings: 0,
      status: null,
      folderToReload: null,
      loading: false,
      folderFilter: null
    }
  },
  created() {
    this.reloadStatus()
  },
  computed: {
    lastRefresh() {
      if (this.status?.last_update) {
        const ts = parseInt(this.status.last_update, 10) * 1000
        return moment(new Date(ts)).fromNow()
      }
      return null
    },
    folderResulst () {
      if ((this.folderFilter?.length || 0) < 3) {
        return []
      }
      const query = this.folderFilter.toLowerCase()
      return this.status?.folders?.filter(f => f.toLowerCase().indexOf(query) !== -1)
        .slice(0, 20)
    }
  },
  watch: {
    folderFilter () {
      this.folderToReload = null
    }
  },
  methods: {
    async reloadStatus() {
      const { data } = await API.knowledge.status()
      this.status = data
    },
    async reloadFolder () {
      this.loading = true
      try {
        await API.knowledge.reloadFolder(this.folderToReload)
        this.folderToReload = null
        this.folderFilter = null
      } catch{}
      this.loading = false
    },
    async reloadKnowledge () {
      this.loading = true
      try {
        await API.knowledge.reload()
      } catch{}
      this.loading = false
    }

  }
}
</script>