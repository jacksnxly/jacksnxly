# Hi, I'm Jackson

**Germany** | **Systems Engineer** | **Quant Trading & AI/ML**

![Rust](https://img.shields.io/badge/-Rust-000000?style=flat-square&logo=rust&logoColor=white)
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/-TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Node.js](https://img.shields.io/badge/-Node.js-339933?style=flat-square&logo=node.js&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/-Redis-DC382D?style=flat-square&logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![AWS](https://img.shields.io/badge/-AWS-232F3E?style=flat-square&logo=amazon-aws&logoColor=white)
![Swift](https://img.shields.io/badge/-Swift-FA7343?style=flat-square&logo=swift&logoColor=white)
![Next.js](https://img.shields.io/badge/-Next.js-000000?style=flat-square&logo=next.js&logoColor=white)

> Building production systems where milliseconds matter — high-throughput Rust services, ML pipelines, and real-time data infrastructure.

## Current Projects

- **[Athenum](https://github.com/jacksnxly)** - Multi-strategy cryptocurrency trading platform. 8 trading products, Rust microservices ingesting from 4 exchanges, Python ML signal generation.
- **[FastPal](https://github.com/jacksnxly)** - AI-powered sales intelligence: real-time coaching during calls + B2B lead generation with gRPC scraping and Vertex AI enrichment.
- **[Typelense](https://github.com/jacksnxly)** - AI fashion photography with SDXL + ControlNet diffusion pipelines for virtual try-on and 2048px+ upscaling.
- **[InnoCom](https://github.com/jacksnxly)** - Multi-tenant innovation platform connecting companies, universities, and students with AI-powered co-founder matching and RAG coaching.

### Open Source

- **[claude-issue-toolkit](https://github.com/jacksnxly/claude-issue-toolkit)** - Full issue lifecycle plugin for Claude Code — create, validate, solve end-to-end
- **[keryx](https://github.com/jacksnxly/keryx)** - AI release notes generator from PRs and conventional commits (Rust CLI)

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

## Stack

```
SYSTEMS           Rust · Tokio · Axum · Actix-Web · Tonic (gRPC) · SQLx
ML/AI             Python · scikit-learn · XGBoost · Diffusers · LangChain · OpenAI
DATA              PostgreSQL · TimescaleDB · Redis · RabbitMQ · Qdrant
FRONTEND          TypeScript · Next.js · React · Tailwind
INFRASTRUCTURE    Docker · AWS · Supabase · Cloudflare R2 · Prometheus · ELK
```

## GitHub Activity

![GitHub Contribution Graph](https://ghchart.rshah.org/jacksnxly)

## What I'm Doing

- **Building trading infrastructure** - Rust-powered analytics and ML-enhanced signal pipelines for crypto markets
- **Shipping AI products** - From real-time sales coaching to fashion photography diffusion models
- **Open source tooling** - Developer tools for AI workflows and release automation

## Connect

[![Twitter](https://img.shields.io/badge/-@jacksnxly-1DA1F2?style=flat-square&logo=twitter&logoColor=white)](https://x.com/jacksnxly)
[![LinkedIn](https://img.shields.io/badge/-Jackson_Ly-0077B5?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/jackson-ly/)
[![Instagram](https://img.shields.io/badge/-@jacksnxly-E4405F?style=flat-square&logo=instagram&logoColor=white)](https://www.instagram.com/jacksnxly/)
[![YouTube](https://img.shields.io/badge/-jacksonly-FF0000?style=flat-square&logo=youtube&logoColor=white)](https://www.youtube.com/@jacksonly)
[![TikTok](https://img.shields.io/badge/-@jacksonxly-000000?style=flat-square&logo=tiktok&logoColor=white)](https://www.tiktok.com/@jacksonxly)
[![Website](https://img.shields.io/badge/-jacksonly.xyz-FF5722?style=flat-square&logo=hugo&logoColor=white)](https://jacksonly.xyz)
[![GitHub](https://img.shields.io/badge/-Follow-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/jacksnxly)

---

### Philosophy

> "Ship beats perfect" — I build high-performance systems to solve real problems, then iterate relentlessly. Rust for speed, Python for intelligence, TypeScript for interfaces.

<details>
<summary>Featured: Athenum Architecture</summary>

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

</details>

---

<div align="center">

![GitHub Stats](https://github-readme-stats.vercel.app/api?username=jacksnxly&show_icons=true&hide_border=true&bg_color=00000000&title_color=888888&text_color=666666&icon_color=888888)

**Building systems where milliseconds matter.**

</div>
