# Custom Images

Custom images allow you to create tailored environments with specific operating systems, pre-installed software, and configurations that match your business requirements.

## Overview

### What are Custom Images?

Custom images are user-defined environment templates that extend or customize AgentBay's system images or existing custom images. They are ideal for scenarios where:

1. **Production Deployments**: Lock environment versions for production stability to avoid breaking changes from automatic updates
2. **Specialized Software**: Pre-install specific tools, libraries, or applications not included in system images
3. **Team Standardization**: Create standardized environments to ensure all team members use identical development setups
4. **Compliance Requirements**: Configure custom system settings with specific security configurations or compliance-approved software versions
5. **Performance Optimization**: Pre-installing dependencies reduces session startup time

### System Images vs Custom Images

AgentBay provides official **system images** for different use cases:

| Image Type | Use Case | Example |
|------------|----------|---------|
| `linux_latest` | Computer Use | General computing, server tasks |
| `windows_latest` | Computer Use | Windows applications, .NET development |
| `browser_latest` | Browser Use | Web automation, scraping |
| `code_latest` | CodeSpace | Development environments |
| `mobile_latest` | Mobile Use | Android automation |

**Key differences:**

- **System Images**: Maintained by AgentBay, automatically updated to latest versions
- **Custom Images**: Created and maintained by you, version-controlled and stable

### Image ID

The **Image ID** is a unique identifier for each image (both system and custom images). It serves as:

- A credential for SDK and MCP (Model Context Protocol) API calls
- A reference to specify which environment to use when creating sessions

**Example usage:**
```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams

agent_bay = AgentBay()

# Use custom image by Image ID
params = CreateSessionParams(image_id="your_custom_image_id")
session = agent_bay.create(params).session

# Your automation tasks here...

agent_bay.delete(session)
```

## Creating Custom Images

There are two primary methods to create custom images:

### 1. AgentBay Console (UI-Based)

The [AgentBay Console](https://agentbay.console.aliyun.com/) provides a user-friendly interface for creating and managing custom images through visual workflows.

**Key features:**
- Interactive image builder with step-by-step guidance
- Visual selection of base images and configurations
- Real-time preview of image specifications
- Easy management of existing custom images

**Supported image types:**
- Computer Use images (Windows/Linux)
- Mobile Use images (Android)

**Note:** Browser Use images are currently not supported for customization.

**To get started:**
Visit the [AgentBay Console](https://agentbay.console.aliyun.com/) and navigate to the Custom Images section to explore the UI-based creation workflow.

### 2. AgentBay CLI (Command-Line)

The AgentBay CLI provides a programmatic approach to create custom images using Dockerfile-based definitions.

**Key features:**
- Dockerfile-based image definitions
- Command-line automation for CI/CD integration
- Version control for image configurations
- Scriptable and repeatable image builds

**Supported image types:**
- CodeSpace images

**Note:** Computer Use and Mobile Use images should use the AgentBay Console for customization.

**To get started:**
Visit the [AgentBay CLI GitHub repository](https://github.com/aliyun/agentbay-cli) for detailed installation instructions.

**Basic workflow:**
```bash
# 1. Log in to AgentBay
agentbay login

# 2. List available user images
agentbay image list

# 3. Create a custom image
agentbay image create myapp --dockerfile ./Dockerfile --imageId code_latest

# 4. Activate the image
agentbay image activate imgc-xxxxx...xxx

# 5. Deactivate when done
agentbay image deactivate imgc-xxxxx...xxx
```

## Production Environment Best Practices

### Version Stability

**⚠️ Important for Production:**

The `xxxx_latest` system images are automatically updated to newer versions, which may introduce:
- API incompatibilities with older SDK versions
- Unexpected behavior changes
- Breaking changes in pre-installed software

**Recommendation:**
- **Always use custom images with fixed versions in production environments**
- Pin specific versions of dependencies in your custom image definitions
- Test custom images thoroughly before deploying to production
- Maintain separate custom images for development, staging, and production

### Example Production Setup

```python
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams

agent_bay = AgentBay()

# Development: Use latest for new features
dev_params = CreateSessionParams(image_id="browser_latest")

# Production: Use version-locked custom image
prod_params = CreateSessionParams(image_id="my_browser_prod_v1.2.0")

# Create production session with stable environment
session = agent_bay.create(prod_params).session
```

## Availability

**Important Notice**: The Custom Images feature is an exclusive premium feature for paid subscription users (Pro/Ultra). For more details about pricing and subscription plans, please visit the [AgentBay Billing Instructions](https://help.aliyun.com/zh/agentbay/product-overview/agentbay-billing-instructions).

## Next Steps

- Explore the [AgentBay Console](https://agentbay.console.aliyun.com/) to create your first custom image
- Check out the [AgentBay CLI](https://github.com/aliyun/agentbay-cli) for automated image creation
- Review [Session Management](../basics/session-management.md) to learn how to use custom images in your workflows
- See [SDK Configuration](../configuration/sdk-configuration.md) for environment-specific settings

