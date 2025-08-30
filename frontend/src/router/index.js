// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import SubmitIdeaView from '../views/SubmitIdeaView.vue'
import IdeaListView from '../views/IdeaListView.vue'
import IdeaDetailView from '../views/IdeaDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/ideas', name: 'ideas', component: IdeaListView },
    { path: '/ideas/:id', name: 'idea-detail', component: IdeaDetailView },
    
    // --- 我们来改造“提交创意”的路由规则 ---
    {
      path: '/submit-idea',
      name: 'submit-idea',
      component: SubmitIdeaView,
      // 1. 添加 meta 字段，像给这个路由贴一个标签
      meta: { requiresAuth: true } // 这个标签的意思是：需要认证
    }
  ]
})

// 2. 在这里，我们创建我们的“全局路由守卫” (保安)
// router.beforeEach 是一个函数，它会在每一次路由跳转发生“之前”被调用
router.beforeEach((to, from, next) => {
  // to: 用户想要去的那个页面的路由信息
  // from: 用户当前所在的页面的路由信息
  // next: 一个必须被调用的函数，用来“放行”

  // 检查用户想去的页面 (to) 是否被贴上了 'requiresAuth' 的标签
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 如果需要认证，我们就检查用户的“口袋”里有没有 token
    if (!localStorage.getItem('token')) {
      // 如果没有 token，就把他带到登录页
      alert('请先登录才能访问此页面！');
      next({ name: 'login' }); 
    } else {
      // 如果有 token，就放行
      next(); 
    }
  } else {
    // 如果页面不需要认证，直接放行
    next(); 
  }
});

export default router