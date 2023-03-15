<template>
    <main>
        <p>404</p>
        <div>
            <h1>Not Found</h1>
            <p>This page is not on earth</p>
        </div>
    </main>
</template>

<style scoped>
h1, p {
    margin: 0;
}

main {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    margin-top: 10%;
    font-family: system-ui;
}

main > p {
    font-size: 3rem;
    font-weight: 700;
    color: #10b981;
}

main > div {
    border-color: #e4e4e7;
    border-left-style: solid;
    border-left-width: 1px;
    padding-left: 1.5rem;
    margin-left: 1.5rem;
}

div > h1 {
    font-size: 3rem;
    font-weight: 800;
}
</style>