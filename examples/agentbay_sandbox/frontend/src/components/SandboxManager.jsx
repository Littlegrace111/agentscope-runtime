import React, { useState } from 'react'
import './SandboxManager.css'

function SandboxManager({
  sandboxes,
  selectedSandboxId,
  onSandboxSelect,
  onSandboxCreated,
}) {
  const sandboxTypes = ['linux', 'windows', 'browser', 'mobile']
  const [creating, setCreating] = useState({})

  const getStatusBadge = (status) => {
    const badges = {
      active: { text: 'Active', class: 'badge-active' },
      not_initialized: { text: 'Not Ready', class: 'badge-inactive' },
    }
    const badge = badges[status] || badges.not_initialized
    return <span className={`badge ${badge.class}`}>{badge.text}</span>
  }

  const handleCreateSandbox = async (sandboxType, e) => {
    e.stopPropagation()
    setCreating((prev) => ({ ...prev, [sandboxType]: true }))

    try {
      const response = await fetch(
        `/api/sandboxes?sandbox_type=${sandboxType}`,
        {
          method: 'POST',
        }
      )
      const data = await response.json()

      if (data.success && data.sandbox_id) {
        if (onSandboxCreated) {
          onSandboxCreated(data.sandbox_id)
        }
      } else {
        alert(`Failed to create sandbox: ${data.error || 'Unknown error'}`)
      }
    } catch (error) {
      console.error('Error creating sandbox:', error)
      alert(`Error creating sandbox: ${error.message}`)
    } finally {
      setCreating((prev) => ({ ...prev, [sandboxType]: false }))
    }
  }

  // Group sandboxes by type (only include created sandboxes with sandbox_id)
  const sandboxesByType = {}
  sandboxTypes.forEach((type) => {
    sandboxesByType[type] = []
  })

  Object.entries(sandboxes).forEach(([key, sandbox]) => {
    const type = sandbox.sandbox_type || key
    if (sandboxTypes.includes(type)) {
      // Only include created sandboxes (key starts with 's-' and has sandbox_id)
      if (key.startsWith('s-') && sandbox.sandbox_id) {
        sandboxesByType[type].push({ ...sandbox, sandbox_id: key })
      }
      // Ignore uninitialized sandboxes (they will show as empty with Create button)
    }
  })

  return (
    <div className="sandbox-manager">
      <div className="manager-header">
        <h3>Sandbox Manager</h3>
      </div>

      <div className="manager-content">
        {sandboxTypes.map((type) => {
          const typeSandboxes = sandboxesByType[type] || []
          const hasActive = typeSandboxes.some((s) => s.status === 'active')
          const isCreating = creating[type]

          return (
            <div key={type} className="sandbox-type-group">
              <div className="sandbox-type-header">
                <span className="sandbox-type-name">{type.toUpperCase()}</span>
                {!hasActive && (
                  <button
                    className="create-btn"
                    onClick={(e) => handleCreateSandbox(type, e)}
                    disabled={isCreating}
                    title={`Create ${type} sandbox`}
                  >
                    {isCreating ? 'Creating...' : '+ Create'}
                  </button>
                )}
              </div>

              {typeSandboxes.length > 0 ? (
                typeSandboxes.map((sandbox) => {
                  const sandboxId = sandbox.sandbox_id
                  const isSelected = selectedSandboxId === sandboxId

                  return (
                    <div
                      key={sandboxId || type}
                      className={`sandbox-item ${isSelected ? 'selected' : ''}`}
                      onClick={() => {
                        if (sandboxId) {
                          onSandboxSelect(sandboxId)
                        }
                      }}
                    >
                      <div className="sandbox-item-header">
                        <span className="sandbox-name">
                          {sandboxId
                            ? `${type.toUpperCase()} (${sandboxId.substring(0, 8)}...)`
                            : type.toUpperCase()}
                        </span>
                        {getStatusBadge(sandbox.status)}
                      </div>
                      {sandbox.tools_count !== undefined && (
                        <div className="sandbox-info">
                          <span className="info-text">
                            {sandbox.tools_count} tools available
                          </span>
                        </div>
                      )}
                    </div>
                  )
                })
              ) : (
                <div className="sandbox-item empty">
                  <div className="sandbox-item-header">
                    <span className="sandbox-name">{type.toUpperCase()}</span>
                    <span className="badge badge-inactive">Not Created</span>
                  </div>
                  <div className="sandbox-info">
                    <button
                      className="create-btn-small"
                      onClick={(e) => handleCreateSandbox(type, e)}
                      disabled={isCreating}
                    >
                      {isCreating ? 'Creating...' : 'Create'}
                    </button>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default SandboxManager
