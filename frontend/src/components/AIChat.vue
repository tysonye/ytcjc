<template>
  <div class="ai-chat" :class="{ expanded: isExpanded, inline: inline }">
    <div v-if="!inline" class="chat-toggle" @click="isExpanded = !isExpanded">
      <span class="toggle-label">AI 足球分析师</span>
      <el-icon :class="{ rotated: isExpanded }"><ArrowDown /></el-icon>
    </div>
    <div class="chat-body" v-show="inline || isExpanded">
      <div class="chat-messages" ref="msgContainer">
        <div v-for="(msg, i) in messages" :key="i" class="message" :class="msg.role">
          <div class="msg-avatar">
            <el-icon v-if="msg.role === 'assistant'"><ChatDotRound /></el-icon>
            <el-icon v-else><User /></el-icon>
          </div>
          <div class="msg-content" v-html="renderMarkdown(msg.content)"></div>
        </div>
        <div v-if="typing" class="message assistant">
          <div class="msg-avatar"><el-icon><ChatDotRound /></el-icon></div>
          <div class="msg-content typing"><span></span><span></span><span></span></div>
        </div>
      </div>
      <div class="chat-input">
        <el-input v-model="inputText" placeholder="询问比赛分析..." @keyup.enter="send" :disabled="sending" />
        <el-button type="primary" :loading="sending" @click="send" :disabled="!inputText.trim()">发送</el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, computed } from 'vue'
import { ArrowDown, ChatDotRound, User } from '@element-plus/icons-vue'
import { marked } from 'marked'
import { useAISettingsStore } from '../stores/aiSettings'
import { useUserStore } from '../stores/user'

const props = defineProps({ matchId: { type: [String, Number], default: '' }, inline: { type: Boolean, default: false }, matchContext: { type: String, default: '' } })

const aiSettings = useAISettingsStore()
const userStore = useUserStore()

const isExpanded = ref(false)
const welcomeMsg = computed(() => {
  if (props.matchContext) {
    return '您好！我是AI足球分析师。\n\n当前比赛：' + props.matchContext + '\n\n您可以直接询问关于这场比赛的分析，例如赔率走势、历史交锋、球队状态等。'
  }
  return '您好！我是AI足球分析师，可以帮您分析比赛赔率走势、历史交锋、球队状态等信息。\n\n请从左侧列表选择一场比赛，我将为您进行针对性分析。'
})
const messages = ref([
  { role: 'assistant', content: welcomeMsg.value }
])

watch(welcomeMsg, (val) => {
  if (messages.value.length === 1 && messages.value[0].role === 'assistant') {
    messages.value[0].content = ''
    const chars = val.split('')
    let idx = 0
    const timer = setInterval(() => {
      if (idx < chars.length) {
        messages.value[0].content += chars[idx]
        idx++
      } else {
        clearInterval(timer)
      }
    }, 20)
  }
})
const inputText = ref('')
const sending = ref(false)
const typing = ref(false)
const msgContainer = ref(null)

function renderMarkdown(text) {
  try { return marked.parse(text) } catch { return text }
}

async function send() {
  const text = inputText.value.trim()
  if (!text || sending.value) return
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  scrollToBottom()
  sending.value = true
  typing.value = true

  try {
    const headers = { 'Content-Type': 'application/json' }
    if (userStore.token) {
      headers['Authorization'] = `Bearer ${userStore.token}`
    }
    const resp = await fetch('/api/proxy/ai-chat', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        message: text,
        context: props.matchContext || (props.matchId ? `当前查看的比赛ID: ${props.matchId}` : ''),
        settings: aiSettings.getSettings(),
      }),
    })
    if (resp.status === 401) {
      typing.value = false
      messages.value.push({ role: 'assistant', content: '登录已过期，请重新登录后使用AI预测功能。' })
      return
    }
    const data = await resp.json()
    typing.value = false
    messages.value.push({ role: 'assistant', content: data.reply || '抱歉，暂时无法回答您的问题。' })
  } catch (e) {
    typing.value = false
    messages.value.push({ role: 'assistant', content: '网络连接失败，请稍后重试。' })
  } finally {
    sending.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (msgContainer.value) msgContainer.value.scrollTop = msgContainer.value.scrollHeight
  })
}
</script>

<style lang="scss" scoped>
.ai-chat {
  position: fixed;
  bottom: 70px;
  right: 20px;
  z-index: 200;
  width: 360px;
  max-height: 500px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.15);
  overflow: hidden;
  transition: max-height 0.3s ease;

  @media (max-width: 768px) {
    width: calc(100% - 20px);
    right: 10px;
    bottom: 65px;
  }
  &.expanded { max-height: 520px; }
  &.inline {
    position: static;
    width: 100%;
    max-height: none;
    border-radius: 0;
    box-shadow: none;
    height: 100%;
    .chat-body { height: 100%; }
  }
}

.chat-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: linear-gradient(135deg, #1890ff, #096dd9);
  color: #fff;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  .el-icon { transition: transform 0.3s; }
  .rotated { transform: rotate(180deg); }
}

.chat-body {
  display: flex;
  flex-direction: column;
  height: 380px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.message {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  &.user { flex-direction: row-reverse; .msg-content { background: #e6f7ff; } }
  &.assistant { .msg-content { background: #f5f5f5; } }
}

.msg-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
  color: #666;
}

.msg-content {
  max-width: 75%;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.6;
  word-break: break-word;
  :deep(p) { margin: 4px 0; }
  :deep(pre) { background: #282c34; color: #abb2bf; padding: 8px; border-radius: 4px; overflow-x: auto; font-size: 12px; }
  :deep(table) { border-collapse: collapse; width: 100%; font-size: 12px; th,td { border:1px solid #eee;padding:4px 6px;} }
}

.typing span {
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #999;
  margin: 0 2px;
  animation: typing-bounce 1.4s infinite both;
  &:nth-child(2) { animation-delay: 0.2s; }
  &:nth-child(3) { animation-delay: 0.4s; }
}
@keyframes typing-bounce { 0%,80%,100%{transform:scale(0.6);opacity:.4} 40%{transform:scale(1);opacity:1} }

.chat-input {
  display: flex;
  gap: 6px;
  padding: 10px 12px;
  border-top: 1px solid #eee;
}
</style>
