import React, { useState } from 'react'
import ChatInterface from './components/ChatInterface'
import SandboxViewer from './components/SandboxViewer'
import './App.css'

function App() {
  const [selectedSandboxId, setSelectedSandboxId] = useState(null)
  const [selectedSandboxType, setSelectedSandboxType] = useState(null)
  const [resourceUrl, setResourceUrl] = useState(null)

  const fetchSandboxInfo = async () => {
    try {
      const response = await fetch('/api/sandboxes')
      const data = await response.json()
      const sandboxEntries = Object.entries(data.sandboxes || {})
      const activeSandbox = sandboxEntries
        .filter(([key]) => key.startsWith('s-'))
        .map(([, info]) => info)
        .find((info) => info.status === 'active' && info.sandbox_id)

      if (activeSandbox) {
        return {
          sandboxId: activeSandbox.sandbox_id,
          sandboxType: activeSandbox.sandbox_type,
        }
      }
    } catch (error) {
      console.error('Error fetching sandbox info:', error)
    }
    return null
  }

  const fetchResourceUrl = async (sandboxId) => {
    if (!sandboxId) return

    try {
      const response = await fetch(`/api/sandboxes/${sandboxId}/resource_url`)
      const data = await response.json()
      if (data.success && data.resource_url) {
        setResourceUrl(data.resource_url)
      } else {
        setResourceUrl(null)
      }
    } catch (error) {
      console.error('Error fetching resource_url:', error)
      setResourceUrl(null)
    }
  }

  const handleToolCall = () => {
    // Refresh resource URL after tool call (in case sandbox was created)
    if (selectedSandboxId) {
      setTimeout(() => {
        fetchResourceUrl(selectedSandboxId)
      }, 1000)
    }
  }

  const handleSandboxResourceEvent = async (eventData) => {
    if (!eventData || !eventData.sandbox_id) {
      return
    }

    const { sandbox_id: sandboxId, sandbox_type: sandboxType, resource_url } =
      eventData

    setSelectedSandboxId(sandboxId)
    setSelectedSandboxType(sandboxType)
    if (resource_url) {
      setResourceUrl(resource_url)
    } else {
      await fetchResourceUrl(sandboxId)
    }

    // Refresh sandbox info to keep state consistent (best effort)
    await fetchSandboxInfo()
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>Multi-Sandbox Agent Chat</h1>
        <p>Chat with AI agent that can control 4 GUI sandboxes</p>
      </header>

      <div className="app-content">
        <div className="app-left">
          <ChatInterface
            onToolCall={handleToolCall}
            onSandboxResource={handleSandboxResourceEvent}
          />
        </div>

        <div className="app-right">
          <SandboxViewer
            sandboxId={selectedSandboxId}
            sandboxType={selectedSandboxType}
            resourceUrl={resourceUrl}
            onRefresh={() => fetchResourceUrl(selectedSandboxId)}
          />
        </div>
      </div>
    </div>
  )
}

export default App
