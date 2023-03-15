<script setup>
import { RouterView } from 'vue-router'
import TheNavBar from './components/TheNavBar.vue'
</script>

<template>
    <TheNavBar />

    <RouterView />
    <notifications position="bottom right" width="100%"/>
</template>
