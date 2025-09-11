<template>
  <div id="app">
    <router-view />
    <!-- 语音导航组件 - 全局可用 -->
    <VoiceNavigation />
  </div>
</template>

<script setup>
import VoiceNavigation from '@/components/VoiceNavigation.vue'
</script>

<style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

#app {
  height: 100vh;
}
</style> 