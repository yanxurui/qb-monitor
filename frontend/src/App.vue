<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
    <header>
        <h1>Qbittorrent monitor</h1>
    </header>

    <RouterView />
    <notifications position="bottom right" />
</template>

<style scoped></style>
