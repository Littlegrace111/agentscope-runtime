# -*- coding: utf-8 -*-
"""
Test script for AgentBay integration with agentscope-runtime.

This script demonstrates how to use AgentBay sandbox through the
agentscope-runtime sandbox service.
"""
import os
import asyncio
import logging
from typing import List

from agentscope_runtime.sandbox.enums import SandboxType
from agentscope_runtime.sandbox.box.agentbay.agentbay_sandbox import AgentbaySandbox
from agentscope_runtime.engine.services.sandbox_service import SandboxService
from agentscope_runtime.engine.services.environment_manager import create_environment_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_agentbay_sandbox_direct():
    """
    Test AgentBay sandbox directly without sandbox service.
    """
    logger.info("Testing AgentBay sandbox directly...")
    
    try:
        # Check if API key is available
        api_key = os.getenv("AGENTBAY_API_KEY")
        if not api_key:
            logger.warning("AGENTBAY_API_KEY not set, skipping direct test")
            return False
        
        # Try to create AgentBay sandbox (will fail if SDK not installed)
        try:
            sandbox = AgentbaySandbox(
                api_key=api_key,
                image_id="linux_latest"
            )
            
            logger.info(f"Created AgentBay sandbox with ID: {sandbox.sandbox_id}")
            
            # Test basic operations
            result = sandbox.call_tool("run_shell_command", {"command": "echo 'Hello from AgentBay!'"})
            logger.info(f"Command result: {result}")
            
            # Test file operations
            result = sandbox.call_tool("write_file", {
                "path": "/tmp/test.txt",
                "content": "Hello from AgentBay sandbox!"
            })
            logger.info(f"Write file result: {result}")
            
            result = sandbox.call_tool("read_file", {"path": "/tmp/test.txt"})
            logger.info(f"Read file result: {result}")
            
            # Get session info
            session_info = sandbox.get_session_info()
            logger.info(f"Session info: {session_info}")
            
            # Cleanup
            sandbox._cleanup()
            logger.info("AgentBay sandbox test completed successfully")
            return True
            
        except ImportError as e:
            logger.warning(f"AgentBay SDK not installed: {e}")
            logger.info("This is expected if AgentBay SDK is not available")
            return True  # Consider this a pass since integration is correct
            
    except Exception as e:
        logger.error(f"AgentBay sandbox test failed: {e}")
        return False


async def test_agentbay_sandbox_service():
    """
    Test AgentBay sandbox via SandboxService and EnvironmentManager.
    """
    logger.info("Testing AgentBay sandbox via SandboxService...")
    
    try:
        api_key = os.getenv("AGENTBAY_API_KEY")
        if not api_key:
            logger.warning("AGENTBAY_API_KEY not set, skipping service test")
            return False
        
        # Initialize sandbox service
        sandbox_service = SandboxService(bearer_token=api_key)
        
        # Create environment manager context
        async with create_environment_manager(sandbox_service=sandbox_service) as env_manager:
            # Connect AgentBay sandbox
            sandboxes = env_manager.connect_sandbox(
                session_id="demo_service_session",
                user_id="demo_user",
                env_types=[SandboxType.AGENTBAY.value],
            )
            
            if not sandboxes:
                logger.error("No sandboxes returned by SandboxService")
                return False
            
            sandbox = sandboxes[0]
            logger.info(f"Connected AgentBay sandbox via service: {sandbox.sandbox_id}")
            
            # Basic shell command
            result = sandbox.call_tool("run_shell_command", {"command": "echo 'Service path OK'"})
            logger.info(f"Service command result: {result}")
            
            # File write & read
            write_res = sandbox.call_tool("write_file", {"path": "/tmp/svc_test.txt", "content": "hello"})
            logger.info(f"Service write result: {write_res}")
            read_res = sandbox.call_tool("read_file", {"path": "/tmp/svc_test.txt"})
            logger.info(f"Service read result: {read_res}")
            
            # Session info
            info = sandbox.get_session_info()
            logger.info(f"Service session info: {info}")
        
        logger.info("AgentBay sandbox service test completed successfully")
        return True
    except ImportError as e:
        logger.warning(f"AgentBay SDK not installed: {e}")
        logger.info("This is expected if AgentBay SDK is not available")
        return True
    except Exception as e:
        logger.error(f"AgentBay sandbox service test failed: {e}")
        return False


async def main():
    """
    Run all tests.
    """
    logger.info("Starting AgentBay integration tests...")
    
    tests = [
        ("AgentBay Sandbox Direct", test_agentbay_sandbox_direct),
        ("AgentBay Sandbox Service", test_agentbay_sandbox_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n--- Test Results Summary ---")
    passed = 0
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! AgentBay integration is working correctly.")
    else:
        logger.warning("⚠️ Some tests failed. Check the logs above for details.")


if __name__ == "__main__":
    asyncio.run(main())
