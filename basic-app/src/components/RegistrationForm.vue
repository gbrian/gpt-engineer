<template>
  <form @submit.prevent="register">
    <input v-model="name" type="text" placeholder="Name" required>
    <input type="file" @change="onFileChange" required>
    <select v-model="category" required>
      <option disabled value="">Please select a category</option>
      <option>5</option>
      <option>4</option>
      <option>3</option>
      <option>1</option>
    </select>
    <button type="submit">Register</button>
  </form>
</template>

<script>
import axios from 'axios'

export default {
  data() {
    return {
      name: '',
      photo: null,
      category: ''
    }
  },
  methods: {
    onFileChange(e) {
      this.photo = e.target.files[0];
    },
    async register() {
      const formData = new FormData()
      formData.append('name', this.name)
      formData.append('photo', this.photo)
      formData.append('category', this.category)

      await axios.post('http://localhost:1337/users', formData)
    }
  }
}
</script>
