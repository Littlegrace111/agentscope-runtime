# Browser Fingerprint Guide

Browser fingerprinting is a crucial feature for web automation that helps avoid detection by anti-bot systems. AgentBay provides comprehensive fingerprint management capabilities including generation, customization, and persistence across sessions.

## Overview

AgentBay supports advanced browser fingerprint management with the following key capabilities:

- **Multiple Generation Methods**: Random generation, local browser sync, and custom construction
- **Fingerprint Persistence**: Maintain consistent fingerprints across multiple sessions
- **Context Management**: Persistent storage using browser and fingerprint contexts

## 1. Fingerprint Generation Methods

### 1.1 Random Fingerprint Generation

Generate random fingerprints based on specified criteria such as device type, operating system, and locale.

#### Features
- Automatic randomization of browser characteristics
- Configurable device types (desktop/mobile)
- Operating system selection (Windows, macOS, Linux, Android, iOS)
- Locale and language customization

#### Python Example

```python
import os
import asyncio
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption, BrowserFingerprint
from playwright.async_api import async_playwright

async def random_fingerprint_example():
    # Initialize AgentBay client
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)

    # Create session
    params = CreateSessionParams(image_id="browser_latest")
    session_result = agent_bay.create(params)

    if session_result.success:
        session = session_result.session

        # Configure random fingerprint
        browser_fingerprint = BrowserFingerprint(
            devices=["desktop"],
            operating_systems=["windows", "macos"],
            locales=["en-US", "zh-CN"]
        )

        # Enable stealth mode with random fingerprint
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint=browser_fingerprint
        )

        # Initialize browser
        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()

            # Connect using Playwright
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()

                # Test fingerprint
                await page.goto("https://httpbin.org/user-agent")
                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                print(f"Random User Agent: {response.get('user-agent')}")

                # Check navigator properties
                nav_info = await page.evaluate("""
                    () => ({
                        platform: navigator.platform,
                        language: navigator.language,
                        hardwareConcurrency: navigator.hardwareConcurrency,
                        deviceMemory: navigator.deviceMemory
                    })
                """)

                print(f"Platform: {nav_info.get('platform')}")
                print(f"Language: {nav_info.get('language')}")
                print(f"CPU Cores: {nav_info.get('hardwareConcurrency')}")
                print(f"Device Memory: {nav_info.get('deviceMemory')} GB")

                await browser.close()

        # Clean up session
        agent_bay.delete(session)

if __name__ == "__main__":
    asyncio.run(random_fingerprint_example())
```

#### TypeScript Example

```typescript
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, BrowserFingerprint } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

async function randomFingerprintExample(): Promise<void> {
    // Get API key from environment variable
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
        console.log("Error: AGENTBAY_API_KEY environment variable not set");
        return;
    }

    try {
        // Initialize AgentBay client
        console.log("Initializing AgentBay client...");
        const agentBay = new AgentBay({ apiKey });

        // Create session
        console.log("Creating a new session...");
        const params: CreateSessionParams = {
            imageId: "browser_latest"
        };
        const sessionResult = await agentBay.create(params);

        if (!sessionResult.success) {
            console.log("Failed to create session");
            return;
        }

        const session = sessionResult.session;
        console.log(`Session created with ID: ${session.sessionId}`);

        // Configure random fingerprint
        const browserFingerprint: BrowserFingerprint = {
            devices: ["desktop"],
            operatingSystems: ["windows"],
            locales: ["zh-CN", "zh"]
        };

        // Enable stealth mode with random fingerprint
        const browserOption: BrowserOption = {
            useStealth: true,
            fingerprint: browserFingerprint
        };

        // Initialize browser
        const initialized = await session.browser.initializeAsync(browserOption);
        if (!initialized) {
            console.log("Failed to initialize browser");
            return;
        }

        const endpointUrl = await session.browser.getEndpointUrl();
        console.log("endpoint_url =", endpointUrl);

        // Connect using Playwright
        const browser = await chromium.connectOverCDP(endpointUrl);
        const context = browser.contexts()[0];
        const page = await context.newPage();

        // Test fingerprint
        console.log("\n--- Check User Agent ---");
        await page.goto("https://httpbin.org/user-agent");
        const response = await page.evaluate(() => JSON.parse(document.body.textContent));
        const userAgent = response["user-agent"] || "";
        console.log(`User Agent: ${userAgent}`);

        // Check navigator properties
        console.log("\n--- Check Navigator Properties ---");
        const navInfo = await page.evaluate(() => ({
            platform: navigator.platform,
            language: navigator.language,
            languages: navigator.languages,
            webdriver: navigator.webdriver
        }));

        console.log(`Platform: ${navInfo.platform}`);
        console.log(`Language: ${navInfo.language}`);
        console.log(`Languages: ${navInfo.languages}`);
        console.log(`WebDriver: ${navInfo.webdriver}`);

        await page.waitForTimeout(3000);
        await browser.close();

        // Clean up session
        await agentBay.delete(session);
        console.log("Session cleaned up successfully");

    } catch (error) {
        console.error("Error in main function:", error);
    }
}

randomFingerprintExample().catch(console.error);
```

### 1.2 Local Browser Fingerprint Sync

Capture fingerprint characteristics from your local Chrome browser and apply them to remote sessions for consistent behavior.

#### Features
- Extract fingerprint from local Chrome installation
- Preserve exact browser characteristics
- Maintain consistency between local and remote environments
- Support for both headless and visible mode extraction

#### Python Example

```python
import os
import asyncio
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption
from agentbay.browser.fingerprint import BrowserFingerprintGenerator
from playwright.async_api import async_playwright

async def local_sync_fingerprint_example():
    # Initialize AgentBay client
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)

    # Create session
    params = CreateSessionParams(image_id="browser_latest")
    session_result = agent_bay.create(params)

    if session_result.success:
        session = session_result.session

        # Generate fingerprint from local Chrome browser
        print("Extracting fingerprint from local Chrome browser...")
        fingerprint_generator = BrowserFingerprintGenerator(headless=False)
        fingerprint_format = await fingerprint_generator.generate_fingerprint()

        if not fingerprint_format:
            print("Failed to generate local fingerprint")
            return

        print("Local fingerprint extracted successfully")

        # Apply local fingerprint to remote browser
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_format=fingerprint_format
        )

        # Initialize browser
        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()

            # Connect using Playwright
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()

                # Verify fingerprint sync
                await page.goto("https://httpbin.org/user-agent")
                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                remote_ua = response.get('user-agent')
                local_ua = fingerprint_format.fingerprint.navigator.userAgent

                print(f"Local User Agent: {local_ua}")
                print(f"Remote User Agent: {remote_ua}")
                print(f"Fingerprint Sync: {'✓ Success' if remote_ua == local_ua else '✗ Failed'}")

                await browser.close()

        # Clean up session
        agent_bay.delete(session)

if __name__ == "__main__":
    asyncio.run(local_sync_fingerprint_example())
```

#### TypeScript Example

```typescript
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, BrowserFingerprintGenerator } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

async function localSyncFingerprintExample(): Promise<void> {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
        console.log("Error: AGENTBAY_API_KEY environment variable not set");
        return;
    }

    try {
        // Initialize AgentBay client
        console.log("Initializing AgentBay client...");
        const agentBay = new AgentBay({ apiKey });

        // Create session
        console.log("Creating a new session...");
        const params: CreateSessionParams = {
            imageId: "browser_latest"
        };
        const sessionResult = await agentBay.create(params);

        if (!sessionResult.success) {
            console.log("Failed to create session");
            return;
        }

        const session = sessionResult.session;
        console.log(`Session created with ID: ${session.sessionId}`);

        // Generate fingerprint from local Chrome browser
        console.log("Starting fingerprint generation");
        console.log("Extracting comprehensive browser fingerprint...");
        const fingerprintGenerator = new BrowserFingerprintGenerator();
        const fingerprintFormat = await fingerprintGenerator.generateFingerprint();

        if (!fingerprintFormat) {
            console.log("Failed to generate local fingerprint");
            return;
        }

        console.log("Fingerprint generation completed successfully!");
        console.log(`Fingerprint format: ${JSON.stringify(fingerprintFormat)}`);

        // Apply local fingerprint to remote browser
        const browserOption: BrowserOption = {
            useStealth: true,
            fingerprintFormat: fingerprintFormat
        };

        // Initialize browser
        const initialized = await session.browser.initializeAsync(browserOption);
        if (!initialized) {
            console.log("Failed to initialize browser");
            return;
        }

        const endpointUrl = await session.browser.getEndpointUrl();
        console.log("endpoint_url =", endpointUrl);

        // Connect using Playwright
        const browser = await chromium.connectOverCDP(endpointUrl);
        const context = browser.contexts()[0];
        const page = await context.newPage();

        // Verify fingerprint sync
        console.log("\n--- Check User Agent ---");
        await page.goto("https://httpbin.org/user-agent");
        const response = await page.evaluate(() => JSON.parse(document.body.textContent));
        const userAgent = response["user-agent"] || "";
        console.log(`User Agent: ${userAgent}`);

        console.log("Please check if User Agent is synced correctly by visiting https://httpbin.org/user-agent in local chrome browser.");

        await page.waitForTimeout(3000);
        await browser.close();

        // Clean up session
        await agentBay.delete(session);
        console.log("Session cleaned up successfully");

    } catch (error) {
        console.error("Error in main function:", error);
    }
}

localSyncFingerprintExample().catch(console.error);
```

### 1.3 Custom Fingerprint Construction

Load and apply custom fingerprint data from JSON files or construct fingerprints programmatically.

#### Features
- Load fingerprint from JSON files
- Construct fingerprints programmatically
- Full control over all fingerprint characteristics
- Reusable fingerprint configurations

#### Python Example

```python
import os
import asyncio
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from agentbay.browser.browser import BrowserOption
from agentbay.browser.fingerprint import FingerprintFormat
from playwright.async_api import async_playwright

async def custom_fingerprint_example():
    # Initialize AgentBay client
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)

    # Create session
    params = CreateSessionParams(image_id="browser_latest")
    session_result = agent_bay.create(params)

    if session_result.success:
        session = session_result.session

        # Load fingerprint from JSON file
        fingerprint_file = "path/to/custom_fingerprint.json"
        try:
            with open(fingerprint_file, "r") as f:
                fingerprint_format = FingerprintFormat.from_json(f.read())
            print("Custom fingerprint loaded from file")
        except FileNotFoundError:
            # Fallback: Use example fingerprint data
            print("Using example fingerprint data")
            # You can also construct fingerprint programmatically here
            # For demonstration, we'll use a simple approach
            return

        # Apply custom fingerprint to browser
        browser_option = BrowserOption(
            use_stealth=True,
            fingerprint_format=fingerprint_format
        )

        # Initialize browser
        if await session.browser.initialize_async(browser_option):
            endpoint_url = session.browser.get_endpoint_url()

            # Connect using Playwright
            async with async_playwright() as p:
                browser = await p.chromium.connect_over_cdp(endpoint_url)
                context = browser.contexts[0]
                page = await context.new_page()

                # Verify custom fingerprint
                await page.goto("https://httpbin.org/user-agent")
                response = await page.evaluate("() => JSON.parse(document.body.textContent)")
                remote_ua = response.get('user-agent')
                expected_ua = fingerprint_format.fingerprint.navigator.userAgent

                print(f"Expected User Agent: {expected_ua}")
                print(f"Remote User Agent: {remote_ua}")
                print(f"Custom Fingerprint: {'✓ Applied' if remote_ua == expected_ua else '✗ Failed'}")

                # Test additional properties
                screen_info = await page.evaluate("""
                    () => ({
                        width: screen.width,
                        height: screen.height,
                        colorDepth: screen.colorDepth,
                        pixelDepth: screen.pixelDepth
                    })
                """)

                print(f"Screen Resolution: {screen_info.get('width')}x{screen_info.get('height')}")
                print(f"Color Depth: {screen_info.get('colorDepth')}")

                await browser.close()

        # Clean up session
        agent_bay.delete(session)

if __name__ == "__main__":
    asyncio.run(custom_fingerprint_example())
```

#### TypeScript Example

```typescript
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, FingerprintFormat } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';
import * as fs from 'fs';
import * as path from 'path';

async function generateFingerprintByFile(): Promise<FingerprintFormat> {
    /**
     * Generate fingerprint by file.
     */
    const fingerprintPath = path.join(__dirname, "../../../../../resource/fingerprint.example.json");
    const fingerprintData = fs.readFileSync(fingerprintPath, 'utf8');
    return FingerprintFormat.fromJson(fingerprintData);
}

async function customFingerprintExample(): Promise<void> {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
        console.log("Error: AGENTBAY_API_KEY environment variable not set");
        return;
    }

    try {
        // Initialize AgentBay client
        console.log("Initializing AgentBay client...");
        const agentBay = new AgentBay({ apiKey });

        // Create session
        console.log("Creating a new session...");
        const params: CreateSessionParams = {
            imageId: "browser_latest"
        };
        const sessionResult = await agentBay.create(params);

        if (!sessionResult.success) {
            console.log("Failed to create session");
            return;
        }

        const session = sessionResult.session;
        console.log(`Session created with ID: ${session.sessionId}`);

        // You can generate fingerprint by file or construct FingerprintFormat by yourself totally.
        const fingerprintFormat = await generateFingerprintByFile();

        // Apply custom fingerprint to browser
        const browserOption: BrowserOption = {
            useStealth: true,
            fingerprintFormat: fingerprintFormat
        };

        // Initialize browser
        const initialized = await session.browser.initializeAsync(browserOption);
        if (!initialized) {
            console.log("Failed to initialize browser");
            return;
        }

        const endpointUrl = await session.browser.getEndpointUrl();
        console.log("endpoint_url =", endpointUrl);

        // Connect using Playwright
        const browser = await chromium.connectOverCDP(endpointUrl);
        const context = browser.contexts()[0];
        const page = await context.newPage();

        // Verify custom fingerprint
        console.log("\n--- Check User Agent ---");
        await page.goto("https://httpbin.org/user-agent");
        const response = await page.evaluate(() => JSON.parse(document.body.textContent));
        const userAgent = response["user-agent"] || "";
        console.log(`User Agent: ${userAgent}`);

        // Verify that the user agent matches the fingerprint format
        if (fingerprintFormat.fingerprint?.navigator?.userAgent) {
            if (userAgent === fingerprintFormat.fingerprint.navigator.userAgent) {
                console.log("User Agent constructed correctly");
            } else {
                console.log("User Agent mismatch");
            }
        }

        await page.waitForTimeout(3000);
        await browser.close();

        // Clean up session
        await agentBay.delete(session);
        console.log("Session cleaned up successfully");

    } catch (error) {
        console.error("Error in main function:", error);
    }
}

customFingerprintExample().catch(console.error);
```

## 2. Fingerprint Persistence

Fingerprint persistence allows you to maintain consistent browser characteristics across multiple sessions by using browser contexts and fingerprint contexts.

### Features
- Persistent fingerprint storage across sessions
- Context-based fingerprint management
- Support for all fingerprint generation methods
- Automatic fingerprint loading and saving

### How It Works

1. **First Session**: Generate or apply a fingerprint with `fingerprint_persistent=True`
2. **Context Sync**: Save the session with `sync_context=True` to persist the fingerprint
3. **Subsequent Sessions**: Create new sessions with the same contexts to reuse the fingerprint

### Python Example (Random Fingerprint Persistence)

```python
import os
import time
import asyncio
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams, BrowserContext
from agentbay.browser.browser import BrowserOption, BrowserFingerprint, BrowserFingerprintContext
from playwright.async_api import async_playwright

async def fingerprint_persistence_example():
    # Initialize AgentBay client
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)

    # Create browser context for persistence
    browser_context_name = f"persistent-browser-{int(time.time())}"
    browser_context_result = agent_bay.context.get(browser_context_name, create_if_not_exists=True)
    browser_context = BrowserContext(browser_context_result.context.id, auto_upload=True)

    # Create fingerprint context for persistence
    fingerprint_context_name = f"persistent-fingerprint-{int(time.time())}"
    fingerprint_context_result = agent_bay.context.get(fingerprint_context_name, create_if_not_exists=True)
    fingerprint_context = BrowserFingerprintContext(fingerprint_context_result.context.id)
    browser_context.fingerprint_context = fingerprint_context

    print(f"Created contexts - Browser: {browser_context.context_id}, Fingerprint: {fingerprint_context.fingerprint_context_id}")

    # === FIRST SESSION: Generate and persist fingerprint ===
    print("\n=== First Session: Generating and persisting fingerprint ===")

    params1 = CreateSessionParams(
        image_id="browser_latest",
        browser_context=browser_context
    )
    session1_result = agent_bay.create(params1)

    if session1_result.success:
        session1 = session1_result.session
        print(f"First session created: {session1.session_id}")

        # Configure random fingerprint with persistence
        browser_option1 = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True,  # Enable persistence
            fingerprint=BrowserFingerprint(
                devices=["desktop"],
                operating_systems=["windows"],
                locales=["en-US"]
            )
        )

        # Initialize browser and capture fingerprint
        if await session1.browser.initialize_async(browser_option1):
            endpoint_url1 = session1.browser.get_endpoint_url()

            async with async_playwright() as p:
                browser1 = await p.chromium.connect_over_cdp(endpoint_url1)
                context1 = browser1.contexts[0]
                page1 = await context1.new_page()

                # Capture first session fingerprint
                await page1.goto("https://httpbin.org/user-agent")
                response1 = await page1.evaluate("() => JSON.parse(document.body.textContent)")
                first_user_agent = response1.get('user-agent')
                print(f"First session User Agent: {first_user_agent}")

                await browser1.close()

        # Delete session with context sync to save fingerprint
        agent_bay.delete(session1, sync_context=True)
        print("First session deleted with fingerprint saved to context")

    # Wait for context sync to complete
    await asyncio.sleep(3)

    # === SECOND SESSION: Reuse persisted fingerprint ===
    print("\n=== Second Session: Reusing persisted fingerprint ===")

    params2 = CreateSessionParams(
        image_id="browser_latest",
        browser_context=browser_context  # Same context
    )
    session2_result = agent_bay.create(params2)

    if session2_result.success:
        session2 = session2_result.session
        print(f"Second session created: {session2.session_id}")

        # Configure browser to load persisted fingerprint
        browser_option2 = BrowserOption(
            use_stealth=True,
            fingerprint_persistent=True  # Will load saved fingerprint
            # No fingerprint parameter - will use persisted one
        )

        # Initialize browser with persisted fingerprint
        if await session2.browser.initialize_async(browser_option2):
            endpoint_url2 = session2.browser.get_endpoint_url()

            async with async_playwright() as p:
                browser2 = await p.chromium.connect_over_cdp(endpoint_url2)
                context2 = browser2.contexts[0]
                page2 = await context2.new_page()

                # Verify fingerprint persistence
                await page2.goto("https://httpbin.org/user-agent")
                response2 = await page2.evaluate("() => JSON.parse(document.body.textContent)")
                second_user_agent = response2.get('user-agent')
                print(f"Second session User Agent: {second_user_agent}")

                # Check if fingerprints match
                fingerprint_persisted = first_user_agent == second_user_agent
                print(f"Fingerprint Persistence: {'✓ Success' if fingerprint_persisted else '✗ Failed'}")

                if fingerprint_persisted:
                    print("🎉 Fingerprint successfully persisted across sessions!")

                await browser2.close()

        # Clean up second session
        agent_bay.delete(session2, sync_context=True)
        print("Second session deleted")

    # Clean up contexts
    try:
        agent_bay.context.delete(browser_context_result.context)
        agent_bay.context.delete(fingerprint_context_result.context)
        print("Contexts cleaned up")
    except Exception as e:
        print(f"Context cleanup warning: {e}")

if __name__ == "__main__":
    asyncio.run(fingerprint_persistence_example())
```

### TypeScript Example (Random Fingerprint Persistence)

```typescript
import { AgentBay, CreateSessionParams } from 'wuying-agentbay-sdk';
import { BrowserOption, BrowserFingerprint, BrowserContext, BrowserFingerprintContext } from 'wuying-agentbay-sdk';
import { chromium } from 'playwright';

// Global variables for persistent context and fingerprint context
let persistentContext: any = null;
let persistentFingerprintContext: any = null;

function getTestApiKey(): string {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
        throw new Error("AGENTBAY_API_KEY environment variable not set");
    }
    return apiKey;
}

function isWindowsUserAgent(userAgent: string): boolean {
    if (!userAgent) {
        return false;
    }
    const userAgentLower = userAgent.toLowerCase();
    const windowsIndicators = [
        'windows nt',
        'win32',
        'win64',
        'windows',
        'wow64'
    ];
    return windowsIndicators.some(indicator => userAgentLower.includes(indicator));
}

async function runAsFirstTime(): Promise<void> {
    console.log("====================");
    console.log("Run as first time");
    console.log("====================");

    const apiKey = getTestApiKey();
    const agentBay = new AgentBay({ apiKey });

    // Create a browser context for first time
    const sessionContextName = `test-browser-context-${Date.now()}`;
    const contextResult = await agentBay.context.get(sessionContextName, true);
    if (!contextResult.success || !contextResult.context) {
        console.log("Failed to create browser context");
        return;
    }

    persistentContext = contextResult.context;
    console.log(`Created browser context: ${persistentContext.name} (ID: ${persistentContext.id})`);

    // Create a browser fingerprint context for first time
    const fingerprintContextName = `test-browser-fingerprint-${Date.now()}`;
    const fingerprintContextResult = await agentBay.context.get(fingerprintContextName, true);
    if (!fingerprintContextResult.success || !fingerprintContextResult.context) {
        console.log("Failed to create fingerprint context");
        return;
    }

    persistentFingerprintContext = fingerprintContextResult.context;
    console.log(`Created fingerprint context: ${persistentFingerprintContext.name} (ID: ${persistentFingerprintContext.id})`);

    // Create session with BrowserContext and FingerprintContext
    console.log(`Creating session with browser context ID: ${persistentContext.id} ` +
                `and fingerprint context ID: ${persistentFingerprintContext.id}`);

    const fingerprintContext = new BrowserFingerprintContext(persistentFingerprintContext.id);
    const browserContext = new BrowserContext(persistentContext.id, true, undefined, fingerprintContext);

    const params = new CreateSessionParams()
        .withImageId("browser_latest")
        .withBrowserContext(browserContext);

    const sessionResult = await agentBay.create(params);
    if (!sessionResult.success || !sessionResult.session) {
        console.log(`Failed to create first session: ${sessionResult.errorMessage}`);
        return;
    }

    const session = sessionResult.session;
    console.log(`First session created with ID: ${session.sessionId}`);

    // Initialize browser with fingerprint persistent enabled and set fingerprint generation options
    const browserOption: BrowserOption = {
        useStealth: true,
        fingerprintPersistent: true,
        fingerprint: {
            devices: ["desktop"],
            operatingSystems: ["windows"],
            locales: ["zh-CN"]
        } as BrowserFingerprint
    };

    const initSuccess = await session.browser.initializeAsync(browserOption);
    if (!initSuccess) {
        console.log("Failed to initialize browser");
        return;
    }
    console.log("First session browser initialized successfully");

    // Get endpoint URL and test fingerprint
    const endpointUrl = await session.browser.getEndpointUrl();
    if (!endpointUrl) {
        console.log("Failed to get browser endpoint URL");
        return;
    }
    console.log(`First session browser endpoint URL: ${endpointUrl}`);

    // Connect with playwright, test first session fingerprint
    console.log("Opening https://httpbin.org/user-agent and test user agent...");
    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts().length > 0 ? browser.contexts()[0] : await browser.newContext();

    const page = await context.newPage();
    await page.goto("https://httpbin.org/user-agent", { timeout: 60000 });
    const response = await page.evaluate(() => JSON.parse(document.body.textContent));
    const userAgent = response["user-agent"];
    console.log("user_agent =", userAgent);

    const isWindows = isWindowsUserAgent(userAgent);
    if (!isWindows) {
        console.log("Failed to get windows user agent");
        return;
    }

    await context.close();
    console.log("First session browser fingerprint check completed");

    // Delete first session with syncContext=true
    console.log("Deleting first session with syncContext=true...");
    const deleteResult = await agentBay.delete(session, { syncContext: true });
    console.log(`First session deleted successfully (RequestID: ${deleteResult.requestId})`);
}

async function runAsSecondTime(): Promise<void> {
    console.log("====================");
    console.log("Run as second time");
    console.log("====================");

    const apiKey = getTestApiKey();
    const agentBay = new AgentBay({ apiKey });

    // Create second session with same browser context and fingerprint context
    console.log(`Creating second session with same browser context ID: ${persistentContext.id} ` +
                `and fingerprint context ID: ${persistentFingerprintContext.id}`);

    const fingerprintContext = new BrowserFingerprintContext(persistentFingerprintContext.id);
    const browserContext = new BrowserContext(persistentContext.id, true, undefined, fingerprintContext);

    const params = new CreateSessionParams()
        .withImageId("browser_latest")
        .withBrowserContext(browserContext);

    const sessionResult = await agentBay.create(params);
    if (!sessionResult.success || !sessionResult.session) {
        console.log(`Failed to create second session: ${sessionResult.errorMessage}`);
        return;
    }

    const session = sessionResult.session;
    console.log(`Second session created with ID: ${session.sessionId}`);

    // Initialize browser with fingerprint persistent enabled but not specific fingerprint generation options
    const browserOption: BrowserOption = {
        useStealth: true,
        fingerprintPersistent: true
    };

    const initSuccess = await session.browser.initializeAsync(browserOption);
    if (!initSuccess) {
        console.log("Failed to initialize browser in second session");
        return;
    }
    console.log("Second session browser initialized successfully");

    // Get endpoint URL and test fingerprint persistence
    const endpointUrl = await session.browser.getEndpointUrl();
    if (!endpointUrl) {
        console.log("Failed to get browser endpoint URL in second session");
        return;
    }
    console.log(`Second session browser endpoint URL: ${endpointUrl}`);

    // Connect with playwright and test second session fingerprint
    const browser = await chromium.connectOverCDP(endpointUrl);
    const context = browser.contexts().length > 0 ? browser.contexts()[0] : await browser.newContext();
    const page = await context.newPage();
    await page.goto("https://httpbin.org/user-agent", { timeout: 60000 });
    const response = await page.evaluate(() => JSON.parse(document.body.textContent));
    const userAgent = response["user-agent"];
    console.log("user_agent =", userAgent);

    const isWindows = isWindowsUserAgent(userAgent);
    if (!isWindows) {
        console.log("Failed to get windows user agent in second session");
        return;
    }
    console.log("SUCCESS: fingerprint persisted correctly!");

    await context.close();
    console.log("Second session browser fingerprint check completed");

    // Delete second session with syncContext=true
    console.log("Deleting second session with syncContext=true...");
    const deleteResult = await agentBay.delete(session, { syncContext: true });
    console.log(`Second session deleted successfully (RequestID: ${deleteResult.requestId})`);
}

async function fingerprintPersistenceExample(): Promise<void> {
    /**
     * Test browser fingerprint persist across sessions with the same browser and fingerprint context.
     */
    try {
        await runAsFirstTime();
        await new Promise(resolve => setTimeout(resolve, 3000)); // Wait 3 seconds
        await runAsSecondTime();
    } catch (error) {
        console.error("Error in main function:", error);
    }
}

fingerprintPersistenceExample().catch(console.error);
```

### Persistence with Other Fingerprint Types

The fingerprint persistence feature works with all three generation methods:

#### Local Sync Persistence
```python
# First session: Generate from local browser and persist
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=local_fingerprint_format  # From BrowserFingerprintGenerator
)
```

#### Custom Fingerprint Persistence
```python
# First session: Load custom fingerprint and persist
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=custom_fingerprint_format  # From JSON file or constructed
)
```

## Best Practices

### 1. Browser Context Usage

**💡 Important**: Always use the pre-created browser context provided by AgentBay SDK.

```python
# ✅ Correct - Use the existing context
browser = await p.chromium.connect_over_cdp(endpoint_url)
context = browser.contexts[0]  # Use the default context
page = await context.new_page()
```

```python
# ❌ Incorrect - Creating new context breaks stealth features
browser = await p.chromium.connect_over_cdp(endpoint_url)
context = await browser.new_context()  # Don't do this
page = await context.new_page()
```

### 2. Important Notice

All fingerprint generation methods require `use_stealth=True` configuration, otherwise fingerprint settings will not take effect. This is because fingerprint functionality depends on stealth mode to properly apply browser feature masking.

```python
# ✅ Correct - Always enable stealth mode for fingerprints
browser_option = BrowserOption(
    use_stealth=True,  # Required for fingerprint to work
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)

session = await agentbay.start_browser_session(
    browser_option=browser_option
)
```

```python
# ❌ Incorrect - Missing use_stealth=True
browser_option = BrowserOption(
    # use_stealth=True is missing!
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)
# Fingerprint configuration will be ignored
```

### 3. Fingerprint Generation Strategy

#### Parameter Priority
When multiple fingerprint parameters are provided, the priority is:
1. `fingerprint_format` (customized generation)
2. `fingerprint` (random generation)

```python
# ✅ Correct - Use fingerprint_format for specific fingerprints
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_format=my_fingerprint_format
    # fingerprint parameter will be ignored
)
```

```python
# ❌ Avoid - user_agent disables fingerprint features
browser_option = BrowserOption(
    use_stealth=True,
    user_agent="Custom User Agent",
    fingerprint=BrowserFingerprint(...)  # Will be ignored
)
```

### 4. Fingerprint Persistence Behavior

When fingerprint persistence is enabled (`fingerprint_persistent=True`), the system behaves differently based on the fingerprint configuration type:

#### Using `fingerprint` Parameter
When configured with the `fingerprint` parameter, the system will **prioritize persisted fingerprints** over generating new random ones:

```python
# First run - generates and persists a random fingerprint
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint=BrowserFingerprint(
        devices=["desktop"],
        operating_systems=["windows"],
        locales=["en-US"]
    )
)

# Subsequent runs - uses the same persisted fingerprint
# The fingerprint parameter serves as a template but won't generate new random values
```

#### Using `fingerprint_format` Parameter
When configured with the `fingerprint_format` parameter, the system will **override existing persisted fingerprints** because the user has explicitly configured the fingerprint parameters :

```python
# This will replace any existing persisted fingerprint
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=custom_fingerprint_format  # Overrides persisted data
)
```

#### Behavior Summary

| Configuration Type | Persistence Behavior |
|-------------------|---------------------|
| `fingerprint` | Uses persisted fingerprint if exists, otherwise generates and persists new random fingerprint |
| `fingerprint_format` | Always uses provided fingerprint and overwrites any existing persisted data |

```python
# ✅ Correct - Consistent fingerprint across sessions
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint=BrowserFingerprint(devices=["desktop"])
)
# Will use the same fingerprint in all sessions

# ✅ Correct - Force update persisted fingerprint
browser_option = BrowserOption(
    use_stealth=True,
    fingerprint_persistent=True,
    fingerprint_format=new_fingerprint_data
)
# Will replace existing fingerprint with new data
```

### 5. Device and OS Compatibility

Ensure device types match operating systems:

```python
# ✅ Correct configurations
desktop_fingerprint = BrowserFingerprint(
    devices=["desktop"],
    operating_systems=["windows", "macos", "linux"]
)

mobile_fingerprint = BrowserFingerprint(
    devices=["mobile"],
    operating_systems=["android", "ios"]
)
```

```python
# ❌ Incorrect - mismatched device and OS
wrong_fingerprint = BrowserFingerprint(
    devices=["desktop"],
    operating_systems=["android", "ios"]  # Mobile OS with desktop device
)
```

### 6. Context Management for Persistence

- Create unique context names to avoid conflicts
- Use `sync_context=True` when deleting sessions to save fingerprints
- Clean up contexts after use to prevent resource leaks
- Wait for context sync to complete before creating new sessions

## Troubleshooting

### Common Issues

1. **Fingerprint Not Persisting**
   - Ensure `fingerprint_persistent=True` is set
   - Verify browser and fingerprint contexts are properly configured
   - Use `sync_context=True` when deleting sessions
   - Wait for context sync to complete

2. **Local Fingerprint Generation Fails**
   - Check if Chrome is installed and accessible
   - Try running with `headless=False` for debugging
   - Ensure sufficient permissions for browser automation

3. **Custom Fingerprint Loading Errors**
   - Verify JSON file format matches FingerprintFormat schema
   - Check file permissions and path accessibility
   - Validate fingerprint data completeness

## 📚 Related Guides

- [Browser Proxies](browser-proxies.md) - IP rotation and proxy configuration
- [CAPTCHA Resolution](captcha.md) - Automatic CAPTCHA handling
- [Browser Context](browser-context.md) - Cookie and session management
- [Browser Use Overview](../README.md) - Complete browser automation features

## 🆘 Getting Help

- [GitHub Issues](https://github.com/aliyun/wuying-agentbay-sdk/issues)
- [Documentation Home](../../README.md)