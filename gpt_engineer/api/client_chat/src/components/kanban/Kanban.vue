<script setup>
import draggable from "vuedraggable"
import TaskCard from "./TaskCard.vue"
import { API } from '../../api/api'
import ChatViewVue from '../../views/ChatView.vue'
</script>
<template>
  <ChatViewVue :openChat="chat" v-if="chat" @chats="chat = null" ></ChatViewVue>
  <div class="flex flex-col gap-2 h-full" v-else>
    <div class="dropdown">
      <div tabindex="0" class="click text-2xl flex gap-2 items-center">
        {{ board || defBoard }}
        <i class="fa-solid fa-sort-down"></i>
      </div>
      <ul tabindex="0" class="dropdown-content menu bg-base-200 rounded-md w-60 z-50">
        <li v-for="tasksBoard in boards" :key="tasksBoard">
          <a>{{ tasksBoard }}</a>
        </li>
      </ul>
    </div>
    <div class="flex justify-center grow overflow-auto">
      <div class="min-h-screen min-w-full overflow-x-scroll">
        <div
          v-for="column in columns"
          :key="column.title"
          class="bg-neutral rounded-lg px-3 py-3 column-width rounded mr-4"
        >
          <p class="text-neutral-content font-semibold font-sans tracking-wide text-sm flex justify-between items-center">
            {{column.title}}
            <button class="btn btn-sm" @click="newChat (column.title)">
              <i class="fa-solid fa-plus"></i>
            </button>
          </p>
          <draggable 
            v-model="column.tasks" 
            :group="column.title" 
            @start="drag=true" 
            @end="drag=false" 
            :item-key="column.title">
            <template #item="{element}">
              <task-card
                :task="element"
                class="mt-3 cursor-move"
                @click="chat = element"
              ></task-card>
            </template>
          </draggable>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
const unassigned = "<none>"
export default {
  data() {
    return {
      chat: null,
      chats: [],
      board: unassigned
    };
  },
  async created () {
    this.chats = (await API.chats.list())
                    .map(c => ({
                      ...c,
                      board: c.board || unassigned,
                      column: c.column || unassigned
                    }))
  },
  computed: {
    boards () {
      return [...new Set(this.chats?.map(c => c.board))]             
    },
    columns () {
      const columns = [...new Set(this.chats?.map(c => c.column))]
      return columns.map(col => ({
        title: col,
        tasks: this.chats.filter(c => c.column === col)
      }))
    }
  },
  methods: {
    newChat (column) {
      this.chat = {
        name: "New chat",
        board: this.board,
        column,
        column_ix: 0
      }
    }
  }
};
</script>

<style scoped>
.column-width {
  min-width: 320px;
  width: 320px;
}
/* Unfortunately @apply cannot be setup in codesandbox, 
but you'd use "@apply border opacity-50 border-blue-500 bg-gray-200" here */
.ghost-card {
  opacity: 0.5;
  background: #F7FAFC;
  border: 1px solid #4299e1;
}
</style>
