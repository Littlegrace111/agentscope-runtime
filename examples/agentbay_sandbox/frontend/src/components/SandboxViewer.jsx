import React from 'react'
import './SandboxViewer.css'

function SandboxViewer({ sandboxId, sandboxType, resourceUrl, onRefresh }) {
  return (
    <div className="sandbox-viewer">
      <div className="viewer-header">
        <h3>Sandbox Viewer</h3>
        {sandboxId && (
          <div className="viewer-actions">
            <span className="sandbox-id">
              {sandboxType ? `${sandboxType.toUpperCase()} | ` : ''}
              ID: {sandboxId}
            </span>
            <button
              onClick={onRefresh}
              className="refresh-btn"
              title="Refresh resource URL"
              disabled={!onRefresh}
            >
              🔄
            </button>
          </div>
        )}
      </div>

      <div className="viewer-content">
        {resourceUrl ? (
          <div className="iframe-container">
            <iframe
              src={resourceUrl}
              title="Sandbox Environment"
              className="sandbox-iframe"
              allow="camera; microphone; fullscreen"
              sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals"
            />
          </div>
        ) : (
          <div className="viewer-placeholder">
            <div className="placeholder-icon">🖥️</div>
            <p>No sandbox selected</p>
            <p className="hint">
              {sandboxId
                ? 'Loading resource URL...'
                : 'Sandboxes are created automatically when the agent needs them'}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

export default SandboxViewer
