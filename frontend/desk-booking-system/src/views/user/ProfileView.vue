<script setup lang="ts">
import { currentUser } from '@/stores/auth'
import DeskHeightCalculator from '@/components/DeskHeightCalculator.vue'
</script>

<template>
  <v-container class="pa-6 fill-height d-flex flex-column justify-center" v-if="currentUser">
    <v-row align="center" class="flex-grow-1">
      <v-col cols="12" md="6" lg="6" class="d-flex flex-column align-center pa-8">
        <!-- Profile Header -->
        <v-card class="mb-6" elevation="2" min-width="500">
          <v-card-text class="text-center pa-8">
            <!-- Profile Picture -->
            <v-avatar size="120" class="mb-4" color="primary">
              <v-img
                v-if="currentUser.profilePicture"
                :src="currentUser.profilePicture"
                :alt="currentUser.fullName"
                cover
              />
              <v-icon v-else size="60" color="white">mdi-account</v-icon>
            </v-avatar>

            <!-- User Information -->
            <div class="mb-6">
              <div class="mb-4">
                <v-chip color="primary" variant="outlined" class="mb-2">Username</v-chip>
                <div class="text-h6">{{ currentUser.username }}</div>
              </div>

              <div class="mb-4">
                <v-chip color="primary" variant="outlined" class="mb-2">Full Name</v-chip>
                <div class="text-h6">{{ currentUser.fullName }}</div>
              </div>

              <div class="mb-4">
                <v-chip color="primary" variant="outlined" class="mb-2">Email</v-chip>
                <div class="text-h6">{{ currentUser.email }}</div>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col cols="12" md="6" lg="6" class="d-flex flex-column align-center pa-8">
        <DeskHeightCalculator />
      </v-col>
    </v-row>
  </v-container>

  <!-- Redirect message if not authorized -->
  <v-container v-else class="text-center pa-8">
    <v-icon size="64" color="warning" class="mb-4">mdi-lock</v-icon>
    <h2 class="text-h5 mb-2">Access Denied</h2>
    <p class="text-body-1 mb-4">This page is only available for logged-in users.</p>
    <v-btn color="primary" to="/login">Go to Login</v-btn>
  </v-container>
</template>
