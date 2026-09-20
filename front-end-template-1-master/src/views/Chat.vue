<template>
  <div class="chat-container">
    <div class="chat-box">
      <div class="chat-title">
        <img src="../assets/logo.png" style="width:70px;height:70px;" alt="">
        智能数据分析问答
        <button class="new-chat" @click="newChat()">新对话</button>
      </div>
      <div class="chat-messages" ref="messages">
        <div v-if="messages.length === 0" class="chat-empty">
          <p>用自然语言提问，Agent 会自动生成 SQL 查询数据库并回答。</p>
          <div class="examples">
            <span v-for="e in examples" :key="e" @click="ask(e)">{{ e }}</span>
          </div>
        </div>
        <div v-for="(msg, i) in messages" :key="i" class="msg-row" :class="msg.role">
          <div class="msg-bubble">
            <div v-if="msg.answer_html" class="msg-text" v-html="msg.answer_html"></div>
            <div v-else class="msg-text">{{ msg.text }}</div>

            <div v-if="msg.summary && msg.summary.length" class="msg-summary">
              <div v-for="(s, si) in msg.summary" :key="si" class="summary-item">
                <span class="summary-label">{{ s.label }}</span>
                <span class="summary-value">{{ s.value }}</span>
              </div>
            </div>

            <div v-if="msg.prediction && msg.prediction.predictions && msg.prediction.predictions.length" class="msg-prediction">
              <div class="prediction-title">病情预测（仅供参考）</div>
              <div v-for="(p, pi) in msg.prediction.predictions" :key="pi" class="prediction-item">
                <span class="prediction-disease">{{ p.disease }}</span>
                <span class="prediction-bar"><span class="prediction-fill" :style="{ width: (p.prob * 100).toFixed(1) + '%' }"></span></span>
                <span class="prediction-prob">{{ (p.prob * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div v-if="msg.chart && msg.chart.option" class="msg-chart">
              <div class="chart-title">{{ msg.chart.title }}</div>
              <result-chart :option="msg.chart.option" />
            </div>

            <details v-if="msg.sql" class="msg-sql">
              <summary>执行 SQL</summary>
              <pre>{{ msg.sql }}</pre>
            </details>

            <details v-if="msg.data && msg.data.columns && msg.data.columns.length" class="msg-data">
              <summary>查询结果（{{ msg.data.rows ? msg.data.rows.length : 0 }} 行）</summary>
              <table>
                <thead>
                  <tr><th v-for="c in msg.data.columns" :key="c">{{ c }}</th></tr>
                </thead>
                <tbody>
                  <tr v-for="(r, ri) in msg.data.rows" :key="ri">
                    <td v-for="(v, ci) in r" :key="ci">{{ v }}</td>
                  </tr>
                </tbody>
              </table>
            </details>
          </div>
        </div>
      </div>
      <div class="chat-input">
        <input
          type="text"
          v-model="question"
          placeholder="例如：哪个年龄段的患者最多？"
          @keyup.enter="ask()"
        />
        <button @click="ask()" :disabled="loading">发送</button>
      </div>
    </div>
  </div>
</template>

<script>
import ResultChart from '@/components/ResultChart.vue'
export default {
  name: 'Chat',
  components: { ResultChart },
  data() {
    return {
      question: '',
      sessionId: '',
      messages: [],
      loading: false,
      examples: [
        '一共有多少条病例？',
        '哪种疾病人数最多？',
        '高血压患者的男女比例是多少？',
        '40岁以上患糖尿病的有多少人？',
        '哪个科室接诊的患者最多？'
      ]
    }
  },
  created() {
    this.resetSession()
  },
  methods: {
    resetSession() {
      this.sessionId = 'sess-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8)
    },
    newChat() {
      this.messages = []
      this.question = ''
      this.resetSession()
    },
    async ask(q) {
      const text = (q || this.question || '').trim()
      if (!text || this.loading) return
      this.question = ''
      this.messages.push({ role: 'user', text })
      const agentMsg = { role: 'agent', text: '思考中…', answer_html: '', summary: null, chart: null, sql: '', data: null, prediction: null }
      this.messages.push(agentMsg)
      this.loading = true
      this.scrollBottom()
      const base = this.$http.defaults.baseURL || ''
      let streamedText = ''
      try {
        const res = await fetch(base + '/chat/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: text, session_id: this.sessionId })
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err.message || ('HTTP ' + res.status))
        }
        const reader = res.body.getReader()
        const decoder = new TextDecoder('utf-8')
        let buffer = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          let idx
          while ((idx = buffer.indexOf('\n\n')) >= 0) {
            const raw = buffer.slice(0, idx).trim()
            buffer = buffer.slice(idx + 2)
            if (!raw.startsWith('data:')) continue
            let payload
            try { payload = JSON.parse(raw.slice(5).trim()) } catch (e) { continue }
            if (payload.type === 'token') {
              streamedText += payload.content
              agentMsg.text = streamedText
            } else if (payload.type === 'done') {
              agentMsg.text = payload.answer || streamedText || '（无回答）'
              agentMsg.answer_html = payload.answer_html || ''
              agentMsg.sql = payload.sql || ''
              agentMsg.data = payload.data || null
              agentMsg.summary = payload.summary || null
              agentMsg.chart = payload.chart || null
              agentMsg.prediction = payload.prediction || null
            } else if (payload.type === 'error') {
              agentMsg.text = '调用失败：' + (payload.message || '未知错误')
            }
            this.scrollBottom()
          }
        }
      } catch (e) {
        agentMsg.text = '调用失败：' + (e.message || e)
      } finally {
        this.loading = false
        this.scrollBottom()
      }
    },
    scrollBottom() {
      this.$nextTick(() => {
        const el = this.$refs.messages
        if (el) el.scrollTop = el.scrollHeight
      })
    }
  }
}
</script>

<style lang="less" scoped>
.chat-container {
  width: 100%;
  height: calc(100vh - 120px);
  display: flex;
  justify-content: center;
  .chat-box {
    width: 70%;
    min-width: 700px;
    display: flex;
    flex-direction: column;
    background: rgba(10, 30, 55, 0.55);
    border: 1px solid #1b2d4a;
    border-radius: 12px;
    padding: 20px;
    .chat-title {
      color: #26fffd;
      font-size: 26px;
      font-weight: bold;
      display: flex;
      align-items: center;
      margin-bottom: 15px;
      .new-chat {
        margin-left: auto;
        padding: 6px 16px;
        border-radius: 16px;
        background: transparent;
        border: 1px solid #26fffd;
        color: #26fffd;
        font-size: 14px;
        cursor: pointer;
        &:hover { background: #1b2d4a; }
      }
    }
    .chat-messages {
      flex: 1;
      overflow-y: auto;
      padding: 10px;
      .chat-empty {
        color: #7aa7c9;
        font-size: 15px;
        text-align: center;
        margin-top: 60px;
        .examples {
          margin-top: 20px;
          span {
            display: inline-block;
            margin: 6px;
            padding: 8px 16px;
            border: 1px solid #26fffd;
            border-radius: 20px;
            color: #26fffd;
            cursor: pointer;
            &:hover { background: #1b2d4a; }
          }
        }
      }
      .msg-row {
        display: flex;
        margin-bottom: 14px;
        &.user { justify-content: flex-end; }
        &.agent { justify-content: flex-start; }
        .msg-bubble {
          max-width: 85%;
          background: #10263f;
          border: 1px solid #1b2d4a;
          border-radius: 10px;
          padding: 12px 16px;
          color: #d3dcf7;
          font-size: 15px;
          line-height: 1.6;
          .msg-text {
            white-space: pre-wrap;
            h1, h2, h3 { color: #26fffd; font-size: 16px; margin: 8px 0 4px; }
            h4, h5, h6 { color: #26fffd; font-size: 14px; margin: 6px 0 3px; }
            strong { color: #ffd479; }
            code { background: #0a1626; padding: 1px 5px; border-radius: 4px; color: #ffd479; }
            pre { background: #0a1626; padding: 8px; border-radius: 6px; color: #ffd479; overflow-x: auto; }
            ul, ol { margin: 6px 0; padding-left: 20px; }
            li { margin: 3px 0; }
            blockquote { border-left: 3px solid #26fffd; padding-left: 10px; color: #7aa7c9; margin: 6px 0; }
            hr { border: none; border-top: 1px solid #2a4a6a; margin: 8px 0; }
          }
          .msg-summary {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
            .summary-item {
              background: #0a1626;
              border: 1px solid #2a4a6a;
              border-radius: 8px;
              padding: 8px 14px;
              .summary-label { display: block; color: #7aa7c9; font-size: 12px; margin-bottom: 2px; }
              .summary-value { color: #26fffd; font-size: 16px; font-weight: bold; }
            }
          }
          .msg-prediction {
            margin-top: 10px;
            background: #0a1626;
            border: 1px solid #2a4a6a;
            border-radius: 8px;
            padding: 10px 14px;
            .prediction-title { color: #ffd479; font-size: 13px; margin-bottom: 8px; }
            .prediction-item {
              display: flex;
              align-items: center;
              margin-bottom: 6px;
              &:last-child { margin-bottom: 0; }
              .prediction-disease { width: 70px; color: #d3dcf7; font-size: 13px; flex-shrink: 0; }
              .prediction-bar {
                flex: 1;
                height: 10px;
                background: #16324f;
                border-radius: 5px;
                overflow: hidden;
                margin: 0 10px;
                .prediction-fill { display: block; height: 100%; background: #26fffd; border-radius: 5px; }
              }
              .prediction-prob { color: #26fffd; font-size: 13px; font-weight: bold; width: 52px; text-align: right; }
            }
          }
          .msg-chart {
            margin-top: 10px;
            .chart-title { color: #26fffd; font-size: 14px; margin-bottom: 6px; }
          }
          .msg-sql {
            margin-top: 10px;
            summary { cursor: pointer; color: #26fffd; font-size: 13px; outline: none; }
            pre {
              background: #0a1626;
              padding: 8px;
              border-radius: 6px;
              color: #ffd479;
              font-size: 13px;
              overflow-x: auto;
              margin-top: 6px;
            }
          }
          .msg-data {
            margin-top: 10px;
            summary { cursor: pointer; color: #26fffd; font-size: 13px; outline: none; }
            table {
              border-collapse: collapse;
              font-size: 13px;
              margin-top: 6px;
              th, td {
                border: 1px solid #2a4a6a;
                padding: 4px 8px;
                text-align: left;
              }
              th { background: #16324f; color: #26fffd; }
            }
          }
        }
      }
    }
    .chat-input {
      display: flex;
      margin-top: 10px;
      input {
        flex: 1;
        height: 40px;
        border-radius: 20px;
        background: #0a1626;
        border: 1px solid #26fffd;
        outline: none;
        color: #d3dcf7;
        padding: 0 18px;
        font-size: 15px;
      }
      button {
        width: 90px;
        margin-left: 10px;
        border-radius: 20px;
        background: #26fffd;
        color: #000;
        border: none;
        cursor: pointer;
        font-size: 15px;
        &:disabled { opacity: 0.5; cursor: not-allowed; }
      }
    }
  }
}
</style>
