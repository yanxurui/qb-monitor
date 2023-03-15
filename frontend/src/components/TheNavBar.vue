<template>
    <ul v-show="show">
        <li><RouterLink to="/">Home</RouterLink></li>
        <li><RouterLink to="/config">Config</RouterLink></li>
        <li style="float:right"><a @click.prevent="show_modal = true" href="#">Logout</a></li>
    </ul>

    <ModalConfirm
      v-model="show_modal"
      title="Logout"
      @confirm="() => logout()"
    >
        <div>
            <input type="checkbox" id="checkbox" v-model="checked">
            <label for="checkbox">Logout for all devices</label>
        </div>
    </ModalConfirm>
</template>

<script setup>
import {ref, computed} from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useNotification } from "@kyvg/vue3-notification";
import { useUserStore } from '../store'
import ModalConfirm from '../components/ModalConfirm.vue'

const router = useRouter();
const { notify }  = useNotification();
const userStore = useUserStore();

const show = computed(() => (useRoute().name != "login" && userStore.isLoggedIn));
const show_modal = ref(false)
const checked = ref(false)

async function logout() {
    show_modal.value = false;
    try {
        const response = await fetch('/api/logout', {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({all: checked.value})
        });
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