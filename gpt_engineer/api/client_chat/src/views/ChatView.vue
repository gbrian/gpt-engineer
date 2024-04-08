<script setup>
import Chat from '@/components/chat/Chat.vue'
</script>
<template>
  <div class="flex flex-col gap-2 h-full justify-between" v-if="chat">
    <div class="text-xl flex gap-2 items-center px-2">
      CODX
      <input type="text" class="input input-xs input-bordered w-40" v-model="chat.name" />
      <div class="dropdown">
        <div tabindex="0" role="button" class="btn btn-sm m-1">Add profiles</div>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li @click="addProfile(p)" v-for="p in profiles" :key="p"
            ><a><i class="fa-solid fa-plus"></i> {{ p }}</a>
          </li>
        </ul>
      </div>
      <button class="btn btn-primary btn-xs" @click="newChat">
        <i class="fa-solid fa-plus"></i>
      </button>
      <button class="btn btn-xs" @click="saveChat">
        <i class="fa-solid fa-floppy-disk"></i>
      </button>
      <button class="btn btn-xs btn-error" @click="deleteChat">
        <i class="fa-solid fa-trash"></i>
      </button>
      <div class="grow"></div>
      <div class="dropdown dropdown-end">
        <div tabindex="0" role="button btn-sm" class="btn btn-xs">
          <i class="fa-solid fa-folder-tree"></i>
        </div>
        <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
          <li v-for="openChat in chats" :key="openChat" @click="loadChat(openChat)" >
            <a>{{ openChat }}</a>
          </li>
        </ul>
      </div>
    </div>
    <div class="p-2">
      <button class="btn btn-sm mr-2" @click="addFile = ''">
        <i class="fa-solid fa-file-circle-plus"></i>
      </button>
      <span class="cursor-pointer mr-2 hover:underline group text-primary"
        v-for="file in chat.profiles" :key="file" :title="file"
        @click="showFile = file"
      >
        <i class="fa-solid fa-rectangle-list"></i>
        {{ file.split("/").reverse()[0] }}
      </span>

      <span class="cursor-pointer mr-2 hover:underline group text-secondary"
        v-for="file in chat.file_list" :key="file" :title="file"
        @click="showFile = file"
      >
        <i class="fa-solid fa-file"></i>
        {{ file.split("/").reverse()[0] }}
      </span>
    </div>
    <Chat :chat="chat" @change="loadChat(chat.name)" v-if="chat"/>
    <div class="modal modal-open" role="dialog" v-if="showFile || addFile !== null">
      <div class="modal-box flex flex-col gap-4 p-4">
        <h3 class="font-bold text-lg" v-if="showFile">
          This file belongs to the task context:
          <div class="font-thin">{{ showFile }}</div>
        </h3>
        <div v-else>
          <input type="text" class="input input-bordered w-full" v-model="addFile" placeholder="Add file to context, full path" />
        </div>
        <div class="flex gap-2 justify-center">
          <button class="btn btn-error" @click="removeFileFromContext" v-if="showFile">
            Remove
          </button>
          <button class="btn btn-primary" @click="addFileToContext" v-else>
            Add
          </button>
          <button class="btn" @click="addFile = showFile = null">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
import { API } from '../api/api'
export default {
  data() {
    return {
      chat: null,
      chats: [],
      profiles: null,
      showFile: null,
      addFile: null
    }
  },
  async created () {
    this.chats = await API.chats.list()
    if (this.chats.length) {
      this.chat = await API.chats.loadChat(this.chats.reverse()[0])
    } else {
      this.chat = await API.chats.newChat()
      this.chats.push(this.chat.name)
    }
    this.loadProfiles()
  },
  methods: {
    async loadProfiles () {
      try {
        const { data } = await API.profiles.list()
        this.profiles = data
      } catch {}
    },
    newChat () {
      this.chat = API.chatManager.newChat()
    },
    
    async saveChat () {
      return API.chats.save(this.chat)
    },
    deleteChat () {
      API.chatManager.deleteChat(this.chat)
      this.chats = API.chatManager.getChats()
      this.newChat()
    },
    async loadChat (newChat) {
      this.chat = await API.chats.loadChat(newChat)
    },
    async removeFileFromContext () {
      this.chat.profiles = this.chat.profiles.filter(f => f !== this.showFile) 
      this.chat.file_list = this.chat.file_list.filter(f => f !== this.showFile)
      await this.saveChat()
      await this.loadChat(this.chat.name)
      this.showFile = null
    },
    async addFileToContext () {
      this.chat.file_list = [...this.chat.file_list, this.addFile]
      await this.saveChat()
      await this.loadChat(this.chat.name)
      this.showFile = null
      this.addFile = null
    },
    async addProfile (profile) {
      if (this.chat.profiles.find(f => f.endsWith(profile))) {
        return
      }
      this.chat.profiles = [...this.chat.profiles, profile]
      await this.saveChat()
      await this.loadChat(this.chat.name)
    }
  }
}
</script>