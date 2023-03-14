<template>
    <div class="container">
        <GoogleLogin :callback="callback" />
    </div>
</template>

<script setup>
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { useNotification } from "@kyvg/vue3-notification";
import { useUserStore } from '../store'
import { decodeCredential } from 'vue3-google-login'

const router = useRouter()
const { notify}  = useNotification()
const userStore = useUserStore()

const callback = async (resp) => {
    // This callback will be triggered when the user selects or login to
    // his Google account from the popup
    // decodeCredential will retrive the JWT payload from the credential
    const userData = decodeCredential(resp.credential)
    console.log(resp.credential)
    console.log("Handle the userData", userData)
    try {
        const response = await fetch('/api/signin', {
            method: "POST",
            body: resp.credential
        });
        if (response.ok) {
            router.push({ name: "home" });
            if (response.status ==201) {
                notify({ type: "success", title: "New account created!" });
            } else {
                notify({ type: "success", title: "Welcome " + userData.given_name + " back!" });
            }
            userStore.login(userData.email);
        } else {
            const errMsg = await response.text();
            notify({ type: "error", title: response.statusText, text: errMsg });
        }
    } catch (error) {
        notify({ type: "error", duration: 8000, text: error });
    }
}

onBeforeRouteLeave ((to, from) => {
    // Delete teh cookie added by google one-tap sign-in
    // because Python's SimpleCookie failed to parse cookie value with double quotes
    document.cookie = 'g_state=; Path=/; Expires=Thu, 01 Jan 1970 00:00:01 GMT;';
})

</script>

<style scoped>
.container {
    margin-top: 5%;
    text-align: center;
}
</style>