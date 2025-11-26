import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkBreaks from 'remark-breaks'
import './MessageList.css'

function MessageList({ messages, isLoading }) {
  // 预处理内容：将单个换行符转换为 Markdown 硬换行（两个空格 + 换行）
  // 这样可以确保在 Markdown 渲染时保留换行
  const preprocessMarkdown = (content) => {
    // 简单方法：将单个换行符转换为两个空格加换行（Markdown 硬换行语法）
    // 但需要避免在代码块中转换
    let inCodeBlock = false
    const lines = content.split('\n')

    return lines.map((line, index) => {
      // 检查是否是代码块标记
      if (line.trim().startsWith('```')) {
        inCodeBlock = !inCodeBlock
        return line
      }

      // 在代码块中，保持原样
      if (inCodeBlock) {
        return line
      }

      // 不在代码块中，检查是否是列表项或空行
      const isListItem = /^(\s*)([-*+]|\d+\.)\s/.test(line)
      const isEmpty = line.trim() === ''
      const isPrevEmpty = index > 0 && lines[index - 1].trim() === ''
      const isNextEmpty = index < lines.length - 1 && lines[index + 1].trim() === ''

      // 如果是列表项、空行，或前后有空行，保持原样
      if (isListItem || isEmpty || isPrevEmpty || isNextEmpty) {
        return line
      }

      // 否则，在行尾添加两个空格（Markdown 硬换行）
      return line + '  '
    }).join('\n')
  }

  return (
    <div className="message-list">
      {messages.length === 0 && (
        <div className="empty-state">
          <p>Start a conversation with the AI agent</p>
          <p className="hint">Try: "List files in the Linux sandbox"</p>
        </div>
      )}

      {messages.map((message) => (
        <div
          key={message.id}
          className={`message message-${message.role}`}
        >
          <div className="message-header">
            <span className="message-role">
              {message.role === 'user' ? 'You' : 'Agent'}
            </span>
            <span className="message-time">
              {message.timestamp.toLocaleTimeString()}
            </span>
          </div>
          <div className="message-content">
            {message.role === 'assistant' ? (
              // 使用 markdown 渲染助手消息，保留单个换行符
              <ReactMarkdown remarkPlugins={[remarkBreaks]}>
                {preprocessMarkdown(message.content)}
              </ReactMarkdown>
            ) : (
              // 用户消息保持纯文本显示
              message.content.split('\n').map((line, i) => (
                <React.Fragment key={i}>
                  {line}
                  {i < message.content.split('\n').length - 1 && <br />}
                </React.Fragment>
              ))
            )}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message message-assistant">
          <div className="message-content">
            <span className="typing-indicator">Thinking...</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default MessageList
