<script setup lang="ts">
import type { Desk, Booking } from '@/types/mockData'
import deskPhoto from '@/assets/deskPhoto.png'

const props = defineProps<{
  desks: Desk[]
  bookings: Booking[]
  currentUser: string
}>()
</script>

<template>
  <v-card elevation="2" class="pa-6 mt-4">
    <v-row class="mb-4">
      <v-col>
        <h2 class="text-h5 font-weight-bold">My Current Booking</h2>
      </v-col>
    </v-row>

    <v-row class="justify-center">
      <v-col cols="12" md="10" lg="8" xl="6">
        <v-alert
          v-if="props.desks.filter((d) => d.bookedBy === props.currentUser).length === 0"
          type="info"
          variant="tonal"
          class="mb-4"
        >
          No active bookings. Click on an available desk to make a reservation.
        </v-alert>

        <div v-else>
          <v-card
            v-for="desk in props.desks.filter((d) => d.bookedBy === props.currentUser)"
            :key="desk.id"
            elevation="3"
            class="booking-detail-card mb-4"
          >
            <v-row no-gutters>
              <!-- IMAGE -->
              <v-col cols="12" md="4">
                <div class="image-wrapper">
                  <!-- Changed to 'contain' and added proper height -->
                  <v-img
                    :src="deskPhoto"
                    alt="Desk"
                    height="300"
                    contain
                    position="center center"
                    class="rounded-lg"
                  >
                    <template #placeholder>
                      <div class="d-flex align-center justify-center fill-height">
                        <v-icon size="64" color="grey">mdi-desk</v-icon>
                      </div>
                    </template>
                  </v-img>

                  <!-- desk label -->
                  <div class="desk-label">
                    <v-chip color="primary" size="small">{{ desk.id }}</v-chip>
                  </div>
                </div>
              </v-col>

              <!-- RIGHT SIDE -->
              <v-col cols="12" md="8">
                <v-card-text class="pa-4">
                  <!-- smaller date/time -->
                  <v-alert
                    color="success"
                    variant="tonal"
                    density="compact"
                    class="mb-3 d-flex flex-column align-center justify-center text-center py-4 ga-1"
                  >
                    <div class="text-subtitle-2 font-weight-bold">Active Booking</div>

                    <div class="text-caption d-flex align-center justify-center ga-1">
                      <v-icon size="x-small">mdi-calendar</v-icon>
                      {{
                        props.bookings.find(
                          (b) => b.deskId === desk.id && b.userId === props.currentUser,
                        )?.date || 'N/A'
                      }}
                    </div>

                    <div class="text-caption d-flex align-center justify-center ga-1">
                      <v-icon size="x-small">mdi-clock-outline</v-icon>
                      {{
                        props.bookings.find(
                          (b) => b.deskId === desk.id && b.userId === props.currentUser,
                        )?.startTime || 'N/A'
                      }}
                      &nbsp;–&nbsp;
                      {{
                        props.bookings.find(
                          (b) => b.deskId === desk.id && b.userId === props.currentUser,
                        )?.endTime || 'N/A'
                      }}
                    </div>
                  </v-alert>

                  <div class="mb-3">
                    <v-text-field
                      :model-value="112"
                      label="Standing Height (cm)"
                      type="number"
                      variant="outlined"
                      density="compact"
                      hide-details
                      class="mb-2"
                    />
                    <v-text-field
                      :model-value="68"
                      label="Sitting Height (cm)"
                      type="number"
                      variant="outlined"
                      density="compact"
                      hide-details
                    />
                  </div>

                  <v-alert type="info" variant="tonal" density="compact" class="mb-3">
                    <div class="text-center">
                      <div class="text-caption">Current Height</div>
                      <div class="text-h6 font-weight-bold">68 cm</div>
                    </div>
                  </v-alert>

                  <div class="d-flex flex-column ga-2">
                    <v-btn
                      color="primary"
                      variant="flat"
                      size="small"
                      prepend-icon="mdi-arrow-up"
                      block
                    >
                      Raise Desk
                    </v-btn>
                    <v-btn
                      color="primary"
                      variant="outlined"
                      size="small"
                      prepend-icon="mdi-arrow-down"
                      block
                    >
                      Lower Desk
                    </v-btn>
                  </div>
                </v-card-text>
              </v-col>
            </v-row>
          </v-card>
        </div>
      </v-col>
    </v-row>
  </v-card>
</template>

<style scoped>
.booking-detail-card {
  overflow: hidden;
}

.image-wrapper {
  position: relative;
  height: 300px;
  background-color: #1a1a1a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.desk-label {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 1;
}
</style>
