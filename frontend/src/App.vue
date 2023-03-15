<script setup>
import { RouterView } from 'vue-router'
import TheNavBar from './components/TheNavBar.vue'
import { ModalsContainer } from 'vue-final-modal'
</script>

<template>
    <TheNavBar />
    <RouterView />
    <notifications position="bottom right" width="100%"/>
    <ModalsContainer />
</template>
