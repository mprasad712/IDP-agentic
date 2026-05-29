# Document Intelligence Platform (IDP) — Project Brief

> **PwC Technology Consulting** · Internal — Confidential  
> Last updated: 2026-05-29

---

## 1. What This Product Is

A multi-tenant SaaS platform that **classifies, extracts, validates, and audits data from any document type**, arriving through any channel, with audit-grade output that withstands compliance review.

**Positioning**: One platform. Any document. Any channel. Audit-grade output.  
Replaces fragmented OCR stacks (separate tools for invoices, KYC, bank statements, contracts) with one configuration-driven pipeline.

---

## 2. The Seven Pillars (Product Architecture)

| # | Pillar | What it does |
|---|--------|-------------|
| 1 | **Channel-Agnostic Intake** | Email (M365/Gmail/IMAP), OneDrive, SharePoint, S3, SFTP, REST upload, Vendor portal — all normalised to a canonical `DocumentIntake` event |
| 2 | **Image Quality Pipeline** | Deskew, rotation correction, perspective correction, glare/shadow removal, low-res upscaling, handwriting recognition — 8 steps before any OCR/LLM |
| 3 | **Universal Classifier & Extractor** | 30+ document types out of the box; 4-layer classification (visual + textual + multi-doc splitter + confidence reconciliation); add new types via UI with prompt-driven or sample-driven schema generation |
| 4 | **Visual Element Detection** | Signatures, stamps/seals, checkboxes, QR codes/barcodes, logos, handwritten annotations — all as structured outputs |
| 5 | **Long Document Handling** | Section-aware chunking, multi-page table reconstruction, cross-page entity linking, hierarchical extraction, streaming processing, lost-in-the-middle mitigation |
| 6 | **Extraction Quality Layer** | Multi-model selector with fallback, per-field calibrated confidence, self-correcting math loop (MathReconcileAgent), reasoning trace as first-class output |
| 7 | **Audit-Grade Output** | Field-level provenance (value, confidence, reasoning, page/bbox, model, processing applied, reviewer chain), immutable append-only audit log, PII detection & redaction (4 modes), observability, explainable AI |

---

## 3. Target Production Stack (from Architecture Docs)

### Frontend
| Tech | Version | Purpose |
|------|---------|---------|
| React | 18.x | Reviewer dashboard, Admin console, Ops dashboard, Vendor portal |
| TypeScript | 5.x | Type safety |
| Vite | 5.x | Build tool |
| Tailwind CSS | 3.x | Styling |
| React Router | 6.x | Client-side routing |
| Recharts | 2.x | Ops dashboard charts |

### Backend
| Tech | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Language |
| FastAPI | 0.115+ | Async web framework |
| Pydantic | 2.x | Schemas |
| uvicorn | 0.30+ | ASGI server |
| SQLAlchemy | 2.x (async) | ORM |
| Alembic | 1.13+ | DB migrations |
| OpenCV (cv2) | 4.x | Image preprocessing pipeline |
| Pillow | 10.x | Image I/O |
| pdfplumber + pypdfium2 | 0.11.x / 4.x | PDF parsing |
| httpx | 0.27+ | Async HTTP (LLM calls, webhooks) |
| python-jose | 3.3+ | JWT |
| passlib | 1.7.x | Password hashing |
| slowapi | 0.1.9+ | Rate limiting |

### Data / Infrastructure (Azure)
| Service | SKU | Purpose |
|---------|-----|---------|
| Azure SQL Database | Business Critical 8vCore, zone-redundant | All structured data — 12 tables |
| Azure Blob Storage | Standard RA-GRS Hot+Cool | Raw docs + preprocessed images (WORM) |
| Azure Cache for Redis | Premium P1, zone-redundant | Sessions, idempotency, rate limits |
| Azure Service Bus | Standard tier | Durable event queue between modules |
| Azure Key Vault | Premium HSM-backed | Secrets, OAuth tokens, PII vault |

### LLM Layer (Multi-Provider via Model Router)
| Provider | Model | Role |
|----------|-------|------|
| Azure OpenAI | GPT-4o (PTU) | Primary for most tenants |
| Anthropic Claude | Claude Sonnet 4 | Long-form contracts, reasoning-heavy |
| Google Gemini | Gemini 2.5 Pro | Multilingual (Indian regional languages) |
| Self-hosted LLM | Llama 3.x / Mistral on AKS+vLLM | Data-residency-sensitive tenants |

### Identity
- **Microsoft Entra ID** via OIDC Auth Code + PKCE
- JWT tokens carry user identity, tenant context, Entra group memberships
- SQL Row-Level Security (`SESSION_CONTEXT('tenant_id')`) enforces tenant isolation at DB level

### Hosting
- FastAPI → Azure App Service (Linux, Premium P2v3, multi-instance, zone-spread)
- React → Azure Static Web Apps (CDN)
- Azure Load Balancer Standard SKU (zone-redundant) as public entry point
- 5 environments: Dev → Test → Staging → Pre-Production → Production (CAB gate + canary)

---

## 4. Data Model (12 SQL Tables)

### Reference group
- **tenant** — one row per customer org; drives `data_residency`, `retention_years`
- **case** — unit of work; statuses: PENDING / PROCESSING / AUTO_APPROVED / NEEDS_REVIEW / REJECTED / DUPLICATE
- **document_type** — versioned config per doc type; `field_schema_json`, `extraction_prompt`, `validators_json`, `confidentiality` (PUBLIC/INTERNAL/CONFIDENTIAL/RESTRICTED)
- **vendor_master** — known counterparties; `tax_id_vault_ref` → Key Vault

### Transactional group
- **extraction** — one row per LLM call; records provider, model, version, prompt_hash, tokens_used, cost_usd
- **field_record** — one row per extracted field; `value_text`, `value_vault_ref`, `masking_mode`, `raw_confidence`, `calibrated_confidence`, `reasoning`, `page_number`, `was_corrected`
- **visual_element** — stamps, signatures, checkboxes, QR codes per case
- **audit_log** — append-only (INSTEAD OF UPDATE/DELETE triggers); 7-year default retention

### Configuration group
- **channel_config** — per-tenant intake channel settings; credentials via Key Vault
- **model_routing_rule** — LLM routing: priority, `match_predicate_json`, primary provider, `fallback_chain_json`, `ab_bucket_pct`
- **role_assignment** — TENANT / VENDOR / DOCUMENT_TYPE scope
- **app_user** — Entra-synced; JIT-provisioned on first login

---

## 5. RBAC — Six Platform Roles

| Role | Permissions |
|------|-------------|
| `reviewer` | View cases, correct fields, approve/reject cases |
| `senior_reviewer` | reviewer + reassign + override QA gates |
| `administrator` | Configure doc types, channels, model routing, RBAC |
| `compliance_officer` | Read-only audit log, export, detokenise PII (JIT, with reason) |
| `operations` | Ops dashboard, replay cases, view metrics — cannot read PII |
| `vendor_user` | Vendor portal only, own submitted cases only |
| `platform_admin` | JIT only for incident response; bypasses RLS; every action Sev-2 alerted |

---

## 6. Current Implementation State (as of 2026-05-29)

### What's built

**Backend** (`backend/`)
```
backend/
├── main.py              # FastAPI app; lifespan: _ensure_database_exists() + _seed_users()
├── alembic.ini          # Alembic config (URL from .env: postgresql+asyncpg://postgres:1234@localhost/idp)
├── alembic/
│   ├── env.py           # Async-compatible Alembic env; reads DATABASE_URL from settings
│   ├── script.py.mako   # Migration template
│   └── versions/
│       └── 0001_initial_users_table.py   # Initial migration: users table
├── app/
│   ├── api/auth.py      # POST /api/auth/login, GET /api/auth/me, POST /api/auth/logout
│   ├── core/
│   │   ├── config.py    # pydantic-settings: SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES=480, DATABASE_URL
│   │   └── security.py  # hash_password(), verify_password(), create_access_token(), decode_access_token()
│   ├── db/
│   │   ├── base.py      # SQLAlchemy DeclarativeBase
│   │   ├── models.py    # User ORM: id(str PK "usr_*"), email, display_name, hashed_password, role, is_active
│   │   └── session.py   # async engine (pool_size=5, max_overflow=10), AsyncSessionLocal, get_db()
│   └── models/user.py   # Pydantic: UserRole(enum), LoginRequest, UserOut, TokenResponse
└── requirements.txt
```

**Demo users seeded at startup:**
- `admin@idp.local` / `Admin@123` → role: administrator
- `reviewer@idp.local` / `Review@123` → role: reviewer

**UserRole enum values:** reviewer, senior_reviewer, administrator, compliance_officer, operations, vendor_user

**Frontend** (`frontend/src/`)
```
src/
├── App.jsx              # Routes: /login (PublicRoute), /register (PublicRoute), /dashboard (PrivateRoute)
├── main.jsx
├── context/AuthContext.jsx   # AuthProvider: user state, login(), logout(), loading
├── api/auth.js               # authApi.login(), authApi.getMe()
├── components/auth/
│   ├── Login.jsx        # Full PwC-branded 2-panel login (navy + orange theme)
│   └── Register.jsx     # Registration page
└── pages/Dashboard.jsx  # Protected dashboard (stub — needs implementation)
```

**Design system (Tailwind custom tokens):**
- `pwc-navy` — dark blue (left panel bg, text)
- `pwc-orange` / `pwc-orange-dark` — PwC orange (CTAs, accents)
- `pwc-surface` / `pwc-surface-dark` — light grey surfaces
- `pwc-gray-cool` / `pwc-gray-light` / `pwc-slate` — grey text variants
- `shadow-glow-orange` — orange glow on icon

### What's NOT built yet (roadmap)

**Backend:**
- [ ] Document intake channels (email M365/Gmail, OneDrive, S3, SFTP, REST upload)
- [ ] Image quality pipeline (OpenCV: deskew, rotation, perspective, glare, upscale, handwriting)
- [ ] Universal classifier (visual + textual, multi-doc splitter)
- [ ] LLM extraction engine + model router (Azure OpenAI, Claude, Gemini fallback chain)
- [ ] Visual element detection (signatures, stamps, checkboxes, QR)
- [ ] Long document handling (chunking, multi-page table reconstruction, entity linking)
- [ ] Extraction quality layer (confidence calibration, math reconciliation, reasoning trace)
- [ ] Audit log (immutable, append-only, Service Bus integration)
- [ ] PII detection + redaction (4 modes: FULL_MASK, PARTIAL_MASK, TOKENISE, VAULT_ONLY)
- [ ] Full RBAC middleware (role scoping, JIT elevation)
- [ ] Webhook delivery (HMAC-signed outbound events)
- [ ] Azure Blob Storage integration
- [ ] Azure Service Bus integration
- [ ] Redis session/cache layer
- [ ] Azure Key Vault secrets integration
- [ ] Multi-tenant Row-Level Security
- [ ] Remaining DB tables (10 of 12 tables)

**Frontend:**
- [ ] Dashboard (reviewer interface — case list, case detail, field correction, approve/reject)
- [ ] Admin console (document type config, channel config, model routing rules, RBAC)
- [ ] Operations dashboard (throughput, latency, LLM cost, queue depth)
- [ ] Vendor portal

---

## 7. Local Dev Setup

**Backend:**
```powershell
# From backend/
.venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**.env:**
```
SECRET_KEY=idp-super-secret-key-change-in-production-2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
FRONTEND_URL=http://localhost:5173
DATABASE_URL=postgresql+asyncpg://postgres:1234@localhost:5432/idp
```

**Alembic (from backend/):**
```powershell
alembic upgrade head          # Apply migrations (creates users table)
alembic current               # Check migration state
alembic stamp head            # Mark existing DB as up-to-date without running migrations
alembic revision --autogenerate -m "description"  # Generate new migration after model change
alembic downgrade -1          # Roll back one
```

**Frontend:**
```powershell
# From frontend/
npm install
npm run dev   # Vite dev server at http://localhost:5173
```

**API base URL:** `http://localhost:8000/api`

---

## 8. Key API Endpoints (implemented)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/auth/login` | None | `{email, password}` → `{access_token, token_type, expires_in, user}` |
| GET | `/api/auth/me` | Bearer JWT | Returns current user (`UserOut`) |
| POST | `/api/auth/logout` | None | Returns `{message}` (stateless) |
| GET | `/health` | None | `{status: "ok", service: "IDP API"}` |

---

## 9. Phase Roadmap

**Phase 1 (current):** Universal platform pillars — auth, intake, image quality, classification, extraction, visual elements, long docs, quality layer, audit output.

**Phase 2 (planned):** Invoice processing as first end-to-end use case — email intake → extraction → 3-way PO matching → ERP posting.

**Phase 3+:** KYC bundles, bank statements, contracts, claim forms — same pipeline, different config.

---

## 10. Key Design Decisions

1. **FastAPI only** — no Django. Async-native, Pydantic validation, one ORM, one observability layer.
2. **Azure SQL for everything** — relational shape fits the data; JSON columns handle variable-schema fields per doc type.
3. **Multi-LLM router from day one** — no vendor lock-in; Tamil invoices may route differently than English contracts.
4. **Masking before storage, never at presentation** — PII vault-only fields never touch the application DB.
5. **Alembic owns schema** — `create_all()` removed from `main.py`; all schema changes go through versioned migrations.
6. **Row-Level Security at DB tier** — even if app code passes wrong `tenant_id`, SQL filters it.
