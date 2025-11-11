<script setup lang="ts">
import { useDeskData } from '@/composables/useDeskData'
import { useAdminDeskManagement } from '@/composables/useAdminDeskManagement'
import { schedulerApi } from '@/services/api'
import { ref } from 'vue'

const { desks, userBookings } = useDeskData()
const { desksByFloor } = useAdminDeskManagement(desks, userBookings)

const deskHeight = ref(100)
const changeHeightFeedbackMessage = ref('')
const changeHeightFeedbackVisible = ref(false)
const changeHeightFeedbackType = ref<'success' | 'error' | 'info' | 'warning'>('success')
const isChangingHeight = ref(false)

const scheduledDate = ref('')
const scheduledTime = ref('')
const scheduledHeight = ref(100)
const scheduleFeedbackMessage = ref('')
const scheduleFeedbackVisible = ref(false)
const scheduleFeedbackType = ref<'success' | 'error' | 'info' | 'warning'>('success')

const today = new Date().toISOString().split('T')[0]

const changeHeightForAllDesks = async () => {
  changeHeightFeedbackVisible.value = false
  isChangingHeight.value = true

  // Validate height in cm (68-120 cm range for desk simulator)
  if (deskHeight.value < 68 || deskHeight.value > 120) {
    changeHeightFeedbackMessage.value =
      'Invalid height! Please enter a value between 68 and 120 cm.'
    changeHeightFeedbackType.value = 'error'
    changeHeightFeedbackVisible.value = true
    isChangingHeight.value = false
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 3000)
    return
  }

  try {
    // Convert cm to mm for the API (desk simulator uses mm)
    const positionMm = deskHeight.value * 10

    console.log(`Setting all desks to ${deskHeight.value} cm (${positionMm} mm)`)

    // Call the scheduler service via gateway
    const results = await schedulerApi.setAllDesksPosition(positionMm)

    // Count successful operations
    const successCount = results.filter((r: any) => r.success).length
    const totalCount = results.length

    // Update local state for immediate UI feedback
    desksByFloor.value.forEach((desk) => {
      desk.height = deskHeight.value
    })

    changeHeightFeedbackMessage.value = `Successfully set ${successCount}/${totalCount} desks to ${deskHeight.value} cm (${positionMm} mm).`
    changeHeightFeedbackType.value = successCount === totalCount ? 'success' : 'warning'
    changeHeightFeedbackVisible.value = true
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 5000)
  } catch (error: any) {
    console.error('Error changing desk heights:', error)
    changeHeightFeedbackMessage.value = 
      error.response?.data?.detail || 
      'Failed to change desk heights. Please check if the scheduler service is running.'
    changeHeightFeedbackType.value = 'error'
    changeHeightFeedbackVisible.value = true
    setTimeout(() => (changeHeightFeedbackVisible.value = false), 5000)
  } finally {
    isChangingHeight.value = false
  }
}

const scheduleHeightAdjustment = () => {
  scheduleFeedbackVisible.value = false

  if (
    !scheduledDate.value ||
    !scheduledTime.value ||
    scheduledHeight.value < 68 ||
    scheduledHeight.value > 120
  ) {
    scheduleFeedbackMessage.value =
      scheduledHeight.value < 68 || scheduledHeight.value > 120
        ? 'Invalid height! Please enter a value between 68 and 120 cm.'
        : 'Please select a valid date, time, and height for scheduling.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
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
      scheduleFeedbackType.value = 'success'
      scheduleFeedbackVisible.value = true
      setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
    }, delay)

    scheduleFeedbackMessage.value = `Height adjustment scheduled for ${scheduledDate.value} at ${scheduledTime.value} to ${scheduledHeight.value} cm.`
    scheduleFeedbackType.value = 'success'
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
  } else {
    scheduleFeedbackMessage.value =
      'The selected date and time are in the past. Please choose a future date and time.'
    scheduleFeedbackType.value = 'error'
    scheduleFeedbackVisible.value = true
    setTimeout(() => (scheduleFeedbackVisible.value = false), 3000)
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
          <v-btn 
            color="primary" 
            @click="changeHeightForAllDesks"
            :loading="isChangingHeight"
            :disabled="isChangingHeight"
          >
            Change Height (All Desks)
          </v-btn>
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
            v-model.number="deskHeight"
            label="Set Desk Height (cm)"
            type="number"
            min="68"
            max="120"
            hint="Valid range: 68-120 cm (680-1200 mm)"
            persistent-hint
            :disabled="isChangingHeight"
          />
        </v-col>
      </v-row>
    </v-card>

    <!-- Scheduling -->
    <v-card elevation="2" class="pa-6 mb-6">
      <h3 class="text-h6 mb-4">Schedule Height Adjustment</h3>
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
            v-model.number="scheduledHeight"
            label="Scheduled Desk Height (cm)"
            type="number"
            min="68"
            max="120"
            hint="Valid range: 68-120 cm (680-1200 mm)"
            persistent-hint
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
.text-success {
  color: green;
  font-weight: bold;
}
</style>