<template>
  <div class="admin-layout">
    <aside class="admin-sidebar">
      <div class="admin-logo">管理后台</div>
      <nav class="admin-nav">
        <router-link to="/admin/members" class="admin-nav-item" :class="{ active: $route.path === '/admin/members' }">会员管理</router-link>
        <router-link to="/admin/orders" class="admin-nav-item" :class="{ active: $route.path === '/admin/orders' }">订单管理</router-link>
        <router-link to="/admin/tokens" class="admin-nav-item" :class="{ active: $route.path === '/admin/tokens' }">Token统计</router-link>
        <router-link to="/admin/stats" class="admin-nav-item" :class="{ active: $route.path === '/admin/stats' }">数据统计</router-link>
        <router-link to="/admin/roles" class="admin-nav-item" :class="{ active: $route.path === '/admin/roles' }">角色权限</router-link>
      </nav>
    </aside>
    <main class="admin-main"><router-view /></main>
  </div>
</template>

<script setup>
</script>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; }
.admin-sidebar { width: 200px; background: #001529; color: #fff; position: fixed; top:0; left:0; bottom:0; z-index:100; }
.admin-logo { padding: 18px 20px; font-size: 16px; font-weight:bold; border-bottom:1px solid rgba(255,255,255,0.1); text-align:center; }
.admin-nav { padding: 10px 0; display:flex; flex-direction:column; }
.admin-nav-item { padding: 12px 24px; color:rgba(255,255,255,0.65); text-decoration:none; font-size:14px; transition:all 0.2s;
  &:hover,&.active { color:#fff; background:#1890ff; }
}
.admin-main { flex:1; margin-left:200px; padding:20px; background:#f0f2f5; min-height:100vh; }
@media(max-width:768px){
  .admin-sidebar{width:60px;} .admin-logo,.admin-nav-item{font-size:0;padding:12px 0;text-align:center;}
  .admin-main{margin-left:60px;padding:10px;}
}
</style>
