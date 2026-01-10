# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Antigravity Tools is a Tauri v2 desktop application for AI account management and API proxying. It converts Google/Anthropic web sessions into standardized API endpoints (OpenAI, Anthropic, Gemini formats), enabling local AI gateway functionality with multi-account rotation and intelligent request dispatching.

## Development Commands

```bash
# Development
npm run dev          # Start Vite dev server (frontend only)
npm run tauri dev    # Start full Tauri app in dev mode (frontend + Rust backend)

# Build
npm run build        # Build frontend (TypeScript + Vite)
npm run tauri build  # Build complete application for release

# Rust-specific (run from src-tauri/)
cargo build          # Build Rust backend
cargo test           # Run all Rust tests
cargo test <test_name>                    # Run a specific test by name
cargo test comprehensive -- --nocapture   # Run proxy tests with output

# Web Server Mode (headless, for Linux servers)
cd src-tauri
cargo build --release --bin antigravity-server --no-default-features --features web-server
./target/release/antigravity-server --port 8765 --static-dir ../dist --data-dir ~/.antigravity
```

## Architecture

### Tech Stack
- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS + DaisyUI
- **Backend**: Rust + Tauri v2 + Axum (HTTP server)
- **State**: Zustand (frontend), DashMap/RwLock (backend)
- **i18n**: i18next with zh/en locales

### Directory Structure

```
src/                    # React frontend
├── pages/              # Main views (Dashboard, Accounts, ApiProxy, Settings, Monitor)
├── components/         # UI components by feature
├── stores/             # Zustand stores (useAccountStore, useConfigStore)
├── services/           # Tauri IPC wrappers (invoke calls)
├── types/              # TypeScript interfaces
└── locales/            # i18n translations (en.json, zh.json)

src-tauri/src/          # Rust backend
├── lib.rs              # Tauri app setup, plugin registration, command handlers
├── commands/           # Tauri commands exposed to frontend
│   ├── mod.rs          # Account management commands
│   └── proxy.rs        # Proxy service control commands
├── modules/            # Core business logic
│   ├── account.rs      # Account CRUD, file-based storage
│   ├── oauth.rs        # Google OAuth token management
│   ├── quota.rs        # Quota fetching from upstream
│   └── tray.rs         # System tray menu
├── models/             # Data structures (Account, TokenData, QuotaData, AppConfig)
└── proxy/              # API proxy server (Axum-based)
    ├── server.rs       # Axum server setup, AppState
    ├── token_manager.rs # Account pool, rotation, rate limiting
    ├── handlers/       # Protocol-specific request handlers
    │   ├── claude.rs   # /v1/messages endpoint
    │   ├── openai.rs   # /v1/chat/completions endpoint
    │   └── gemini.rs   # Gemini API endpoints
    └── mappers/        # Request/response protocol converters
        ├── claude/     # Claude protocol mapping (request.rs, response.rs, streaming.rs)
        ├── openai/     # OpenAI protocol mapping
        └── gemini/     # Gemini protocol mapping
```

### Key Architectural Patterns

**Request Flow**: Client → Axum Handler → Middleware (auth/logging) → Model Router → Account Dispatcher → Protocol Mapper → Upstream API → Response Mapper → Client

**Account Storage**: JSON files in `{data_dir}/accounts/*.json`, one file per account containing TokenData and QuotaData.

**Token Rotation**: `TokenManager` maintains a pool of accounts loaded from disk, handles round-robin selection, rate limit tracking, and automatic failover on 429/401 errors.

**Protocol Conversion**: Incoming requests (OpenAI/Anthropic/Gemini format) are mapped to Google's Gemini API format, then responses are mapped back to the original protocol.

**Frontend-Backend Communication**: All IPC goes through Tauri commands defined in `src-tauri/src/commands/`. Frontend services in `src/services/` wrap `invoke()` calls.

### Important Files

- `src-tauri/src/proxy/config.rs` - ProxyConfig, ZaiConfig, auth modes
- `src-tauri/src/proxy/rate_limit.rs` - Rate limiting and quota tracking
- `src-tauri/src/proxy/mappers/claude/request.rs` - Claude to Gemini request transformation
- `src-tauri/src/proxy/mappers/openai/streaming.rs` - OpenAI SSE response streaming
- `src/pages/ApiProxy.tsx` - Main proxy configuration UI (largest frontend file)

### Conventions

- Rust code uses Chinese comments for inline documentation
- All Tauri commands are registered in `lib.rs` under `invoke_handler`
- Frontend state changes trigger tray menu updates via `tray://` events
- Proxy server runs on configurable port (default 8045)
- API key format: `sk-antigravity` (or custom keys via security config)

### Feature Flags

The Rust backend supports two build modes via Cargo features:
- `tauri-app` (default): Full desktop application with Tauri GUI
- `web-server`: Headless web server mode for deployment on Linux servers without GUI

### Testing

Tests are located in `src-tauri/src/proxy/tests/`. The `comprehensive` test module contains integration tests for the proxy system. Run with `--nocapture` to see detailed output during test execution.
