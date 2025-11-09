<!-- src/views/BookingView.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

// Composables
import { useDeskData } from '@/composables/useDeskData'
import { useFilters } from '@/composables/useFilters'
import { useBookingLogic } from '@/composables/useBookingLogic'
import { useCalendar } from '@/composables/useCalendar'

//UI components
import BookingHeader from '@/components/booking/BookingHeader.vue'
import FiltersBar from '@/components/booking/FiltersBar.vue'
import DeskGrid from '@/components/booking/DeskGrid.vue'
import ContextMenuDialog from '@/components/booking/ContextMenuDialog.vue'
import BookingDialog from '@/components/booking/BookingDialog.vue'
import WeeklyAvailabilityDialog from '@/components/booking/WeeklyAvailabilityDialog.vue'

/* 1) Desk data */
const { CURRENT_USER, desks, userBookings } = useDeskData()

/* 1.5) Floor selection */
const selectedFloor = ref(0)

/* 2) Filters */
const {
  searchQuery,
  selectedStatus,
  selectedFeatures,
  availableFeatures,
  filteredDesks,
  toggleQuickFilter,
  clearFilters,
  hasActiveFilters,
} = useFilters(desks)

/* 2.5) Filter by floor */
const desksByFloor = computed(() => {
  return filteredDesks.value.filter((desk) => desk.floor === selectedFloor.value)
})

/* 3) Booking logic + context menu */
const {
  contextMenu,
  contextMenuDesk,
  bookingDialog,
  selectedDesk,
  bookingDate,
  startTime,
  endTime,
  weeklyAvailabilityDialog,
  selectedDeskForWeekly,
  getDeskColor,
  handleDeskClick,
  handleDeskRightClick,
  quickBook,
  bookHalfDay,
  bookFullDay,
  toggleFavorite,
  confirmBooking,
  viewWeeklyAvailability,
} = useBookingLogic(desks, userBookings, CURRENT_USER)

/* 4) Calendar for weekly availability */
const { weekDays, getDeskBookingForDate } = useCalendar(userBookings)
</script>

<template>
  <v-container fluid class="booking-view pa-6">
    <!-- Header -->
    <BookingHeader />

    <!-- Filters -->
    <FiltersBar
      :search-query="searchQuery"
      :selected-status="selectedStatus"
      :selected-features="selectedFeatures"
      :available-features="availableFeatures"
      :has-active-filters="hasActiveFilters"
      :total-desks="desks.length"
      :filtered-desk-count="filteredDesks.length"
      @update:searchQuery="(val) => (searchQuery = val)"
      @update:selectedStatus="(val) => (selectedStatus = val)"
      @update:selectedFeatures="(val) => (selectedFeatures = val)"
      @toggleQuick="toggleQuickFilter"
      @clear="clearFilters"
    />

    <!-- Legend and Floor Selector -->
    <v-row class="mb-4">
      <v-col cols="12">
        <div class="d-flex flex-wrap justify-space-between align-center ga-4">
          <!-- Legend -->
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

          <!-- Floor Selector -->
          <v-btn-toggle v-model="selectedFloor" color="primary" mandatory rounded="lg">
            <v-btn :value="0">
              <v-icon start>mdi-layers</v-icon>
              Floor 0
            </v-btn>
            <v-btn :value="1">
              <v-icon start>mdi-layers</v-icon>
              Floor 1
            </v-btn>
          </v-btn-toggle>
        </div>
      </v-col>
    </v-row>

    <!-- Desk grid filtered -->
    <DeskGrid
      :desks="desksByFloor"
      :get-desk-color="getDeskColor"
      @left="handleDeskClick"
      @right="handleDeskRightClick"
    />

    <!-- Context menu dialog -->
    <ContextMenuDialog
      v-model="contextMenu"
      :desk="contextMenuDesk"
      @quick="(h: number) => quickBook(contextMenuDesk!, h)"
      @half="() => bookHalfDay(contextMenuDesk!)"
      @full="() => bookFullDay(contextMenuDesk!)"
      @favorite="() => toggleFavorite(contextMenuDesk!)"
      @weekly="() => viewWeeklyAvailability(contextMenuDesk!)"
    />

    <!-- Booking dialog -->
    <BookingDialog
      v-model="bookingDialog"
      :desk-id="selectedDesk?.id"
      :date="bookingDate"
      :start-time="startTime"
      :end-time="endTime"
      @update:date="(v) => (bookingDate = v)"
      @update:startTime="(v) => (startTime = v)"
      @update:endTime="(v) => (endTime = v)"
      @confirm="confirmBooking"
    />

    <!-- Weekly availability dialog -->
    <WeeklyAvailabilityDialog
      v-model="weeklyAvailabilityDialog"
      :desk="selectedDeskForWeekly"
      :week-days="weekDays"
      :is-booked="(deskId, date) => getDeskBookingForDate(deskId, date)"
      @book="
        () => {
          selectedDesk && (bookingDialog = true)
        }
      "
    />
  </v-container>
</template>

<style scoped>
.booking-view {
  min-height: 100vh;
}
</style>
