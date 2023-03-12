<template>
    <form @submit.prevent="">
        <textarea :rows="countOfLines" v-model="config"></textarea>
        <button @click="updateConfig">submit</button>
    </form>
</template>

<script>
const example = `[
    {
        "name": "localhost",
        "url": "http://localhost:8080",
        "username": "test",
        "password": "123456"
    },
    {
        "name": "remote",
        "url": "http://example.com:8080",
        "username": "test",
        "password": "123456"
    }
]
`
export default {
    data() {
        return {
            config: ""
        }
    },
    mounted() {
        this.getConfig();
    },
    computed: {
        countOfLines() {
            return Math.max(6, this.config.split(/\r\n|\r|\n/).length);
        }
    },
    methods: {
        async getConfig() {
            const response = await fetch("/api/config");
            let body = await response.text();
            if (response.ok) {
                this.config = body;
            } else {
                if (response.status == 401) {
                    this.$router.push("/login");
                }
                if (response.status == 404) {
                    this.config = example;
                    this.$notify({ type: "warn", text: "Your config is empty! An example was populated." });
                } else {
                    this.$notify({ type: "error", title: response.statusText, text: body });
                }
            }
        },
        async updateConfig() {
            const response = await fetch("/api/config", { method: "POST", body: this.config });
            let body = await response.text();
            let type = "error";
            if (response.ok) {
                this.$router.push("/");
                type = "success";
            }
            this.$notify({ type: type, text: body });
        }
    }
}
</script>

<style scoped>
form {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-around;
    align-items: stretch;
}

form textarea {
    flex: 100%;
    overflow: auto;
}

form>button {
    margin: 10px;
}
</style>
