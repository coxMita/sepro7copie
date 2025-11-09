<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const INCHES_PER_FOOT = 12
const CM_PER_INCH = 2.54
const SITTING_MULTIPLIER = 0.45
const STANDING_MULTIPLIER = 0.7

// Input values
const heightCm = ref<number | null>(null)
const heightFeet = ref<number | null>(null)
const heightInches = ref<number | null>(null)
const units = ref<'metric' | 'imperial'>('metric')
const position = ref<'sitting' | 'standing'>('sitting')

// Results
const showResults = ref(false)
const calculatedHeight = ref<number | null>(null)

// Watch for position and units changes and hide results
watch(position, () => {
  showResults.value = false
  calculatedHeight.value = null
})

watch(units, () => {
  showResults.value = false
  calculatedHeight.value = null
})

// Convert height to cm for calculations
const heightInCm = computed(() => {
  if (units.value === 'metric') {
    return heightCm.value
  } else {
    if (!heightFeet.value) return null
    const totalInches = heightFeet.value * INCHES_PER_FOOT + (heightInches.value || 0)
    return Math.round(totalInches * CM_PER_INCH)
  }
})

// Validation
const isValidInput = computed(() => {
  if (units.value === 'metric') {
    return heightCm.value && heightCm.value > 0
  } else {
    return (
      heightFeet.value &&
      heightFeet.value > 0 &&
      (heightInches.value === null || heightInches.value >= 0)
    )
  }
})

const calculate = () => {
  if (!heightInCm.value) return

  let multiplier = SITTING_MULTIPLIER
  if (position.value === 'standing') {
    multiplier = STANDING_MULTIPLIER
  }

  calculatedHeight.value = Math.round(heightInCm.value * multiplier)
  showResults.value = true
}

const reset = () => {
  heightCm.value = null
  heightFeet.value = null
  heightInches.value = null
  showResults.value = false
  calculatedHeight.value = null
}

// Convert result to display units
const displayHeight = computed(() => {
  if (!calculatedHeight.value) return null

  if (units.value === 'metric') {
    return `${calculatedHeight.value} cm`
  } else {
    const totalInches = Math.round(calculatedHeight.value / CM_PER_INCH)
    const feet = Math.floor(totalInches / INCHES_PER_FOOT)
    const inches = totalInches % INCHES_PER_FOOT
    return `${feet}' ${inches}"`
  }
})
</script>

<template>
  <v-card class="mx-auto" max-width="500">
    <v-card-title class="text-h6 font-weight-bold"> Desk Height Calculator </v-card-title>

    <v-card-subtitle>
      Enter your height and position to calculate the ideal desk height for ergonomic comfort.
    </v-card-subtitle>

    <v-card-text>
      <!-- Unit Selection -->
      <v-row class="mb-3">
        <v-col cols="12">
          <v-btn-toggle v-model="units" color="primary" variant="outlined" divided mandatory>
            <v-btn value="metric">Metric (cm)</v-btn>
            <v-btn value="imperial">Imperial (ft/in)</v-btn>
          </v-btn-toggle>
        </v-col>
      </v-row>

      <!-- Height Input - Metric -->
      <v-row v-if="units === 'metric'">
        <v-col cols="12">
          <v-text-field
            v-model.number="heightCm"
            label="Your Height"
            type="number"
            variant="outlined"
            density="comfortable"
            suffix="cm"
            :rules="[(v) => !!v || 'Height is required', (v) => v > 0 || 'Height must be positive']"
          />
        </v-col>
      </v-row>

      <!-- Height Input - Imperial -->
      <v-row v-else>
        <v-col cols="6">
          <v-text-field
            v-model.number="heightFeet"
            label="Feet"
            type="number"
            variant="outlined"
            density="comfortable"
            suffix="ft"
            :rules="[(v) => !!v || 'Feet is required', (v) => v > 0 || 'Must be positive']"
          />
        </v-col>
        <v-col cols="6">
          <v-text-field
            v-model.number="heightInches"
            label="Inches"
            type="number"
            variant="outlined"
            density="comfortable"
            suffix="in"
            :rules="[
              (v) => v === null || v === undefined || v >= 0 || 'Must be 0 or positive',
              (v) => v === null || v === undefined || v < INCHES_PER_FOOT || 'Must be less than 12',
            ]"
          />
        </v-col>
      </v-row>

      <!-- Position Selection -->
      <v-row class="mb-3">
        <v-col cols="12">
          <v-select
            v-model="position"
            :items="[
              { title: 'Sitting Desk', value: 'sitting' },
              { title: 'Standing Desk', value: 'standing' },
            ]"
            label="Desk Position"
            variant="outlined"
            density="comfortable"
          />
        </v-col>
      </v-row>

      <!-- Results -->
      <v-row v-if="showResults">
        <v-col cols="12">
          <v-alert type="success" variant="tonal" class="mb-3">
            <v-alert-title>Recommended Desk Height</v-alert-title>
            <div class="text-h6 mt-2">{{ displayHeight }}</div>
            <div class="text-caption mt-1">For {{ position }} position based on your height</div>
          </v-alert>
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions>
      <v-btn v-if="showResults" color="secondary" variant="outlined" @click="reset"> Reset </v-btn>
      <v-spacer />
      <v-btn color="primary" variant="elevated" :disabled="!isValidInput" @click="calculate">
        Calculate
      </v-btn>
    </v-card-actions>
  </v-card>
</template>
