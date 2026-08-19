# Huvo AI Sales Agent

A full-stack conversational real-estate sales-agent prototype built for the Huvo AI assessment. It qualifies a lead through a state-aware chat flow, guides the conversation in English, Hindi, or Hinglish, and orchestrates common sales outcomes such as a site-visit request, follow-up, and human handoff. The repository is intentionally self-contained: the active agent uses deterministic responses and simulated business integrations so the demonstrated flow can run locally without a paid LLM or external calendar/CRM.

## Quick Start

Start the backend in one PowerShell terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then start the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). API documentation is available at `http://127.0.0.1:8000/docs`.

## Key Capabilities

- Stateful lead qualification for property type, budget, location, purchase purpose, and timeline
- Rule-based extraction for common real-estate expressions, including 2/3/4 BHK, lakh/crore budgets, and Delhi NCR locations
- English, Hindi (Devanagari), and Hinglish response paths
- Price-objection and “not ready” handling in the deterministic agent
- Simulated site-visit booking, follow-up scheduling, and human-sales escalation
- Booking failure simulation that never reports an unconfirmed booking as successful
- React dashboard with live lead-profile and conversation-outcome panels
- Qualification/outcome summary API

## Why This Project

Property enquiries are often incomplete: an agent needs to gather requirements without forcing the lead through a rigid form, then move the conversation to an appropriate next action. This project separates that work into small services: one extracts and retains lead context, one decides the next conversational prompt, and dedicated services model business outcomes. That makes the core flow easy to inspect, test manually, and replace with production integrations later.

## Architecture

```text
Customer
   |
   v
React + Vite dashboard (frontend/src/App.jsx)
   |  POST /chat with the browser-held ConversationState
   v
FastAPI API (backend/app/api/chat.py)
   |
   +--> StateService: extract qualification data and language
   |
   +--> FollowUpService / EscalationService / BookingService
   |       (simulated workflow outcomes, when requested)
   |
   +--> AgentService --> LLMProvider --> MockLLMProvider
   |                                  (default deterministic responses)
   v
ChatResponse { response, updated state }
   |
   v
Dashboard message history, Lead Profile, and Conversation Outcomes

ConversationState --> POST /analytics/summary --> AnalyticsService
```

The API route stays thin: it coordinates the request and delegates extraction, response generation, and business actions to focused services. `ConversationState` is the shared contract between the browser, API, agent, and analytics summary.

## Project Structure

```text
.
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py                 # FastAPI app, CORS, health route
│       ├── api/                    # /chat and /analytics routes
│       ├── core/                   # environment settings and agent prompt
│       ├── models/                 # Pydantic request/response/state models
│       └── services/               # state, agent, LLM, workflow, analytics services
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx                 # chat/dashboard and backend integration
│       ├── App.css
│       ├── index.css
│       └── main.jsx
└── README.md
```

## Conversation / Agent Flow

For every `POST /chat`, the application follows this order:

1. `StateService` updates the supplied `ConversationState` from the latest message.
2. The route extracts a simple site-visit date/time and a simple follow-up time from the message; explicitly supplied request fields take precedence.
3. If a follow-up time is available, it returns a simulated follow-up result.
4. Otherwise, if an explicit human request or `escalation_reason` is present, it returns a simulated escalation result.
5. Otherwise, if both a site-visit date and time are available, it attempts a simulated booking, including the optional failure path.
6. If no workflow action applies, `AgentService` builds prompt context from the updated state and message, then uses the configured provider to generate the reply.

The frontend stores the returned state in React state and sends it back with the next message. The backend has no server-side conversation store, so this state round-trip is what preserves context during a browser session.

## Lead Qualification

`ConversationState` supports these lead fields:

| Field | Meaning and extraction |
| --- | --- |
| `name` | Lead name field; present in the model and dashboard, but not currently extracted. |
| `language` | `Hindi` when Devanagari is found; `Hinglish` when at least two configured Hindi transliterations occur; otherwise `English`. |
| `property_type` | Regex detects 2, 3, or 4 BHK. |
| `budget` | Regex normalizes common lakh/lac/crore/cr expressions to values such as `₹1.5 Cr`. |
| `preferred_location` | Matches a fixed set of Delhi NCR locations: Gurgaon/Gurugram, Noida, Greater Noida, Delhi, Faridabad, Ghaziabad, Dwarka, and Manesar. |
| `buying_purpose` | Detects configured self-use and investment phrases. |
| `purchase_timeline` | Detects simple week/month/year expressions and a small set of phrases such as “immediately” and “next month.” |

The mock agent checks the state before selecting its next question, progressing through property type, budget, location, purpose, and timeline rather than asking for fields already present. Extractors can update a field when a later message contains a new value; this is useful for corrections but is not conflict resolution.

## Conversation State

The request model defaults to an empty state, so API clients can omit it on the first turn. A representative state returned after qualification and a successful simulated booking is:

```json
{
  "name": null,
  "language": "English",
  "budget": "₹1.5 Cr",
  "preferred_location": "Gurgaon",
  "property_type": "3 BHK",
  "buying_purpose": "Self-use",
  "purchase_timeline": "6 months",
  "site_visit_requested": true,
  "site_visit_date": "20 September",
  "site_visit_time": "11:00 AM",
  "booking_status": "confirmed",
  "human_escalation_requested": false,
  "escalation_id": null,
  "follow_up_requested": false,
  "follow_up_time": null,
  "follow_up_id": null
}
```

The state also records workflow flags and generated reference IDs. It is in-memory in the browser rather than persisted, so refreshing the page or changing clients loses the conversation unless the client retains and resubmits it.

## LLM / Agent Design

`LLMProvider` is a small protocol with one `generate(context)` operation. `AgentService` owns context construction: it combines the system prompt, serialized conversation state, and customer message, then delegates generation to the provider.

`MockLLMProvider` is the default active provider. It produces deterministic, context-aware replies for qualification, language selection, objections, and readiness; it does not call an external service. This keeps development and review reproducible and cost-free while preserving a clean seam for provider substitution.

The repository also contains `LLMService`, an OpenAI Responses API wrapper configured from environment variables. It is not connected to `AgentService` or the running `/chat` path, so an OpenAI key is not required for the demonstrated application.

## Safety, Reliability, and Business Logic

The agent prompt instructs the system not to invent property facts, prices, discounts, availability, or booking outcomes. The deterministic objection response follows that policy by declining to assert unconfirmed offers. Booking returns a confirmation only on a successful simulated result; its failure path offers an alternative or human assistance.

FastAPI/Pydantic validates chat payloads, including a non-empty `message`. Business actions are separated from the conversational reply path, and their result IDs/statuses are written to state, giving the UI an explicit outcome rather than inferring one from prose.

## Booking, Escalation, and Follow-up

### Booking

The chat route accepts `site_visit_date` and `site_visit_time`, or extracts both from a message containing an English month date (for example, `20 September`) and 12-hour time (for example, `11 AM`). When both values are present, `BookingService` creates a simulated booking reference and marks the state `confirmed`. Sending `simulate_booking_failure: true` exercises the failure response and sets `booking_status` to `failed`. There is no calendar integration or persisted appointment record.

### Escalation

An explicit `escalation_reason` or configured phrases such as “speak to a human” trigger `EscalationService`. It creates a simulated escalation ID, sets `human_escalation_requested`, and responds that a sales representative should follow up. It does not contact a person or create a CRM task.

### Follow-up

`follow_up_time` may be supplied directly, or extracted from a narrow pattern such as `tomorrow at 4 PM` / `next week 10:30 AM`. `FollowUpService` returns a simulated follow-up ID and writes it to state. This records a preference only; no background scheduler or outbound follow-up exists.

## Analytics

`POST /analytics/summary` accepts a `ConversationState` and returns a computed qualification percentage across budget, location, property type, buying purpose, and purchase timeline, plus site-visit, follow-up, and escalation outcomes. It is a lightweight backend summary service; the current React UI does not call or display this endpoint as a separate analytics dashboard.

## Frontend

The React 19/Vite UI is a focused sales-agent dashboard. `App.jsx` provides a conversation panel, typing state while the request is pending, Enter-to-send behavior, and a graceful in-chat backend-connection error. The right-hand panel renders the returned lead profile and workflow outcomes live. The frontend calls `http://127.0.0.1:8000/chat` directly and sends its current state with every message.

## API

FastAPI serves interactive OpenAPI documentation at `http://127.0.0.1:8000/docs` while the backend is running.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Returns backend service health. |
| `POST` | `/chat` | Updates lead state and returns either a workflow outcome or agent reply. |
| `POST` | `/analytics/summary` | Produces qualification and outcome metrics for a supplied state. |

### `POST /chat`

Request fields are `message` (required), `state` (optional, defaults to an empty `ConversationState`), `site_visit_date`, `site_visit_time`, `simulate_booking_failure`, `escalation_reason`, and `follow_up_time`.

```json
{
  "message": "I need a 3 BHK under 1.5 crore in Gurgaon for my family"
}
```

```json
{
  "response": "Understood. When are you planning to make the purchase?",
  "state": {
    "name": null,
    "language": "English",
    "budget": "₹1.5 Cr",
    "preferred_location": "Gurgaon",
    "property_type": "3 BHK",
    "buying_purpose": "Self-use",
    "purchase_timeline": null,
    "site_visit_requested": false,
    "site_visit_date": null,
    "site_visit_time": null,
    "booking_status": null,
    "human_escalation_requested": false,
    "escalation_id": null,
    "follow_up_requested": false,
    "follow_up_time": null,
    "follow_up_id": null
  }
}
```

The exact response text reflects the updated state; here, purchase timeline is the next missing qualification field.

## Setup

Prerequisites: Python and Node.js/npm. From the repository root, run the backend in one PowerShell terminal:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then run the frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL printed by the frontend (normally `http://localhost:5173`). The backend is available at `http://127.0.0.1:8000`, health at `/health`, and Swagger UI at `/docs`. The configured CORS policy permits the standard Vite localhost addresses.

## Environment Configuration

`backend/.env.example` documents `OPENAI_API_KEY` and optional `OPENAI_MODEL` (default: `gpt-5.5`) for the standalone `LLMService`. Copy it to a local `.env` only when wiring that service into an application path; do not commit `.env` files. The active assessment flow uses `MockLLMProvider`, so no external LLM API key is required to run the chat UI as shipped.

## Testing / Verification

No automated test suite is present in this repository. The frontend provides `npm run lint` and `npm run build` scripts; these are useful local checks but are not a test suite.

Manual scenarios supported by the implementation include:

- Qualifying a lead across several turns and observing the Lead Profile update
- Hindi text in Devanagari and Hinglish phrases
- A price objection such as “This is too expensive”
- “I am not ready now” followed by `tomorrow at 4 PM`
- “I want to speak to a human”
- A site visit message such as `Please book 20 September at 11 AM`
- The booking failure path via a direct `/chat` request with `simulate_booking_failure: true`

## Example End-to-End Conversation

```text
Customer → I am looking for a 3 BHK under 1.5 crore in Gurgaon for my family.
Agent    → Understood. When are you planning to make the purchase?

Customer → Within 6 months.
Agent    → Thanks, I have the main requirements. Would you like me to help arrange a site visit for the property?

Customer → Please book a visit for 20 September at 11 AM.
Agent    → Your site visit has been booked for 20 September at 11:00 AM. Your booking reference is HUVO-20 September-1100 AM.
```

The booking reference format is simulated and derived from the provided date/time; it is not a calendar confirmation.

## Engineering Decisions

| Decision | Benefit | Trade-off |
| --- | --- | --- |
| Pydantic state as the shared contract | Typed request/response validation and explicit, inspectable conversation context | The client must return state on every turn; it is not durable storage. |
| Thin API with focused services | Keeps extraction, workflow actions, analytics, and response generation independently understandable | The orchestration order is fixed in one route for this assessment-sized application. |
| Provider protocol with deterministic default | Reproducible, zero-cost local demonstrations and a clear substitution point for an LLM | The mock only handles the coded scenarios and is not open-ended natural-language reasoning. |
| Dedicated simulated workflow services | Lets the UI and API exercise success/failure/handoff state without external accounts | No actual calendar, CRM, notifications, or scheduler is invoked. |
| Rule-based extraction | Transparent and predictable for the targeted lead fields | Coverage is intentionally narrow and language/location-specific. |

## Known Limitations

- Conversation state is browser-held and is lost on refresh; there is no database or server-side session.
- The default conversational agent is deterministic and supports only its implemented rules and response paths.
- Extraction is regex/phrase based; name capture, broad geography, and flexible natural-language dates are not implemented.
- Booking, escalation, and follow-up are simulations; their generated IDs are not persisted or integrated with external systems.
- The frontend uses a fixed local backend URL and does not invoke the analytics endpoint.
- There is no authentication, authorization, observability pipeline, or automated test suite.

## Production Evolution

The next production-focused steps would be:

1. Persist conversations, leads, and workflow records in a database with server-side session ownership.
2. Replace or augment the mock provider with a production LLM adapter, structured outputs, prompt/version controls, timeouts, and fallbacks.
3. Integrate a calendar for real appointment confirmation and a CRM for escalations and lead ownership.
4. Add a durable job queue and notification channel for follow-ups.
5. Improve multilingual entity extraction and date/time parsing with validation and timezone handling.
6. Add authentication, role-based access, audit logs, metrics, tracing, and automated unit/integration/e2e tests.
7. Configure environment-specific frontend API URLs, CI, and deployment.

## Security

Keep provider credentials in environment variables and out of version control; `.env` patterns are ignored by the repository. FastAPI/Pydantic validates inbound chat models, but the current prototype does not authenticate callers or enforce authorization. A production deployment should protect the API, restrict CORS to known origins, minimize retained customer data, and secure any LLM, calendar, and CRM credentials.

## Assessment Summary

This implementation demonstrates a modular full-stack sales-agent flow: explicit conversational state, deterministic qualification behavior, business-workflow orchestration with an honest failure path, and a live frontend/backend integration. Its provider abstraction and service boundaries make the assessment scope reproducible today while leaving clear paths to durable storage and real integrations.

## Author

Built as part of the Huvo AI Sales Agent assessment.
