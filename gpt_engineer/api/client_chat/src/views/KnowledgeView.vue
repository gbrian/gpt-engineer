<script setup>
import { API } from '../api/api'
import MarkdownVue from '@/components/Markdown.vue'
</script>
<template>
  <div class="gap-2 h-full justify-between">
    <div class="text-xl font-medium flex justify-between items-center gap-2">
      Knowledge
      <div class="grow"></div>
      <button class="btn btn-sm" @click="settings.watching = !settings?.watching">
        <span class="label-text mr-2">Watch changes</span> 
        <input type="checkbox" class="toggle toggle-sm toggle-primary" :checked="settings?.watching"
          @change="toggleWatch" :disabled="!settings" />
      </button>
      
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
        <div class="flex gap-2 items-center">Keywords:
          <input type="checkbox" v-model="enableKeywords" class="w-20 checkbox checkbox-xs" />
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
        <div class="stat-figure text-info">
          <i class="fa-solid fa-book"></i>
        </div>
        <div class="stat-title">Keywords</div>
        <div class="stat-value">{{ status?.keyword_count }}</div>
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
      <div class="border p-4 rounded-md">
        <div class="text-xl font-medium">Pending files</div>
        <div class="max-h-60 overflow-auto" v-if="status?.pending_files?.length">
          <div class="text-xs" v-for="file in status?.pending_files" :key="file">
            <div class="flex gap-2">
              {{ file.replace(projectPath, "") }}
              <button class="btn btn-xs" @click="reloadPath(file)" >
                <i class="fa-regular fa-circle-play"></i>
              </button>
            </div>
          </div>
        </div>
        <div class="text-xs text-info" v-else>All files indexed</div>
        <div class="flex gap-2">
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
    <dialog class="modal modal-bottom sm:modal-middle modal-open" v-if="showDoc" @click="showDoc = null">
      <div class="modal-box flex flex-col gap-2 w-full max-w-full">
        <div class="font-bold text-wrap">{{ showDoc.metadata.source }}</div>
        <div class="flex flex-col gap-2 grow">
          <MarkdownVue class="prose h-60 overflow-auto" :text="showDocPreview" v-if="false" />
          <pre>{{ showDoc.page_content }}</pre>
          <div>
            <span class="badge badge-primary badge-xs mr-2" v-for="keyword in showDoc.metadata.keywords?.split(',')" :key="keyword">
              {{ keyword }}  
            </span>
          </div>
          <pre class="h-1/4"><code class="language-json text-wrap text-xs">{{ JSON.stringify(showDoc.metadata, null, 2)  }}</code></pre>
        </div>
        <div>
          <form class="flex gap-2" method="dialog">
            <button class="btn btn-info text-white" @click="reIndexFile(showDoc)">
              Re-index
            </button>
            <button class="btn btn-info text-white" @click="extractKeywords(showDoc)">
              Keywords
            </button>
            <button class="btn btn-error text-white" @click="unIndexFile(showDoc)">
              Drop file
            </button>
            <div class="grow"></div>
            <button class="btn" @click="showDoc = null">
              Close
            </button>
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
      documentCount: API.lastSettings.knowledge_search_document_count,
      enableKeywords: API.lastSettings.knowledge_extract_document_tags
    }
  },
  created() {
    this.reloadStatus()
  },
  computed: {
    settings () {
      return API.lastSettings
    },
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

      const allFolders = [...this.status?.pending_files||[], ...this.status?.folders||[]]
      return allFolders.filter((f, ix, arr) => arr.findIndex(f) === ix && f.toLowerCase().indexOf(query) !== -1)
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
      this.reloadPath(this.folderToReload)
    },
    async reloadPath(path) {
      this.loading = true
      try {
        await API.knowledge.reloadFolder(path)
        await this.reloadStatus()
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
    async reIndexFile(doc) {
      await API.knowledge.reloadFolder([doc.metadata.source])
      this.onKnowledgeSearch()
    },
    async extractKeywords(doc) {
      const { data } = await API.knowledge.keywords(doc)
      this.showDoc = data
    },
    async saveKnowledgeSettings () {
      await API.settings.read()
      API.settings.write({
        ...API.lastSettings,
        knowledge_search_type: this.documentSearchType,
        knowledge_context_cutoff_relevance_score: this.cutoffScore,
        knowledge_search_document_count: this.documentCount,
        knowledge_extract_document_tags: this.enableKeywords
      })
    },
    async toggleWatch () {
      if (!API.settings) {
        return
      }
      if (API.settings.watching) {
        await API.project.unwatch()
      } else {
        await API.project.watch()
      }
      API.settings.read()
    }
  }
}
</script>