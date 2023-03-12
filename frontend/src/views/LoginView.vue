<template>
    <form @submit.prevent="">
        <label for="username"><b>Username</b></label>
        <input class="form-control" v-model="username" type="text" name="username" placeholder="username@xample.com" required />
        <label for="password"><b>Password</b></label>
        <input class="form-control" v-model="password" type="password" name="password" placeholder="password123" required />

        <button type="submit" @click="login_or_register('login')">
            Login
        </button>
        <p>You don't have an account? <a class="a-button" @click.prevent="login_or_register('register')">Register</a></p>
    </form>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useNotification } from "@kyvg/vue3-notification";
import { useUserStore } from '../store'

const router = useRouter()
const { notify}  = useNotification()
const userStore = useUserStore()

const username = ref("");
const password = ref("");

const isEmpty = (str) => (!str?.length);

async function login_or_register(action) {
    try {
        if (isEmpty(username.value) || isEmpty(password.value)) {
            notify({type: "error", text: "Empty username or password"});
            return
        }

        const response = await fetch('/api/' + action, {
            method: "POST",
            body: JSON.stringify({ username: username.value, password: password.value })
        });
        if (response.ok) {
            router.push({ name: "home" });
            if (action == 'register') {
                notify({ type: "success", title: "New account created!" });
            } else {
                notify({ type: "success", title: "Welcome " + username.value + " back!" });
            }
            userStore.login(username.value);
        } else {
            const errMsg = await response.text();
            notify({ type: "error", title: response.statusText, text: errMsg });
        }
    } catch (error) {
        notify({ type: "error", duration: 8000, text: error });
    }
}
</script>

<style scoped>
.container {
    text-align: center;
}

form {
    border: 3px solid #f1f1f1;
    padding: 16px;
    margin: 0 auto;
    max-width: 500px;
}

input {
    width: 100%;
    padding: 12px 20px;
    margin: 8px 0;
    display: inline-block;
    border: 1px solid #ccc;
    box-sizing: border-box;
}

button {
    background-color: #04AA6D;
    color: white;
    padding: 14px 20px;
    margin: 8px 0;
    border: none;
    cursor: pointer;
    width: 100%;
}

.a-button {
    color: green;
    cursor: pointer;
}

button:hover {
    opacity: 0.8;
}
</style>