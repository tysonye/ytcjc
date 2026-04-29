<template>
  <div class="order-manage">
    <div class="page-header">
      <h3>订单管理</h3>
      <el-select v-model="filterStatus" placeholder="订单状态" clearable size="small" style="width:130px">
        <el-option label="待支付" value="pending" />
        <el-option label="已支付" value="paid" />
        <el-option label="已取消" value="cancelled" />
      </el-select>
    </div>
    <el-table :data="filteredOrders" stripe size="small" v-loading="loading">
      <el-table-column prop="order_no" label="订单号" width="200" />
      <el-table-column prop="username" label="用户" width="100" />
      <el-table-column prop="plan_name" label="套餐" width="100" />
      <el-table-column prop="amount" label="金额" width="80">
        <template #default="{ row }">¥{{ row.amount }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button v-if="row.status === 'pending'" size="small" type="success" @click="confirmPay(row)">确认支付</el-button>
          <el-button v-if="row.status === 'pending'" size="small" type="danger" @click="cancelOrder(row)">取消</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const orders = ref([])
const filterStatus = ref('')

const filteredOrders = computed(() => {
  if (!filterStatus.value) return orders.value
  return orders.value.filter(o => o.status === filterStatus.value)
})

function statusType(s) { return { pending: 'warning', paid: 'success', cancelled: 'info' }[s] || '' }
function statusLabel(s) { return { pending: '待支付', paid: '已支付', cancelled: '已取消' }[s] || s }

async function fetchOrders() {
  loading.value = true
  try {
    const token = localStorage.getItem('adminToken')
    const resp = await fetch('/api/admin/orders', { headers: { Authorization: `Bearer ${token}` } })
    orders.value = await resp.json()
  } catch { ElMessage.error('获取订单失败') }
  finally { loading.value = false }
}

async function confirmPay(row) {
  try {
    const token = localStorage.getItem('adminToken')
    await fetch(`/api/admin/orders/${row.id}/confirm`, { method: 'PUT', headers: { Authorization: `Bearer ${token}` } })
    ElMessage.success('确认支付成功')
    fetchOrders()
  } catch { ElMessage.error('操作失败') }
}

async function cancelOrder(row) {
  try {
    const token = localStorage.getItem('adminToken')
    await fetch(`/api/admin/orders/${row.id}/cancel`, { method: 'PUT', headers: { Authorization: `Bearer ${token}` } })
    ElMessage.success('订单已取消')
    fetchOrders()
  } catch { ElMessage.error('操作失败') }
}

onMounted(fetchOrders)
</script>

<style scoped>
.page-header { display:flex;align-items:center;justify-content:space-between;margin-bottom:15px; }
.page-header h3 { margin:0;font-size:18px; }
</style>
