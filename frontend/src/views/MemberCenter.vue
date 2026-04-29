<template>
  <div class="member-center">
    <el-row :gutter="20">
      <el-col :xs="24" :sm="24" :md="8">
        <el-card class="user-card">
          <template #header>
            <span>个人信息</span>
          </template>
          <div class="user-profile">
            <el-avatar :size="64" :icon="UserFilled" />
            <h3>{{ userStore.userInfo?.username }}</h3>
            <el-tag :type="levelType" size="small">{{ levelLabel }}</el-tag>
            <p class="expire-info" v-if="userStore.userInfo?.membership_expires_at">
              到期时间: {{ formatDate(userStore.userInfo.membership_expires_at) }}
            </p>
          </div>
        </el-card>

        <el-card class="token-card" style="margin-top:15px">
          <template #header><span>Token 使用量</span></template>
          <div class="token-info">
            <el-progress :percentage="tokenPercent" :status="tokenStatus" />
            <p>已用: {{ userStore.userInfo?.token_used || 0 }} / {{ userStore.userInfo?.token_quota || 0 }}</p>
          </div>
        </el-card>
      </el-col>

      <el-col :xs="24" :sm="24" :md="16">
        <el-card>
          <template #header><span>升级会员</span></template>
          <div class="plans">
            <div v-for="plan in plans" :key="plan.level"
                 class="plan-item" :class="{ active: plan.level === currentLevel, recommended: plan.recommended }">
              <div class="plan-name">{{ plan.name }}</div>
              <div class="plan-price">¥{{ plan.price }}<small>/月</small></div>
              <ul class="plan-features">
                <li v-for="f in plan.features" :key="f">{{ f }}</li>
              </ul>
              <el-button :type="plan.level === currentLevel ? 'info' : 'primary'"
                         :disabled="plan.level === currentLevel"
                         @click="handleUpgrade(plan.level)">
                {{ plan.level === currentLevel ? '当前等级' : '立即开通' }}
              </el-button>
            </div>
          </div>
        </el-card>

        <el-card style="margin-top:15px">
          <template #header><span>订单记录</span></template>
          <el-table :data="orders" stripe size="small" empty-text="暂无订单记录">
            <el-table-column prop="order_no" label="订单号" width="180" />
            <el-table-column prop="plan_name" label="套餐" width="100" />
            <el-table-column prop="amount" label="金额" width="80">
              <template #default="{ row }">¥{{ row.amount }}</template>
            </el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template #default="{ row }">
                <el-tag :type="row.status === 'paid' ? 'success' : 'warning'" size="small">
                  {{ row.status === 'paid' ? '已支付' : '待支付' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { UserFilled } from '@element-plus/icons-vue'
import request from '../utils/request'

const userStore = useUserStore()
const orders = ref([])

const plans = [
  {
    level: 'free', name: '免费版', price: 0,
    features: ['基础比赛列表查看', '球探数据基础板块', '每日5次AI对话'],
    recommended: false,
  },
  {
    level: 'silver', name: '白银会员', price: 29,
    features: ['全部数据源访问', '完整球探数据分析', '500/澳门数据基础', '每日30次AI对话'],
    recommended: false,
  },
  {
    level: 'gold', name: '黄金会员', price: 59,
    features: ['全部数据源+高级分析', '完整500/澳门数据', '自定义板块配置', '每日100次AI对话', '历史数据回溯7天'],
    recommended: true,
  },
  {
    level: 'diamond', name: '钻石会员', price: 99,
    features: ['所有功能完全开放', '无限AI对话', '历史数据无限制', '专属客服支持', 'API接口权限'],
    recommended: false,
  },
]

const currentLevel = computed(() => userStore.membershipLevel)
const levelType = computed(() => ({ free: 'info', silver: '', gold: 'warning', diamond: 'danger' }[currentLevel.value] || 'info'))
const levelLabel = computed(() => ({ free: '免费用户', silver: '白银会员', gold: '黄金会员', diamond: '钻石会员' }[currentLevel.value] || '免费用户'))

const tokenPercent = computed(() => {
  const quota = userStore.userInfo?.token_quota || 0
  const used = userStore.userInfo?.token_used || 0
  return quota > 0 ? Math.round((used / quota) * 100) : 0
})
const tokenStatus = computed(() => {
  if (tokenPercent.value >= 90) return 'exception'
  if (tokenPercent.value >= 70) return 'warning'
  return ''
})

function formatDate(d) {
  try { return new Date(d).toLocaleDateString('zh-CN') } catch { return d }
}

async function handleUpgrade(level) {
  try {
    const data = await request.post('/orders/create', { plan_level: level })
    ElMessage.success(`订单已创建，请完成支付: ${data.order_no}`)
    fetchOrders()
  } catch (e) {}
}

async function fetchOrders() {
  try {
    orders.value = await request.get('/orders/my')
  } catch (e) {}
}

onMounted(async () => {
  await userStore.fetchUserInfo()
  fetchOrders()
})
</script>

<style lang="scss" scoped>
@use '../styles/variables' as *;

.user-profile { text-align: center; }
.user-profile h3 { margin: 10px 0 6px; }
.expire-info { font-size: 12px; color: $text-secondary; margin-top: 8px; }
.token-info p { margin-top: 8px; font-size: 13px; color: $text-secondary; }

.plans { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }

.plan-item {
  border: 2px solid #eee;
  border-radius: 10px;
  padding: 20px;
  text-align: center;
  transition: all 0.2s;

  &.active { border-color: $primary-color; background: #f0f7ff; }
  &.recommended { border-color: $danger-color; position: relative;
    &::before { content: '推荐'; position: absolute; top:-1px; right:15px; background:$danger-color;color:#fff;font-size:11px;padding:2px 8px;border-radius:0 0 4px 4px;}
  }
}
.plan-name { font-size: 16px; font-weight: bold; margin-bottom: 8px; }
.plan-price { font-size: 28px; color: $primary-color; font-weight: bold; small { font-size: 13px; color: $text-secondary; font-weight: normal; } }
.plan-features { text-align: left; margin: 15px 0; padding-left: 20px; font-size: 13px; color: $text-secondary;
  li { margin-bottom: 6px; }
}
</style>
