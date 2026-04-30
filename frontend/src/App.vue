<template>
  <router-view />
  <Analytics />
</template>

<script setup>
import { onMounted } from 'vue'
import { Analytics } from '@vercel/analytics/vue'
import { useSectionsStore } from './stores/sections'
import { useAISettingsStore } from './stores/aiSettings'

const sectionsStore = useSectionsStore()
const aiSettingsStore = useAISettingsStore()

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    sectionsStore.loadFromServer()
    aiSettingsStore.loadFromServer()
  }
})
</script>

<style>
</style>
