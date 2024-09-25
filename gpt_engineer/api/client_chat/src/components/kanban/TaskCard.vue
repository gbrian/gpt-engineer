<template>
  <div class="bg-base-100 shadow rounded pb-5 border border-base-300 flex flex-col gap-2">
    <div class="bg-auto bg-no-repeat bg-center h-28 bg-base-300"
      :style="`background-image: url(${image.src})`"
      v-if="image"
    >
    </div>
                
    <div class="p-2 flex flex-col gap-2">
      <div class="flex justify-between">
        <p class="font-semibold font-sans tracking-wide text-sm">{{task.name}}</p>

        <img
          class="w-6 h-6 rounded-full ml-3"
          src="https://pickaface.net/gallery/avatar/unr_sample_161118_2054_ynlrg.png"
          alt="Avatar"
        >
      </div>
      <p class="text-xs">{{ description  }}</p>
      <div class="flex mt-4 justify-between items-center">
        <span class="text-sm text-gray-600">{{task.updated_at}}</span>
        <badge v-if="task.type" :color="badgeColor">{{task.type}}</badge>
      </div>
    </div>
  </div>
</template>
<script>
import Badge from "./Badge.vue";
export default {
  components: {
    Badge
  },
  props: {
    task: {
      type: Object,
      default: () => ({})
    }
  },
  computed: {
    badgeColor() {
      const mappings = {
        Design: "purple",
        "Feature Request": "teal",
        Backend: "blue",
        QA: "green",
        default: "teal"
      };
      return mappings[this.task.type] || mappings.default;
    },
    description () {
      return this.task.messages ? this.task.messages[0]?.content: null
    },
    image () {
      let image = (this.task.messages[0]?.images||[])[0]
      if (image) {
        try {
          return JSON.parse(image)
        } catch {
          image = {
            src: image
          }
        }
      }
      return image
    }
  }
};
</script>
