<script setup lang="ts">
import { useDeskData } from '@/composables/useDeskData'
import { useAdminDeskManagement } from '@/composables/useAdminDeskManagement'

import { ref } from 'vue'

const { desks, userBookings } = useDeskData()

const { desksByFloor } = useAdminDeskManagement(desks, userBookings)

const deskHeight = ref(100)
const changeHeightFeedbackMessage = ref('')
const changeHeightFeedbackVisible = ref(false)
const changeHeightFeedbackType = ref('success')

const scheduledDate = ref('')
const scheduledTime = ref('')
const scheduledHeight = ref(100)
const scheduleFeedbackMessage = ref('')
const scheduleFeedbackVisible = ref(false)
const scheduleFeedbackType = ref('success')

const today = new Date().toISOString().split('T')[0]

const changeHeightForAllDesks = () => {
  // Reset feedback visibility to ensure it updates properly
  changeHeightFeedbackVisible.value = false

  if (deskHeight.value < 50 || deskHeight.value > 150) {
    // Invalid height feedback
    changeHeightFeedbackMessage.value =
      'Invalid height! Please enter a value between 50 and 150 cm.'
    changeHeightFeedbackType.value = 'error' // Set feedback type to red
    changeHeightFeedbackVisible.value = true
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 3000) // Hide feedback after 3 seconds
    return
  } else {
    // Valid height feedback
    changeHeightFeedbackMessage.value = `All desks have been successfully set to ${deskHeight.value} cm.`
    changeHeightFeedbackType.value = 'success' // Set feedback type to green
    changeHeightFeedbackVisible.value = true
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 3000) // Hide feedback after 3 seconds
  }

  // Valid height feedback
  desksByFloor.value.forEach((desk) => {
    desk.height = deskHeight.value
  })

  changeHeightFeedbackMessage.value = `All desks have been successfully set to ${deskHeight.value} cm.`
  changeHeightFeedbackType.value = 'success' // Set feedback type to green
  changeHeightFeedbackVisible.value = true
  setTimeout(() => (changeHeightFeedbackVisible.value = false), 3000) // Hide feedback after 3 seconds
}

const scheduleHeightAdjustment = () => {
  // Reset feedback visibility to ensure it updates properly
  scheduleFeedbackVisible.value = false

  if (
    !scheduledDate.value ||
    !scheduledTime.value ||
    scheduledHeight.value < 50 ||
    scheduledHeight.value > 150
  ) {
    // Invalid height feedback
    scheduleFeedbackMessage.value =
      scheduledHeight.value < 50 || scheduledHeight.value > 150
        ? 'Invalid height! Please enter a value between 50 and 150 cm.'
        : 'Please select a valid date, time, and height for scheduling.'
    scheduleFeedbackType.value = 'error' // Set feedback type to red
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000) // Hide feedback after 3 seconds
    return
  }

  const now = new Date()
  const selectedDateTime = new Date(`${scheduledDate.value}T${scheduledTime.value}`)
  const delay = selectedDateTime.getTime() - now.getTime()

  if (delay > 0) {
    setTimeout(() => {
      desksByFloor.value.forEach((desk) => {
        desk.height = scheduledHeight.value
      })
      scheduleFeedbackMessage.value = `Desks have been adjusted to ${scheduledHeight.value} cm on ${scheduledDate.value} at ${scheduledTime.value}.`
      scheduleFeedbackType.value = 'success' // Set feedback type to green
      scheduleFeedbackVisible.value = true
      setTimeout(() => (scheduleFeedbackVisible.value = false), 3000) // Hide feedback after 3 seconds
    }, delay)

    scheduleFeedbackMessage.value = `Height adjustment scheduled for ${scheduledDate.value} at ${scheduledTime.value} to ${scheduledHeight.value} cm.`
    scheduleFeedbackType.value = 'success' // Set feedback type to green
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000) // Hide feedback after 3 seconds
  } else {
    scheduleFeedbackMessage.value =
      'The selected date and time are in the past. Please choose a future date and time.'
    scheduleFeedbackType.value = 'error' // Set feedback type to red
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000) // Hide feedback after 3 seconds
  }
}
</script>

<template>
  <v-container fluid class="pa-6">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">Manage Desks</h1>
        <p class="text-body-1 text-medium-emphasis mt-2">
          View and control all desks across both floors.
        </p>
      </v-col>
    </v-row>

    <!-- Actions -->
    <v-card elevation="2" class="pa-6 mb-6">
      <v-row align="center">
        <!-- Change Height (All Desks) Button -->
        <v-col cols="6">
          <v-btn color="primary" @click="changeHeightForAllDesks">Change Height (All Desks)</v-btn>
        </v-col>

        <!-- Feedback Bubble for Change Height -->
        <v-col cols="6">
          <v-alert v-if="changeHeightFeedbackVisible" :type="changeHeightFeedbackType" class="mt-4">
            {{ changeHeightFeedbackMessage }}
          </v-alert>
        </v-col>
      </v-row>

      <!-- Desk Height Adjustment -->
      <v-row class="mt-4">
        <v-col cols="6">
          <v-text-field
            v-model="deskHeight"
            label="Set Desk Height (cm)"
            type="number"
            min="50"
            max="150"
          />
        </v-col>
      </v-row>
    </v-card>

    <!-- Scheduling -->
    <v-card elevation="2" class="pa-6 mb-6">
      <v-row>
        <v-col cols="6">
          <v-text-field v-model="scheduledDate" label="Schedule Date" type="date" :min="today" />
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model="scheduledTime"
            label="Schedule Time (HH:mm)"
            placeholder="e.g., 14:30"
            type="time"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="6">
          <v-text-field
            v-model="scheduledHeight"
            label="Scheduled Desk Height (cm)"
            type="number"
            min="50"
            max="150"
          />
        </v-col>
      </v-row>
      <v-row>
        <v-col cols="12" class="d-flex justify-center">
          <v-btn color="info" @click="scheduleHeightAdjustment">Schedule Height Adjustment</v-btn>
        </v-col>
      </v-row>

      <!-- Scheduling Feedback -->
      <v-alert v-if="scheduleFeedbackVisible" :type="scheduleFeedbackType" class="mt-4">
        {{ scheduleFeedbackMessage }}
      </v-alert>
    </v-card>
  </v-container>
</template>

<style scoped>
.desk-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
}
.desk-button {
  aspect-ratio: 1;
  font-size: 0.75rem;
  font-weight: 600;
  position: relative;
}
.desk-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.desk-features {
  display: flex;
  gap: 2px;
  margin-top: 2px;
}
.text-success {
  color: green;
  font-weight: bold;
}
</style>
