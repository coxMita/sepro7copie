<!-- src/components/admin/AdminDeskManagementDialog.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Desk, DeskStatus, Booking } from '@/types/mockData'

const props = defineProps<{
  modelValue: boolean
  desk: Desk | null
  allBookings: Booking[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  updateStatus: [deskId: string, status: DeskStatus]
  updateBooking: [booking: Booking]
  deleteBooking: [bookingId: string]
}>()

const newStatus = ref<DeskStatus>('available')
const editingBooking = ref<Booking | null>(null)
const showEditBooking = ref(false)

// Get all bookings for this desk
const deskBookings = computed(() => {
  if (!props.desk) return []
  return props.allBookings
    .filter((b) => b.deskId === props.desk!.id && b.status === 'active')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const statusItems = [
  { title: 'Available', value: 'available' },
  { title: 'Occupied', value: 'occupied' },
  { title: 'Reserved', value: 'reserved' },
  { title: 'Maintenance', value: 'maintenance' },
]

const updateStatus = () => {
  if (props.desk) {
    emit('updateStatus', props.desk.id, newStatus.value)
  }
}

const startEditBooking = (booking: Booking) => {
  editingBooking.value = { ...booking }
  showEditBooking.value = true
}

const saveBookingEdit = () => {
  if (editingBooking.value) {
    emit('updateBooking', editingBooking.value)
    showEditBooking.value = false
    editingBooking.value = null
  }
}

const deleteBooking = (bookingId: string) => {
  if (confirm('Are you sure you want to delete this booking?')) {
    emit('deleteBooking', bookingId)
  }
}

// Reset when dialog opens
const handleDialogChange = (value: boolean) => {
  if (value && props.desk) {
    newStatus.value = props.desk.status
  }
  emit('update:modelValue', value)
}
</script>

<template>
  <v-dialog
    :model-value="modelValue"
    @update:model-value="handleDialogChange"
    max-width="700"
    scrollable
  >
    <v-card>
      <v-card-title class="text-h5 d-flex align-center justify-space-between pa-4">
        <span>Manage Desk {{ desk?.id }}</span>
        <v-chip
          :color="
            desk?.status === 'available'
              ? 'success'
              : desk?.status === 'occupied' || desk?.status === 'reserved'
                ? 'error'
                : 'grey'
          "
          size="small"
        >
          {{ desk?.status }}
        </v-chip>
      </v-card-title>

      <v-divider />

      <v-card-text class="pa-4" style="max-height: 600px">
        <!-- Desk Information -->
        <v-alert type="info" variant="tonal" density="compact" class="mb-4">
          <div class="d-flex justify-space-between align-center">
            <div>
              <strong>Desk:</strong> {{ desk?.id }} | <strong>Floor:</strong> {{ desk?.floor }}
            </div>
            <v-icon v-if="desk?.isFavorite" color="red">mdi-heart</v-icon>
          </div>
        </v-alert>

        <!-- Change Status Section -->
        <v-card variant="outlined" class="mb-4">
          <v-card-text>
            <h3 class="text-h6 mb-3">Change Desk Status</h3>
            <v-select
              v-model="newStatus"
              :items="statusItems"
              label="Desk Status"
              variant="outlined"
              density="comfortable"
              hide-details
              class="mb-3"
            />
            <v-btn
              color="primary"
              variant="flat"
              block
              @click="updateStatus"
              :disabled="newStatus === desk?.status"
            >
              Update Status
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- Current Bookings Section -->
        <v-card variant="outlined">
          <v-card-text>
            <div class="d-flex align-center justify-space-between mb-3">
              <h3 class="text-h6">Active Bookings ({{ deskBookings.length }})</h3>
              <v-chip size="small" :color="deskBookings.length > 0 ? 'error' : 'success'">
                {{ deskBookings.length > 0 ? 'Has Bookings' : 'No Bookings' }}
              </v-chip>
            </div>

            <div v-if="deskBookings.length === 0" class="text-center text-grey py-4">
              <v-icon size="64" color="grey-lighten-1">mdi-calendar-blank</v-icon>
              <div class="text-body-2 mt-2">No active bookings for this desk</div>
            </div>

            <v-list v-else density="compact">
              <v-list-item
                v-for="booking in deskBookings"
                :key="booking.id"
                class="mb-2 booking-item"
                border
                rounded
              >
                <template #prepend>
                  <v-avatar color="primary" size="40">
                    <v-icon>mdi-calendar-clock</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title class="font-weight-bold">
                  {{
                    new Date(booking.date).toLocaleDateString('en-GB', {
                      weekday: 'short',
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                    })
                  }}
                </v-list-item-title>

                <v-list-item-subtitle>
                  <v-icon size="small">mdi-clock-outline</v-icon>
                  {{ booking.startTime }} - {{ booking.endTime }}
                  <br />
                  <v-icon size="small">mdi-account</v-icon>
                  User: {{ booking.userId }}
                  <span v-if="booking.notes">
                    <br />
                    <v-icon size="small">mdi-note-text</v-icon>
                    {{ booking.notes }}
                  </span>
                </v-list-item-subtitle>

                <template #append>
                  <div class="d-flex flex-column ga-1">
                    <v-btn
                      icon="mdi-pencil"
                      size="small"
                      variant="text"
                      color="primary"
                      @click="startEditBooking(booking)"
                    />
                    <v-btn
                      icon="mdi-delete"
                      size="small"
                      variant="text"
                      color="error"
                      @click="deleteBooking(booking.id)"
                    />
                  </div>
                </template>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-card-text>

      <v-divider />

      <v-card-actions class="pa-4">
        <v-spacer />
        <v-btn color="grey" variant="text" @click="emit('update:modelValue', false)"> Close </v-btn>
      </v-card-actions>
    </v-card>

    <!-- Edit Booking Dialog -->
    <v-dialog v-model="showEditBooking" max-width="500">
      <v-card v-if="editingBooking">
        <v-card-title class="text-h6">Edit Booking</v-card-title>
        <v-card-text>
          <v-alert type="warning" variant="tonal" density="compact" class="mb-4">
            Editing booking for <strong>{{ editingBooking.userId }}</strong>
          </v-alert>

          <v-text-field
            v-model="editingBooking.date"
            label="Date"
            type="date"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            prepend-inner-icon="mdi-calendar"
          />

          <v-text-field
            v-model="editingBooking.startTime"
            label="Start Time"
            type="time"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            prepend-inner-icon="mdi-clock-start"
          />

          <v-text-field
            v-model="editingBooking.endTime"
            label="End Time"
            type="time"
            variant="outlined"
            density="comfortable"
            class="mb-3"
            prepend-inner-icon="mdi-clock-end"
          />

          <v-textarea
            v-model="editingBooking.notes"
            label="Notes (Optional)"
            variant="outlined"
            density="comfortable"
            rows="2"
            prepend-inner-icon="mdi-note-text"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="grey" variant="text" @click="showEditBooking = false"> Cancel </v-btn>
          <v-btn color="primary" variant="flat" @click="saveBookingEdit"> Save Changes </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-dialog>
</template>

<style scoped>
.booking-item {
  transition: all 0.2s;
}

.booking-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}
</style>
