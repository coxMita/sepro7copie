<!-- src/views/DeskAvailabilityView.vue -->
<script setup lang="ts">
// Composables
import { useDeskData } from '@/composables/useDeskData'
import { useAdminDeskManagement } from '@/composables/useAdminDeskManagement'

// UI Components
import AdminDeskStats from '@/components/admin/AdminDeskStats.vue'
import AdminFiltersBar from '@/components/admin/AdminFiltersBar.vue'
import AdminDeskManagementDialog from '@/components/admin/AdminDeskManagementDialog.vue'

/* Desk Data */
const { desks, userBookings } = useDeskData()

/* Admin Management Logic */
const {
  selectedFloor,
  statusFilter,
  desksByFloor,
  stats,
  managementDialog,
  selectedDesk,
  getDeskColor,
  handleDeskClick,
  handleDeskRightClick,
  updateDeskStatus,
  updateBooking,
  deleteBooking,
} = useAdminDeskManagement(desks, userBookings)
</script>

<template>
  <v-container fluid class="desk-availability-view pa-6">
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <div>
          <h1 class="text-h4 font-weight-bold">Desk Availability Management</h1>
          <p class="text-body-1 text-medium-emphasis mt-2">
            Monitor and control desk availability across all floors
          </p>
        </div>
      </v-col>
    </v-row>

    <!-- Statistics Cards -->
    <AdminDeskStats :stats="stats" />

    <!-- Filters and Floor Selector -->
    <AdminFiltersBar
      :status-filter="statusFilter"
      :selected-floor="selectedFloor"
      @update:status-filter="(val) => (statusFilter = val)"
      @update:selected-floor="(val) => (selectedFloor = val)"
    />

    <!-- Legend -->
    <v-row class="mb-4">
      <v-col cols="12">
        <v-alert type="info" variant="tonal" density="compact">
          <div class="d-flex flex-wrap ga-4 align-center">
            <span class="text-body-2 font-weight-bold"
              >Click any desk to manage status and bookings</span
            >
            <div class="d-flex flex-wrap ga-4">
              <div class="d-flex align-center">
                <v-chip color="success" size="small" class="mr-2" />
                <span class="text-body-2">Available</span>
              </div>
              <div class="d-flex align-center">
                <v-chip color="error" size="small" class="mr-2" />
                <span class="text-body-2">Occupied</span>
              </div>
              <div class="d-flex align-center">
                <v-chip color="warning" size="small" class="mr-2" />
                <span class="text-body-2">Reserved</span>
              </div>
              <div class="d-flex align-center">
                <v-chip color="grey" size="small" class="mr-2" />
                <span class="text-body-2">Maintenance</span>
              </div>
            </div>
          </div>
        </v-alert>
      </v-col>
    </v-row>

    <!-- Admin Desk Grid -->
    <v-card elevation="2" class="pa-6">
      <v-row class="mb-4">
        <v-col>
          <h2 class="text-h5 font-weight-bold">Desk Map</h2>
          <p class="text-caption text-grey mt-1">Click any desk to manage</p>
        </v-col>
      </v-row>

      <div class="desk-grid">
        <v-btn
          v-for="desk in desksByFloor"
          :key="desk.id"
          :color="getDeskColor(desk.status)"
          variant="flat"
          size="large"
          class="desk-button"
          @click="handleDeskClick(desk)"
          @contextmenu.prevent="handleDeskRightClick($event, desk)"
        >
          <div class="desk-content">
            <div class="d-flex align-center gap-1">
              <v-icon v-if="desk.isFavorite" size="x-small" color="red">mdi-heart</v-icon>
              <span>{{ desk.id }}</span>
            </div>
            <div v-if="desk.features.length" class="desk-features">
              <v-icon
                v-for="f in desk.features"
                :key="f"
                size="x-small"
                :icon="f === 'near-window' ? 'mdi-window-closed-variant' : 'mdi-monitor-multiple'"
              />
            </div>
          </div>
        </v-btn>
      </div>
    </v-card>

    <!-- Admin Management Dialog -->
    <AdminDeskManagementDialog
      v-model="managementDialog"
      :desk="selectedDesk"
      :all-bookings="userBookings"
      @update-status="updateDeskStatus"
      @update-booking="updateBooking"
      @delete-booking="deleteBooking"
    />
  </v-container>
</template>

<style scoped>
.desk-availability-view {
  min-height: 100vh;
}

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

@media (max-width: 600px) {
  .desk-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
    gap: 8px;
  }
  .desk-button {
    font-size: 0.65rem;
  }
}
</style>
