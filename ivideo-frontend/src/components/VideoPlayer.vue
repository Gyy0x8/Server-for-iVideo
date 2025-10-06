<template>
  <div class="video-player">
    <div class="player-placeholder">
      <div class="placeholder-icon">📺</div>
      <p>视频播放器组件</p>
      <p class="placeholder-hint">实际项目中这里会嵌入真实的视频播放器</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VideoPlayer'
}
</script>

<style scoped>
.video-player {
  padding: 20px;
  text-align: center;
}

.player-placeholder {
  padding: 40px;
  border: 2px dashed #e6e6e6;
  border-radius: 8px;
  background: #fafafa;
  color: #909399;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.placeholder-hint {
  font-size: 12px;
  margin-top: 8px;
}
</style>