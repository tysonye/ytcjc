import { ref, onMounted, onUnmounted } from 'vue'

export function useResponsive() {
  const isMobile = ref(window.innerWidth <= 767)
  const isTablet = ref(window.innerWidth > 767 && window.innerWidth <= 1023)
  const isDesktop = ref(window.innerWidth > 1023)

  const update = () => {
    isMobile.value = window.innerWidth <= 767
    isTablet.value = window.innerWidth > 767 && window.innerWidth <= 1023
    isDesktop.value = window.innerWidth > 1023
  }

  onMounted(() => window.addEventListener('resize', update))
  onUnmounted(() => window.removeEventListener('resize', update))

  return { isMobile, isTablet, isDesktop }
}
