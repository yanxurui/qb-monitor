<template>
    <ul v-show="userStore.isLoggedIn">
        <li><RouterLink to="/">Home</RouterLink></li>
        <li><RouterLink to="/config">Config</RouterLink></li>
        <li style="float:right"><a @click.prevent="logout" href="#">Logout</a></li>
    </ul>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useNotification } from "@kyvg/vue3-notification";
import { useUserStore } from '../store'

const router = useRouter();
const { notify }  = useNotification();
const userStore = useUserStore();

async function logout() {
    try {
        const response = await fetch('/api/logout', { method: "POST" });
        if (response.ok) {
            router.push({ name: "login" });
            userStore.logout();
            notify({
                title: "Authorization",
                text: "You have been logged out!",
            });
        }
        else {
            const errorMsg = await response.text();
            notify({ type: "error", title: response.statusText, text: errorMsg });
        }
    }
    catch (error) {
        notify({ type: "error", text: error });
    }
}
</script>

<style scoped>
ul {
    list-style-type: none;
    padding: 0;
    margin: 0;
    overflow: hidden;
    background-color: #009688;
}

li {
    float: left;
}

li a {
    display: block;
    color: white;
    text-align: center;
    padding: 14px 16px;
    text-decoration: none;
}

li a:hover:not(.active) {
    background-color: #111;
}

.active {
    background-color: #04AA6D;
}
</style>