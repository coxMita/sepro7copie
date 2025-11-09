<script setup lang="ts">
import { ref, watch } from 'vue'
import { loggedIn, userType, authLogOut } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { userViews, adminViews } from '@/composables/useViews'

const router = useRouter()

// Start with drawer open by default
const drawerVisibility = ref(true)

const closeDrawer = () => {
  drawerVisibility.value = false
}

const toggleDrawer = () => {
  drawerVisibility.value = !drawerVisibility.value
}

// Open drawer when user logs in
watch(loggedIn, (newVal) => {
  if (newVal) {
    drawerVisibility.value = true
  } else {
    drawerVisibility.value = false
  }
})

const theme = ref(window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

const logOut = () => {
  authLogOut()
  closeDrawer()
  router.push('/')
}
</script>

<template>
  <v-app :theme="theme">
    <v-navigation-drawer
      v-if="loggedIn"
      v-model="drawerVisibility"
      color="primary"
      :permanent="drawerVisibility"
      width="280"
    >
      <v-list color="on-primary">
        <v-list-item
          v-for="item in userType === 'admin' ? adminViews : userViews"
          :key="item.title"
          :title="item.title"
          :to="item.to"
          :prepend-icon="item.icon"
          link
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-4">
          <v-btn block @click="logOut">Logout</v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <v-app-bar>
      <v-app-bar-nav-icon v-if="loggedIn" @click="toggleDrawer"></v-app-bar-nav-icon>

      <v-app-bar-title>Application</v-app-bar-title>
      <v-btn
        :prepend-icon="theme === 'light' ? 'mdi-lightbulb-on-10' : 'mdi-lightbulb-on'"
        slim
        @click="toggleTheme"
      ></v-btn>
      <v-btn v-if="!loggedIn" class="bg-primary" color="on-primary" to="/login">Login</v-btn>
      <span v-if="loggedIn" class="ml-4 mr-4"
        >Logged in as: <b>{{ userType }}</b></span
      >
    </v-app-bar>

    <v-main>
      <router-view v-slot="{ Component }">
        <v-fade-transition hide-on-leave>
          <component :is="Component" />
        </v-fade-transition>
      </router-view>
    </v-main>
  </v-app>
</template>

<style scoped></style>
