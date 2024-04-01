<script setup>
import { API } from '../api/api'
import MarkdownVue from '@/components/Markdown.vue'
</script>
<template>
  <div class="gap-2 h-full justify-between">
    <div class="text-xl font-medium flex justify-between items-center gap-2">
      Knowledge
      <div class="stat-desc flex gap-2 items-center btn btn-sm" @click="reloadStatus">
        <i class="fa-solid fa-rotate-right"></i> Update
      </div>
    </div>
    <div class="flex flex-col gap-2">
      <div class="text-xs flex gap-2 items-center">
        <i class="fa-solid fa-sliders"></i>
        <div class="flex gap-2 items-center">Search type: 
          <select v-model="documentSearchType" class="w-20 select-bordered select select-xs">
            <option value="similarity">similarity</option>
          </select>
        </div>
        <div class="flex gap-2 items-center">Document count:
          <input type="text" v-model="documentCount" class="w-20 input-bordered input input-xs  max-w-xs" />
        </div>
        <div class="flex gap-2 items-center">Document score (0-1):
          <input type="text" v-model="cutoffScore" class="w-20 input-bordered input input-xs  max-w-xs" />
        </div>
        <button class="btn btn-sm" @click="saveKnowledgeSettings">
          <i class="fa-solid fa-floppy-disk"></i>
        </button>
      </div>
      <label class="input input-bordered flex items-center gap-2">
        <select class="select select-xs w-20" v-model="searchType">
          <option value="embeddings">Embeddings</option>
          <option value="source">Source</option>
        </select>
        <input type="text" class="grow" placeholder="Search in knowledge"
          @keypress.enter="onKnowledgeSearch"
          v-model="searchTerm" />
        <i class="fa-solid fa-magnifying-glass" @click="onKnowledgeSearch"></i>
      </label>
      <div>{{ searchResults?.settings }}</div>
      <div class="grid grid-cols-3 gap-2">
        <span class="border p-2 border-info cursor-pointer rounded-md bg-base-300 indicator"
            v-for="doc,ix in searchResults?.documents" :key="ix"
            @click="showDoc = doc"
        >
          <span class="indicator-item badge badge-primary flex gap-2">
            <i class="fa-solid fa-gauge"></i>
            {{ doc.metadata.relevance_score }}
          </span>
          {{ doc.metadata.source.split("/").reverse().slice(0, 2).join(" ") }}
        </span>
      </div>
    </div>
    <div class="alert alert-error" >
      {{ status?.empty }}: Invalid indexed docs
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
      <div class="border p-4 rounded-md" v-if="status?.pending_files?.length">
        <div class="text-xl font-medium">Pending files</div>
        <div v-if="status?.pending_files?.length">{{ status?.pending_files }}</div>
        <div class="text-xs text-info" v-else>All files indexed</div>
        <div class="flex gap-2" v-if="status?.pending_files?.length">
          <button class="btn btn-primary btn-sm" @click="reloadKnowledge">
            <i class="fa-solid fa-circle-info"></i> Index files now
          </button>
        </div>
      </div>
      <div class="text-xl flex gap-2 items-center mt-2">
        <i class="fa-solid fa-hand"></i> Manual folder indexing
      </div>
      <div class="text-xs">Allows to index new floders or re-index existing ones</div>
      <label class="input input-bordered flex items-center gap-2">
        <input type="text" class="grow" :placeholder="projectPath" v-model="folderFilter" />
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
    <dialog class="modal modal-bottom sm:modal-middle modal-open" v-if="showDoc">
      <div class="modal-box flex flex-col gap-2">
        <div class="font-bold text-wrap">{{ showDoc.metadata.source }}</div>
        <MarkdownVue class="prose max-h-60 overflow-auto" :text="showDocPreview" />
        <pre><code class="language-json text-wrap">{{ JSON.stringify(showDoc.metadata, null, 2)  }}</code></pre>
        <div class="modal-action">
          <form class="flex flex-gap" method="dialog">
            <button class="btn btn-error" @click="unIndexFile(showDoc)">
              Drop file
            </button>
            <button class="btn" @click="showDoc = null">Close</button>
          </form>
        </div>
      </div>
    </dialog>
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
      folderFilter: null,
      searchTerm: null,
      searchResults: null,
      showDoc: null,
      searchType: "embeddings",
      documentSearchType: API.lastSettings.knowledge_search_type,
      cutoffScore: API.lastSettings.knowledge_context_cutoff_relevance_score,
      documentCount: API.lastSettings.knowledge_search_document_count
    }
  },
  created() {
    this.reloadStatus()
  },
  computed: {
    projectPath () {
      return API.lastSettings.project_path
    },
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
    },
    showDocPreview () {
      const codePreview = this.showDoc.page_content.split("Code:")[1]
      return codePreview || "```" + this.showDoc.metadata.language + 
                            `\n${this.showDoc.page_content}\n` + "```"
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
      this.reloadStatus()
      this.loading = false
    },
    async onKnowledgeSearch () {
      const { searchTerm,
              searchType,
              documentSearchType,
              cutoffScore,
              documentCount
      } = this
      const { data } = await API.knowledge.search({ searchTerm,
                                                    searchType,
                                                    documentSearchType,
                                                    cutoffScore,
                                                    documentCount
                                                  })
      this.searchResults = data 
    },
    async unIndexFile(doc) {
      await API.knowledge.delete([doc.metadata.source])
      this.showDoc = null
      this.onKnowledgeSearch()
    },
    async saveKnowledgeSettings () {
      await API.settings.read()
      API.settings.write({
        ...API.lastSettings,
        knowledge_search_type: this.documentSearchType,
        knowledge_context_cutoff_relevance_score: this.cutoffScore,
        knowledge_search_document_count: this.documentCount
      })
    }
  }
}
</script>