```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
   █                                                                        █
   █     JACKSNXLY                                                          █
   █     Systems Engineering · AI/ML · Quantitative Trading                 █
   █                                                                        █
   ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

I build **production systems** where performance matters—high-throughput Rust services, ML pipelines, and real-time data infrastructure. Polyglot by necessity: Rust for speed, Python for ML, TypeScript for interfaces.

<br/>

## Core Expertise

<table>
<tr>
<td width="50%" valign="top">

### High-Performance Backend
Rust microservices with **Axum**, **Actix-Web**, and **Tokio**. gRPC services via **Tonic**. Async-first architecture with connection pooling, circuit breakers, and comprehensive observability (Prometheus, ELK, structured logging).

</td>
<td width="50%" valign="top">

### ML Systems & AI Integration
Production ML pipelines with **scikit-learn**, **XGBoost**, and **Random Forest** models. Vector embeddings with **Qdrant**. RAG systems with LLM integration. Image generation with **SDXL + ControlNet**.

</td>
</tr>
<tr>
<td width="50%" valign="top">

### Real-Time Data Infrastructure
WebSocket servers handling 1000+ concurrent connections. Message-driven architectures with **RabbitMQ**. Stream processing for market data. **TimescaleDB** for time-series at scale.

</td>
<td width="50%" valign="top">

### Quantitative Trading Systems
Multi-strategy platforms with DBSCAN clustering for liquidation detection. Technical indicators (RSI, MACD, Bollinger Bands). ML-enhanced signal filtering. Backtesting engines with walk-forward validation.

</td>
</tr>
</table>

<br/>

## Selected Projects

### Athenum
**Multi-strategy cryptocurrency trading platform**

Production monorepo with 8 trading products and a real-time analytics platform. Rust microservices ingest data from 4 exchanges via WebSocket, Python ML models generate signals.

```
ANALYTICS PLATFORM (Rust)
├── whale-wall-tracker     Real-time large order detection across Binance, Hyperliquid, Coinbase
├── liquidation-analyzer   DBSCAN clustering for liquidation level detection
├── orderbook-archiver     5-minute snapshots with TimescaleDB hypertables
├── market-aggregator      Multi-exchange price/volume aggregation
└── api                    Actix-web REST + WebSocket SSE, Prometheus metrics

TRADING STRATEGIES (Python)
├── Smart Money            Order Blocks, FVG, Multi-RSI divergence, XGBoost signal filter
├── Hedge Scalping         EMA grid strategy for Hyperliquid DEX
├── HF Momentum            Multi-timeframe momentum with ATR-based position sizing
└── DEX-CEX Arbitrage      Spread monitoring between Lighter DEX and Binance
```

**Stack:** Rust (Tokio, Actix-Web, SQLx) · Python (scikit-learn, XGBoost) · TimescaleDB · RabbitMQ · Redis

---

### FastPal
**AI-powered sales intelligence platform**

Two-product monorepo: real-time sales coaching and B2B lead generation.

**Copilot** — Real-time AI coaching during sales calls
- WebSocket server with connection pooling (1000+ concurrent)
- Big Five personality analysis from speech patterns
- Dual-mode analysis: linguistic markers + LLM scoring
- Native macOS app with Whisper.cpp transcription (Swift/SwiftUI)

**Leads** — B2B lead generation and enrichment
- gRPC maps scraper with 3-month TTL caching (60%+ hit rate)
- Google Vertex AI for company data enrichment
- Distributed pipeline: scrape → enrich → sync with deduplication

**Stack:** Rust (Axum, Tonic gRPC) · Python (Vertex AI) · Swift/SwiftUI · Next.js · Supabase

---

### Typelense
**AI fashion photography platform**

Virtual try-on and image enhancement using diffusion models.

- **SDXL + Tile ControlNet** pipeline for 2048px+ upscaling
- Tiled processing (1024px tiles, 256px overlap) with Gaussian blending
- Quality validation: SSIM >0.85, Delta E <5.0, sharpness metrics
- Auto-device detection (CUDA/MPS/CPU) with VRAM optimization

**Stack:** Rust (Axum) · Python (Diffusers, FastAPI) · React · Cloudflare R2

---

### InnoCom
**Multi-tenant innovation platform**

Connects companies, universities, and students through challenges and AI-powered matching.

- **Co-founder matching engine** — Random Forest + vector embeddings (Sentence Transformers) + Qdrant
- **RAG coaching system** — Document ingestion, chunking, OpenAI integration
- **Real-time gateway** — Rust WebSocket server for messaging and presence
- **Event platform** — Offline-capable check-in, live networking

**Stack:** Rust (Axum, Tonic) · Python (FastAPI, gRPC) · Next.js 15 · PostgreSQL · Qdrant · Redis

---

### Open Source

| Project | Description |
|---------|-------------|
| **[claude-issue-toolkit](https://github.com/jacksnxly/claude-issue-toolkit)** | Full issue lifecycle plugin for Claude Code — create, validate, solve end-to-end |
| **[keryx](https://github.com/jacksnxly/keryx)** | AI release notes generator from PRs and conventional commits (Rust CLI) |

<br/>

## Stack

```
SYSTEMS           Rust · Tokio · Axum · Actix-Web · Tonic (gRPC) · SQLx
ML/AI             Python · scikit-learn · XGBoost · Diffusers · LangChain · OpenAI
DATA              PostgreSQL · TimescaleDB · Redis · RabbitMQ · Qdrant
FRONTEND          TypeScript · Next.js · React · Tailwind
INFRASTRUCTURE    Docker · AWS · Supabase · Cloudflare R2 · Prometheus · ELK
```

<br/>

---

<div align="center">

<br/>

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=jacksnxly&show_icons=true&hide_border=true&bg_color=00000000&title_color=888888&text_color=666666&icon_color=888888)

<br/>

**Building systems where milliseconds matter.**

[![GitHub](https://img.shields.io/badge/GitHub-444444?style=flat-square&logo=github&logoColor=white)](https://github.com/jacksnxly)

</div>
