<script setup lang="ts">
import type { Desk } from '@/types/mockData'
const props = defineProps<{
  desks: Desk[]
  getDeskColor: (s: string) => string
}>()
const emits = defineEmits<{
  (e: 'left', desk: Desk): void
  (e: 'right', ev: MouseEvent, desk: Desk): void
}>()
</script>

<template>
  <v-card elevation="2" class="pa-6">
    <v-row class="mb-4">
      <v-col>
        <h2 class="text-h5 font-weight-bold">Desk Map</h2>
        <p class="text-caption text-grey mt-1">Right-click on available desks for quick actions</p>
      </v-col>
    </v-row>

    <div class="desk-grid">
      <v-btn
        v-for="desk in props.desks"
        :key="desk.id"
        :color="getDeskColor(desk.status)"
        variant="flat"
        size="large"
        class="desk-button"
        :class="{ 'my-booking': desk.bookedBy === 'current-user' }"
        :disabled="desk.status !== 'available'"
        @click="emits('left', desk)"
        @contextmenu="emits('right', $event, desk)"
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
.my-booking {
  border: 2px solid #2196f3 !important;
  box-shadow: 0 0 8px rgba(33, 150, 243, 0.5) !important;
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
