# 🐕 G-Shepherd

> *Loyal. Protective. Built for Uzbekistan.*

![Status](https://img.shields.io/badge/Status-Foundation%20Established-brightgreen)
![Stage](https://img.shields.io/badge/Stage-2%20Stabilization-blue)
![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20Flutter%20%7C%20PostgreSQL%20%7C%20Redis-informational)
![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)

G-Shepherd is a sovereign super app built for Uzbekistan — combining secure messaging, social media, government broadcasting, education, job discovery, market data, and AI assistance into a single platform where all data stays within national borders.

No foreign servers. No data leaks. No dependency on apps that can be blocked overnight.

---

## 🧭 Vision

Modern Uzbekistan deserves a modern platform — one that doesn't send its citizens' data to Silicon Valley or Beijing. G-Shepherd is the answer: a single trusted app that replaces the foreign tools an entire generation depends on, built on a foundation of security, privacy, and sovereign infrastructure.

When Teo.AI is ready — it plugs straight in as the intelligent core.

---

## 🏗️ Development Stages

### ✅ Stage 1 — Communication Core *(Complete)*
- [x] Project architecture & modular folder structure
- [x] Core infrastructure (DB, Redis, encryption, logging, security)
- [x] Encrypted chat module — WebSocket + Fernet E2E encryption
- [x] Clean layered architecture — models, schemas, repository, service, routes
- [x] Connection manager — rooms, online status, typing indicators, read receipts
- [x] Ruff linting — 0 errors
- [x] Pytest — all tests passing

### 🔄 Stage 2 — Stabilization *(In Progress)*
- [ ] Refactoring & code cleanup
- [ ] WebSocket edge cases
- [ ] Transaction discipline
- [ ] Race condition handling
- [ ] Async correctness audit
- [ ] Expanded test coverage

### ⏳ Stage 3 — Identity Layer
- [ ] JWT authentication
- [ ] Refresh tokens
- [ ] OTP verification
- [ ] QR identity sharing
- [ ] Contacts system
- [ ] Device trust & session management

### ⏳ Stage 4 — UX Validation
- [ ] Flutter mobile UI
- [ ] WebSocket workflow testing
- [ ] API integration testing
- [ ] Realtime sync behavior
- [ ] Offline state handling

### ⏳ Stage 5 — Security Hardening
- [ ] Penetration testing
- [ ] Abuse prevention
- [ ] Auth hardening
- [ ] WebSocket rate limiting
- [ ] Replay attack protection
- [ ] Suspicious activity detection

### ⏳ Stage 6 — Feature Expansion
- [ ] Government broadcast channel (Redis Streams)
- [ ] Shadow Mode 👻 (anonymous encrypted chat)
- [ ] Stories, video channels, shorts
- [ ] Knowledge base & free lessons
- [ ] Job board
- [ ] E-payment (Click, Payme, Uzcard, Humo)
- [ ] Market observer (stocks, crypto, forex)
- [ ] Teo.AI integration

---

## ✨ Planned Features

### 🔒 Secure Messaging
- End-to-end encrypted direct messages and group chats
- Real-time communication via WebSockets
- Voice messages, media sharing, read receipts, typing indicators

### 📢 Government Broadcast Channel
- Official one-way channel for laws, announcements, and alerts
- Powered by Redis Streams — messages queued and tracked per user
- Smart reminder system — escalating popups until acknowledged
- Server-signed messages so citizens can verify authenticity

### 👻 Shadow Mode *(Easter Egg)*
- Accessed via a hidden trigger in settings
- Fully anonymous — no username, no avatar, no trace
- Messages auto-expire after 7 days
- Screenshot and download protection
- Zero visibility — even to admins

### 📱 Social Layer
- Stories (24hr disappearing posts)
- Video channels with optional anonymous creator mode
- Short-form video feed
- Public community boards

### 📚 Knowledge Base
- Free lessons across all subjects — searchable by topic
- Financial literacy content built in for Gen-Z
- Powered by curated local content + Teo.AI

### 💼 Job Board
- Opt-in channel for job listings and hiring
- Employers post, seekers apply — all within the app

### 💳 E-Payment
- Integrated with Click, Payme, Uzcard, and Humo
- Send money, split bills, pay merchants natively

### 📈 Market Observer
- Live feed: stocks (UZSE), crypto, and forex (USD/UZS, EUR/UZS)
- Read-only — observe, not trade

### 🤖 Teo.AI *(Planned)*
- AI assistant integrated directly into the app
- Daily problem solving, smart search, conversational help
- Built on the Teo platform — Uzbekistan's own AI

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Mobile | Flutter |
| Backend | FastAPI |
| Real-time | WebSockets |
| Broadcast Queue | Redis Streams |
| Cache & Pub/Sub | Redis |
| Database | PostgreSQL + SQLAlchemy + Alembic |
| Media Storage | MinIO (self-hosted) |
| Authentication | JWT + bcrypt |
| Encryption | Fernet (AES-128-CBC) — Strategy Pattern, swappable |
| Deployment | Docker + Nginx (sovereign infrastructure) |

---

## 🧱 Architecture Principles

Built with discipline — not just vibes.

- **SOLID** — every class has one reason to change
- **KISS** — simple solutions over clever ones
- **DRY** — no repeated logic, ever
- **YAGNI** — nothing built before it's needed
- **CQRS** — reads and writes separated for performance
- **SoC** — auth, chat, broadcast, social, payments fully separated
- **TDD** — tests written alongside features
- **Fail Fast** — invalid input dies at the gate
- **LoD** — modules don't know each other's internals
- **Boy Scout Rule** — every commit leaves the code cleaner
- **Observer Pattern** — event-driven WebSocket architecture
- **Strategy Pattern** — swappable encryption algorithms
- **Factory Pattern** — clean message type creation
- **Singleton** — one DB pool, one Redis client

---

## 📁 Project Structure

```
g-shepherd/
├── backend/
│   ├── app/
│   │   ├── core/                  # Shared infrastructure
│   │   │   ├── config.py          # Settings & env vars
│   │   │   ├── database.py        # Async SQLAlchemy engine
│   │   │   ├── encryption.py      # Strategy pattern encryption
│   │   │   ├── security.py        # JWT & password hashing
│   │   │   ├── redis.py           # Redis singleton
│   │   │   ├── logger.py          # Centralized logging
│   │   │   ├── dependencies.py    # FastAPI dependencies
│   │   │   └── websocket.py       # WS base utilities
│   │   ├── modules/
│   │   │   ├── auth/              # Identity & tokens
│   │   │   ├── chat/              # Messaging engine ✅
│   │   │   ├── broadcast/         # Gov channel (planned)
│   │   │   └── shadow/            # Anonymous mode (planned)
│   │   ├── shared/
│   │   │   ├── exceptions/        # Custom error types
│   │   │   ├── middleware/        # Request middleware
│   │   │   ├── responses/         # Standard API responses
│   │   │   └── utils/             # Shared helpers
│   │   └── main.py
│   ├── tests/
│   │   ├── auth/
│   │   ├── chat/
│   │   └── broadcast/
│   ├── requirements.txt
│   └── .env.example
├── Frontend_Web_V/                # Web test client
├── Frontend_App_F/                # Flutter mobile app
└── README.md
```

---

## 🚀 Getting Started

```bash
# Clone
git clone https://github.com/WraithError/G-shepherd_Messenger.git
cd G-shepherd_Messenger

# Setup environment
cd backend
cp .env.example .env
# Fill in your values

# Install dependencies
pip install -r requirements.txt

# Run
uvicorn app.main:app --reload

# Check health
curl http://localhost:8000/health
# → {"status": "ok", "app": "G-Shepherd"}
```

---

## 👤 Author

**Firdavs** — aka *Reaper* `</>`
Junior Developer | Python & Flutter | Tashkent, Uzbekistan
`WraithError` on GitHub — *One mind. Every tool.*

---

> *"A German Shepherd doesn't ask who you are. It just protects you."*
