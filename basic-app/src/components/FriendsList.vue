<template>
  <ul>
    <li v-for="friend in friends" :key="friend.id">
      <img :src="friend.photo.url" alt="Friend photo">
      <h2>{{ friend.name }}</h2>
      <p>Category: {{ friend.category }}</p>
    </li>
  </ul>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      friends: []
    }
  },
  async created() {
    const response = await axios.get('http://localhost:1337/users/friends')
    this.friends = response.data
  }
}
</script>
