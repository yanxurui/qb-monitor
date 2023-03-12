<script>
const columns = [
    "dl_info_speed",
    "dl_info_data",
    "up_info_speed",
    "up_info_data",
];
export default {
    data() {
        return {
            now: "",
            qbs: [],
            total: {},
            columns: columns,
            sortKey: "",
            sortOrders: columns.reduce((o, key) => ((o[key] = 1), o), {}),
        };
    },
    created() {
        this.init();
    },
    computed: {
        filteredData() {
            const sortKey = this.sortKey;
            const order = this.sortOrders[sortKey];
            let data = this.qbs;

            if (sortKey) {
                data = data.slice().sort((a, b) => {
                    a = a[sortKey];
                    b = b[sortKey];
                    return (a === b ? 0 : a > b ? 1 : -1) * order;
                });
            }
            return data;
        },
    },
    methods: {
        init() {
            // component is now ready.
            this.columns.forEach((c) => {
                this.total[c] = 0;
            });

            fetch("/api/qbs")
                .then((response) => {
                    if (!response.ok) {
                        return Promise.reject(response);
                    }
                    return response.json();
                })
                .then((data) => {
                    // give each item a unique id
                    let id = 0;

                    this.qbs = data;
                    this.qbs.forEach((qb) => {
                        qb.id = id++;
                        qb.get = function (key) {
                            return this[key];
                        };

                        var s = new Date();

                        fetch("/api/qbs/" + qb.id)
                            .then(function (response) {
                                if (!response.ok) {
                                    throw Error(response.statusText);
                                }
                                return response.json();
                            })
                            .then((data) => {
                                this.error = "";
                                this.now = new Date().toLocaleTimeString();
                                this.columns.forEach((c) => {
                                    let v = data[c];
                                    if (v != undefined) {
                                        qb[c] = v;
                                        this.total[c] += v; // sum up all the values
                                    }
                                });
                                qb.ok = true;
                                var seconds = Math.round((new Date() - s) / 10) / 100;
                                console.log(
                                    "Time elapsed: " + seconds + "seconds for " + qb.id
                                );
                            })
                            .catch((error) => {
                                qb.ok = false;
                                this.$notify({ type: "error", text: error });
                            });
                    });
                })
                .catch((error) => {
                    if (typeof error.text === "function") {
                        const response = error;
                        if (response.status == 401) {
                            this.$router.push("/login");
                        }
                        if (response.status == 404) {
                            this.$notify({ type: "warn", text: "You have no config! Please click the Config button to add your qbs" });
                        } else {
                            response.text().then((errorMsg) => {
                                this.$notify({ type: "error", title: error.statusText, text: errorMsg });
                            });
                        }
                    } else {
                        this.$notify({ type: "error", text: error });
                    }
                });
        },
        sortBy(key) {
            this.sortKey = key;
            this.sortOrders[key] = this.sortOrders[key] * -1;
        },
        getColumnName(c) {
            return c.indexOf("speed") > -1 ? "rate" : "total";
        },
        convertBytesToHumanReadable(num) {
            if (num == undefined) {
                return "-";
            }
            const suffix = "B";
            const units = ["", "K", "M", "G", "T", "P", "E", "Z"];
            for (let unit of units) {
                if (Math.abs(num) < 1024.0) {
                    return num.toFixed(1) + unit + suffix;
                }
                num /= 1024.0;
            }
            return num.toFixed(1) + "Y" + suffix;
        },
    },
};
</script>

<template>
    <table>
        <thead>
            <tr>
                <th rowspan="2">Name</th>
                <th colspan="2">Download</th>
                <th colspan="2">Upload</th>
            </tr>
            <tr>
                <th v-for="c in columns" @click="sortBy(c)" :class="{ active: sortKey == c }">
                    {{ getColumnName(c) }}
                    <span class="arrow" :class="sortOrders[c] > 0 ? 'asc' : 'dsc'"></span>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="qb in filteredData" :key="qb.id">
                <td>
                    <a target="_blank" :href="qb.url">{{ qb.name }}</a>
                </td>
                <td v-for="c in columns">
                    <span v-if="!qb.hasOwnProperty('ok')" class="loading"></span>
                    <span v-else-if="qb.ok">{{
                        this.convertBytesToHumanReadable(qb.get(c))
                    }}</span>
                    <span v-else class="failed">ERR</span>
                </td>
            </tr>
            <tr>
                <td>TOTAL</td>
                <td v-for="c in columns">
                    {{ this.convertBytesToHumanReadable(total[c]) }}
                </td>
            </tr>
        </tbody>
    </table>
    <p><button @click="init">Refresh</button></p>
    <p>
        <span class="success" v-if="now">Synced at {{ now }}</span>
    </p>
</template>

<style>
.error {
    color: red;
}

.success {
    color: green;
}

button {
    border: 2px solid black;
    border-color: #04aa6d;
    color: green;
    background-color: white;
    padding: 10px 20px;
    font-size: 16px;
    cursor: pointer;
}

button:hover {
    background-color: #04aa6d;
    color: white;
}

/* table style */
table {
    width: 100%;
    border-collapse: collapse;
}

tbody>tr:nth-of-type(even) {
    background: rgba(0, 0, 0, 0.05);
}

tbody>tr:hover {
    background-color: #ccc;
}

th,
td {
    border: solid 1px;
}

thead {
    border-bottom: solid 2px;
}

th,
td {
    padding: 0.5rem;
}

th {
    text-align: center;
}

/* 3-dots loading style */
.loading:after {
    overflow: hidden;
    display: inline-block;
    vertical-align: bottom;
    -webkit-animation: ellipsis steps(4, end) 900ms infinite;
    animation: ellipsis steps(4, end) 900ms infinite;
    content: "\2026";
    /* ascii code for the ellipsis character */
    width: 0px;
}

@keyframes ellipsis {
    to {
        width: 1.25em;
    }
}

@-webkit-keyframes ellipsis {
    to {
        width: 1.25em;
    }
}

/* styles for sort */
thead>tr:nth-child(2)>th {
    cursor: pointer;
}

th.active .arrow {
    opacity: 1;
    border-bottom-color: #0f0;
    border-top-color: #0f0;
}

.arrow {
    display: inline-block;
    vertical-align: middle;
    width: 0;
    height: 0;
    margin-left: 5px;
    opacity: 0.66;
}

.arrow.asc {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-bottom: 6px solid #000;
}

.arrow.dsc {
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #000;
}
</style>
