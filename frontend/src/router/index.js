import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    { path: '/', name: 'Home', component: () => import('../views/Home.vue') },
    { path: '/login', name: 'Login', component: () => import('../views/Login.vue') },
    { path: '/register', name: 'Register', component: () => import('../views/Register.vue') },
    {
        path: '/admin',
        name: 'AdminDashboard',
        component: () => import('../views/AdminDashboard.vue'),
        meta: { requiresAuth: true, role: 'admin' }
    },
    {
        path: '/company',
        name: 'CompanyDashboard',
        component: () => import('../views/CompanyDashboard.vue'),
        meta: { requiresAuth: true, role: 'company' }
    },
    {
        path: '/student',
        name: 'StudentDashboard',
        component: () => import('../views/StudentDashboard.vue'),
        meta: { requiresAuth: true, role: 'student' }
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token');
    const role = localStorage.getItem('role');

    if (to.meta.requiresAuth && !token) {
        return next('/login');
    }

    if (to.meta.role && to.meta.role !== role) {
        return next('/'); // Or a "not authorized" page
    }

    // redirect logged-in users away from login/register/home
    if ((to.name === 'Login' || to.name === 'Register' || to.name === 'Home') && token) {
        if (role === 'admin') return next('/admin');
        if (role === 'company') return next('/company');
        if (role === 'student') return next('/student');
    }

    next();
})

export default router
