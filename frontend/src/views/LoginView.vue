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

        <p class="error" v-if="this.error">
            {{ this.error }}
        </p>
    </form>
</template>

<script>
export default {
    data() {
        return {
            username: "",
            password: "",
            error: "",
        };
    },
    methods: {
        async login_or_register(action) {
            try {
                const response = await fetch('/api/' + action, {
                    method: "POST",
                    body: JSON.stringify({ username: this.username, password: this.password })
                });
                if (response.ok) {
                    this.$router.push({ name: "home" });
                    if (action == 'register') {
                        this.$notify({ type: "success", title: "New account created!" });
                    } else {
                        this.$notify({ type: "success", title: "Welcome " + this.username + " back!" });
                    }
                } else {
                    const errMsg = await response.text();
                    throw Error(response.statusText + ": " + errMsg)
                }
            } catch (error) {
                this.$notify({ type: "error", duration: 8000, text: error });
            }
        }
    },
};
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