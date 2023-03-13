import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import { useUserStore } from '../store'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      component: HomeView,
    },
    {
      path: "/login",
      name: "login",
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/config",
      name: "config",
      component: () => import("../views/ConfigView.vue"),
    },
    {
      path: "/:pathMatch(.*)*",
      name: "NotFound",
      component: () => import("../views/NotFoundView.vue"),
    },
  ],
});

// redirect to login if the user is not logged in
const protectedRoutes = ["home", "config"];
router.beforeEach((to, from, next) => {
    const userStore = useUserStore();
    const isProtected = protectedRoutes.includes(to.name);
    if (isProtected && !userStore.isLoggedIn) {
        next({
        path: "/login",
        });
    } else next();
});

export default router;
