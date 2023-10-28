<template>
  <div v-if="user">
    <img :src="user.photo.url" alt="User photo">
    <h1>{{ user.name }}</h1>
    <p>Category: {{ user.category }}</p>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      user: null
    }
  },
  async created() {
    const response = await axios.get('http://localhost:1337/users/me')
    this.user = response.data
  }
}
</script>
