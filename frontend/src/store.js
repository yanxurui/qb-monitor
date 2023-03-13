import {ref, computed} from 'vue'
import { defineStore } from 'pinia'
import { useLocalStorage } from "@vueuse/core";

export const useUserStore = defineStore("user", () => {
    const user = ref(
        useLocalStorage("userinfo", {})
    );
    const isLoggedIn = computed(() => user.value.username != null);
    function login(username) {
        user.value.username = username;
    }
    function logout() {
        user.value.username = null;
    }
    return { user, isLoggedIn, login, logout }
  });
