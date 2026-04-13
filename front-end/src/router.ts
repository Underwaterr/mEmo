import { createRouter, createWebHistory } from 'vue-router'
import HomeView from './views/HomeView.vue'
import LoginView from './views/LoginView.vue'
import ProtectedView from './views/ProtectedView.vue'
import NotFoundView from './views/NotFoundView.vue'

const routes = [
  { path: '/', component: HomeView },
  { path: '/login', component: LoginView },
  { path: '/protected', component: ProtectedView },

  // 404 page for any path not caught by earlier routes
  { path: '/:pathMatch(.*)*', component: NotFoundView }
]

const router = createRouter({
  // use nice URLs (`/page` rather than `/#/page`)
  history: createWebHistory(),
  routes,
})

export default router
