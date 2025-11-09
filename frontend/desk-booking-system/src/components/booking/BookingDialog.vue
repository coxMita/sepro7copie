<script setup lang="ts">
import { todayISO } from '@/utils/datetime'
const props = defineProps<{
  modelValue: boolean
  deskId?: string
  date: string
  startTime: string
  endTime: string
}>()
const emits = defineEmits<{
  (e: 'update:modelValue', v: boolean): void
  (e: 'update:date', v: string): void
  (e: 'update:startTime', v: string): void
  (e: 'update:endTime', v: string): void
  (e: 'confirm'): void
}>()
</script>

<template>
  <v-dialog
    :model-value="props.modelValue"
    @update:model-value="emits('update:modelValue', $event)"
    max-width="500px"
  >
    <v-card>
      <v-card-title class="text-h5 pa-4">Book Desk {{ props.deskId }}</v-card-title>
      <v-card-text class="pa-4">
        <v-text-field
          :model-value="props.date"
          @update:model-value="emits('update:date', $event)"
          label="Date"
          type="date"
          :min="todayISO()"
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="mdi-calendar"
        />
        <v-text-field
          :model-value="props.startTime"
          @update:model-value="emits('update:startTime', $event)"
          label="Start Time"
          type="time"
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="mdi-clock-start"
        />
        <v-text-field
          :model-value="props.endTime"
          @update:model-value="emits('update:endTime', $event)"
          label="End Time"
          type="time"
          variant="outlined"
          class="mb-4"
          prepend-inner-icon="mdi-clock-end"
        />
        <v-alert type="info" variant="tonal" class="mb-0">
          <div class="text-body-2">
            <strong>Booking Summary:</strong><br />
            Desk: {{ props.deskId }}<br />
            Date: {{ props.date }}<br />
            Time: {{ props.startTime }} - {{ props.endTime }}
          </div>
        </v-alert>
      </v-card-text>
      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="grey" variant="text" @click="emits('update:modelValue', false)">Cancel</v-btn>
        <v-btn color="primary" variant="flat" @click="emits('confirm')">Confirm Booking</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
