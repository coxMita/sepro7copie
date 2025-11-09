import { ref, type Ref } from 'vue'
import type { Desk, Booking } from '@/types/mockData'
import { todayISO } from '@/utils/datetime'

export function useBookingLogic(
  desks: Ref<Desk[]>,
  userBookings: Ref<Booking[]>,
  CURRENT_USER: string,
) {
  // dialogs
  const contextMenu = ref(false)
  const contextMenuDesk = ref<Desk | null>(null)

  const bookingDialog = ref(false)
  const selectedDesk = ref<Desk | null>(null)
  const bookingDate = ref(todayISO())
  const startTime = ref('09:00')
  const endTime = ref('17:00')

  const weeklyAvailabilityDialog = ref(false)
  const selectedDeskForWeekly = ref<Desk | null>(null)

  // colors
  const getDeskColor = (status: string) =>
    status === 'available'
      ? 'success'
      : status === 'occupied'
        ? 'error'
        : status === 'reserved'
          ? 'warning'
          : 'grey'

  // click / context
  const handleDeskClick = (desk: Desk) => {
    if (desk.status !== 'available') return
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = '09:00'
    endTime.value = '17:00'
    bookingDialog.value = true
  }
  const handleDeskRightClick = (ev: MouseEvent, desk: Desk) => {
    ev.preventDefault()
    if (desk.status !== 'available') return
    contextMenuDesk.value = desk
    contextMenu.value = true
  }

  // quick actions right click
  const quickBook = (desk: Desk, hours: number) => {
    const now = new Date()
    const hh = String(now.getHours()).padStart(2, '0')
    const mm = String(now.getMinutes()).padStart(2, '0')
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = `${hh}:${mm}`
    endTime.value = `${String(now.getHours() + hours).padStart(2, '0')}:${mm}`
    contextMenu.value = false
    bookingDialog.value = true
  }
  const bookHalfDay = (desk: Desk) => {
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = '09:00'
    endTime.value = '13:00'
    contextMenu.value = false
    bookingDialog.value = true
  }
  const bookFullDay = (desk: Desk) => {
    selectedDesk.value = desk
    bookingDate.value = todayISO()
    startTime.value = '09:00'
    endTime.value = '17:00'
    contextMenu.value = false
    bookingDialog.value = true
  }

  // favorite
  const toggleFavorite = (desk: Desk) => {
    const idx = desks.value.findIndex((d: Desk) => d.id === desk.id)
    if (idx !== -1) desks.value[idx].isFavorite = !desks.value[idx].isFavorite
    contextMenu.value = false
  }

  // confirm / cancel
  const confirmBooking = () => {
    if (!selectedDesk.value || !bookingDate.value || !startTime.value || !endTime.value) return

    const newBooking: Booking = {
      id: String(userBookings.value.length + 1),
      deskId: selectedDesk.value.id,
      date: bookingDate.value,
      startTime: startTime.value,
      endTime: endTime.value,
      userId: CURRENT_USER,
      status: 'active',
      createdAt: new Date().toISOString(),
    }
    userBookings.value.push(newBooking)

    const i = desks.value.findIndex((d: Desk) => d.id === selectedDesk.value?.id)
    if (i !== -1) {
      desks.value[i].status = 'reserved'
      desks.value[i].bookedBy = CURRENT_USER
    }
    bookingDialog.value = false
    selectedDesk.value = null
  }
  const cancelBooking = () => {
    bookingDialog.value = false
    selectedDesk.value = null
  }

  // weekly availability
  const viewWeeklyAvailability = (desk: Desk) => {
    selectedDeskForWeekly.value = desk
    weeklyAvailabilityDialog.value = true
    contextMenu.value = false
  }

  return {
    // state
    contextMenu,
    contextMenuDesk,
    bookingDialog,
    selectedDesk,
    bookingDate,
    startTime,
    endTime,
    weeklyAvailabilityDialog,
    selectedDeskForWeekly,
    // actions
    getDeskColor,
    handleDeskClick,
    handleDeskRightClick,
    quickBook,
    bookHalfDay,
    bookFullDay,
    toggleFavorite,
    confirmBooking,
    cancelBooking,
    viewWeeklyAvailability,
  }
}
