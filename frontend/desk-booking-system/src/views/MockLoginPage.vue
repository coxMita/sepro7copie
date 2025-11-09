<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authLogin, userType } from '@/stores/auth'

const userName = ref('')
const userNameRules = [
  (value: string) => {
    if (value === 'user' || value === 'admin') return true
    return 'User name must be either "user" or "admin".'
  },
]

const router = useRouter()

function submit() {
  if (userName.value === 'user' || userName.value === 'admin') {
    authLogin(userName.value)
    const route = userType.value === 'admin' ? '/admin/bookings' : '/book'
    router.push(route)
  }
}
</script>

<template>
  <div class="pa-4">
    <h1>This is the MockLoginPage!</h1>
    <v-sheet class="mx-auto" width="300">
      <v-form fast-fail @submit.prevent="submit">
        <v-text-field v-model="userName" :rules="userNameRules" label="User name"></v-text-field>
        <v-btn class="mt-2" type="submit" block>Submit</v-btn>
      </v-form>
    </v-sheet>
  </div>
</template>
