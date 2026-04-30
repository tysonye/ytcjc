<template>
  <div class="ai-settings">
    <div class="setting-section">
      <div class="section-title">分析风格</div>
      <el-button-group size="small">
        <el-button
          v-for="(cfg, key) in presetOptions"
          :key="key"
          :type="store.preset === key ? 'primary' : ''"
          @click="store.setPreset(key)"
        >{{ cfg.label }}</el-button>
      </el-button-group>
      <div class="section-hint">{{ presetOptions[store.preset]?.focus }}</div>
    </div>

    <div class="setting-section">
      <div class="section-title">分析偏好</div>
      <el-checkbox-group v-model="store.preferences" @change="store.save()">
        <el-checkbox
          v-for="opt in preferenceOptions"
          :key="opt.key"
          :label="opt.label"
          :value="opt.key"
          size="small"
        />
      </el-checkbox-group>
    </div>

    <div class="setting-section">
      <div class="section-title">回复格式</div>
      <el-radio-group v-model="store.replyFormat" size="small" @change="store.save()">
        <el-radio value="detailed">详细模式</el-radio>
        <el-radio value="concise">简洁模式</el-radio>
      </el-radio-group>
    </div>

    <div class="setting-section">
      <div class="section-title">回复语言</div>
      <el-radio-group v-model="store.replyLanguage" size="small" @change="store.save()">
        <el-radio value="zh">中文</el-radio>
        <el-radio value="bilingual">中英双语</el-radio>
      </el-radio-group>
    </div>

    <div class="setting-section">
      <div class="section-title">自定义提示词</div>
      <el-input
        v-model="store.customPrompt"
        type="textarea"
        :rows="3"
        placeholder="追加自定义指令，如：请特别关注日职联比赛..."
        @input="store.save()"
      />
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAISettingsStore } from '../stores/aiSettings'

const store = useAISettingsStore()
const { preferenceOptions, presetOptions } = store

onMounted(() => {
  store.loadFromServer()
})
</script>

<style scoped>
.ai-settings { padding: 0 4px; }
.setting-section { margin-bottom: 20px; }
.section-title { font-size: 14px; font-weight: 600; color: #303133; margin-bottom: 10px; }
.section-hint { font-size: 12px; color: #999; margin-top: 6px; }
.el-checkbox-group { display: flex; flex-direction: column; gap: 6px; }
</style>
