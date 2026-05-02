<template>
  <router-view />
  <Analytics />
</template>

<script setup>
import { onMounted } from 'vue'
import { useSectionsStore } from './stores/sections'
import { useAISettingsStore } from './stores/aiSettings'
import { useUserStore } from './stores/user'

const sectionsStore = useSectionsStore()
const aiSettingsStore = useAISettingsStore()
const userStore = useUserStore()

onMounted(() => {
  const token = localStorage.getItem('token')
  if (token) {
    sectionsStore.loadFromServer()
    aiSettingsStore.loadFromServer()
    userStore.refreshSections()
  }
})
</script>

<style>
</style>
