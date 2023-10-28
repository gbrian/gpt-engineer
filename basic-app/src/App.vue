<template>
  <div id="app">
    <RegistrationForm />
    <Profile />
    <FriendsList />
  </div>
</template>

<script>
import RegistrationForm from './components/RegistrationForm.vue'
import Profile from './components/Profile.vue'
import FriendsList from './components/FriendsList.vue'

export default {
  components: {
    RegistrationForm,
    Profile,
    FriendsList
  }
}
</script>
