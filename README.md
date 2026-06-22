# DealScout

> **Autonomous deal-hunting AI** - an agentic system that estimates what a product is *really* worth and surfaces online bargains in real time.

DealScout estimates the price of any product from its text description, then puts
that capability to work: a team of AI agents continuously scans online deals,
prices each one with an ensemble of models, and pushes you a notification when it
finds something selling for far below its estimated value.

It's built in **three phases**, taking a model from raw data all the way to a
deployed, autonomous, agentic application.

---

## Highlights

- **800K-product dataset** curated from Amazon metadata into a clean `Item` model.
- **Multiple estimators**: traditional ML baselines, a residual deep neural net,
  a fine-tuned frontier model, and a QLoRA fine-tuned **Llama-3.2-3B**.
- **RAG pricing** with a Chroma vector store + frontier LLM.
- **Ensemble agent** that blends a Modal-hosted specialist model, RAG, and the DNN.
- **Autonomous agent team** that scans RSS deal feeds, prices opportunities, and
  alerts you via push notification - orchestrated with LLM tool-calling.
- **Live Gradio dashboard** that streams agent activity, tracks the scrape ->
  price -> notify pipeline in real time, spotlights the best opportunity, and
  raises push-style deal alerts.
- **Demo mode** - a self-contained, **LLM-free** build (curated sample deals,
  zero API / network / model calls) made to run on **Hugging Face Spaces** so you
  can share a live, reliable demo without exposing any keys.

---

## Architecture

DealScout is organized as one installable Python package (`src/dealscout`) plus
notebooks that tell the build story. See [`docs/architecture.md`](docs/architecture.md)
for the full diagram.

```
Phase 1: Modeling      ->  Phase 2: Open-Source FT   ->  Phase 3: Agentic App
-----------------          ----------------------        --------------------
curate dataset             QLoRA fine-tune               Modal SpecialistAgent
baselines + DNN            Llama-3.2-3B                   Chroma RAG FrontierAgent
frontier fine-tune         (Colab GPU)                    EnsembleAgent
                                                          Scanner + Messaging
                                                          Autonomous Planner
                                                          Gradio dashboard
```

| Layer | Module | Responsibility |
|-------|--------|----------------|
| Core | `dealscout.core` | `Item` model, dataset `parser`, parallel `ItemLoader`, `evaluate` harness |
| Models | `dealscout.models` | Deep neural network (train + inference), LLM `Preprocessor`, Groq `Batch` summarizer |
| Deployment | `dealscout.deployment` | Modal apps - `pricer_service2` serves the fine-tuned model |
| Agents | `dealscout.agents` | Specialist, Frontier (RAG), NeuralNetwork, Ensemble, Scanner, Messaging, Planning, AutonomousPlanning |
| Framework | `dealscout.framework` | `DealAgentFramework` wiring agents to Chroma + `memory.json` |
| Config | `dealscout.config` | `DEMO_MODE` switch that selects the real pipeline vs. the demo |
| Demo | `dealscout.demo` | `DemoAgentFramework` simulator + curated `sample_deals` (no LLM/network) |
| App | `app/dealscout_app.py` | Gradio dashboard (real **and** demo); root `app.py` is the Spaces entry |

See [`docs/architecture.md`](docs/architecture.md) for the full component and
data-flow breakdown, including how demo mode avoids every heavy import.

---

## Project structure

```
DealScout/
|-- README.md
|-- LICENSE
|-- pyproject.toml              # Full package + dependencies (installable via pip/uv)
|-- requirements.txt            # Slim deps for the Hugging Face Spaces demo
|-- app.py                      # Hugging Face Spaces entry point (forces demo mode)
|-- .env.example                # Copy to .env and fill in your keys
|-- .gitignore
|
|-- src/dealscout/
|   |-- config.py               # DEMO_MODE switch (reads DEALSCOUT_DEMO_MODE)
|   |-- core/                   # items, parser, loaders, evaluator
|   |-- models/                 # deep_neural_network, preprocessor, batch
|   |-- deployment/             # dealscout_service (Modal app serving the FT model)
|   |-- agents/                 # the agent team + deals data models
|   |-- framework/              # deal_agent_framework, log_utils
|   `-- demo/                   # demo_engine + sample_deals (LLM-free demo)
|
|-- app/
|   `-- dealscout_app.py        # Gradio dashboard (real + demo modes)
|
|-- notebooks/
|   |-- phase1_data_modeling/   # 01-05: curation -> baselines -> DNN -> frontier FT
|   |-- phase2_finetuning/      # 06-09: QLoRA -> prompts -> train (Colab) -> eval
|   `-- phase3_agents/          # 10-14: Modal -> RAG/ensemble -> scanner -> autonomous
|
|-- scripts/
|   `-- build_vectorstore.py    # Populate the Chroma vector store
|
|-- tests/                      # pytest: items, evaluator, agents
`-- docs/
    `-- architecture.md
```

---

## Getting started

### 1. Prerequisites

- Python **3.11+**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
- Accounts/keys as needed per phase (OpenAI, HuggingFace, Modal, Pushover, etc.)

### 2. Install

```bash
git clone https://github.com/your-username/dealscout.git
cd dealscout

# with uv (recommended)
uv venv
uv pip install -e ".[dev]"

# or with pip
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Installing in editable mode (`-e`) means notebooks and scripts can simply
`from dealscout.core.items import Item` from anywhere.

> Just want the no-key demo? Skip the full install and use the slim deps instead:
> `uv pip install -r requirements.txt`, then `uv run python app.py`. See
> [Demo mode](#demo-mode-no-llm--hugging-face-spaces) below.

### 3. Configure secrets

```bash
cp .env.example .env
# edit .env and add your keys
```

| Variable | Needed for |
|----------|-----------|
| `OPENAI_API_KEY` | Frontier agent, scanner agent, frontier fine-tuning |
| `HF_TOKEN` | Loading/pushing datasets & models on the HuggingFace Hub |
| `ANTHROPIC_API_KEY` | Messaging agent (crafts alerts with Claude) |
| `GROQ_API_KEY` | Batch / fast preprocessing |
| `MODAL_TOKEN_ID` / `MODAL_TOKEN_SECRET` | Deploying the fine-tuned model |
| `PUSHOVER_USER` / `PUSHOVER_TOKEN` | Push notifications for deals |

---

## Running each phase

### Phase 1 - Modeling (`notebooks/phase1_modeling`)
Curate the dataset, build baselines, train the deep neural network, and fine-tune
a frontier model. Run the notebooks `01` -> `05` in order. Models are evaluated
with `dealscout.core.evaluator.evaluate`.

### Phase 2 - Open-source fine-tuning (`notebooks/phase2_finetuning`)
Prepare prompt/completion data (`06`-`07`), run QLoRA training on **Google Colab**
(`08`, GPU required), and evaluate (`09`). The fine-tuned adapter is published to
the HuggingFace Hub.

### Phase 3 - Agentic application (`notebooks/phase3_agents`)

```bash
# 1. Deploy the fine-tuned model to Modal
uv run modal deploy -m dealscout.deployment.dealscout_service

# 2. Build the Chroma vector store for RAG
uv run python scripts/build_vectorstore.py --lite   # or omit --lite for full

# 3. Launch the live dashboard (real mode - uses your keys)
uv run python app/dealscout_app.py
```

Walk through notebooks `10` -> `13` to build up each agent, or jump straight to the
app once the model is deployed and the vector store is built.

> **Note:** the `NeuralNetworkAgent` expects `deep_neural_network.pth` (produced in
> Phase 1, Step 4) in the working directory.

---

## Demo mode (no LLM) & Hugging Face Spaces

DealScout ships with a **demo mode** so you can show the product to anyone -
without API keys, GPUs, a Modal deployment, or a vector store. It runs the same
dashboard on a curated set of sample deals and a simulated agent pipeline, and it
**never makes a network, model, or API call**.

### What demo mode does (and does not) do

| | Real mode (default) | Demo mode |
|---|---|---|
| Deal source | Live DealNews RSS scraping | Curated `sample_deals` |
| Pricing | Modal specialist + RAG frontier + DNN ensemble | Pre-computed sample estimates |
| Notifications | Real Pushover push | Simulated in-app push cards |
| Heavy deps | torch, modal, chromadb, openai, ... | **none** (gradio + pydantic only) |
| API keys | Required | **None** |

The dashboard UI is identical in both modes: a hero header, KPI cards, a live
**Scrape -> Summarize -> Price -> Rank -> Notify** pipeline stepper, the best-deal
spotlight, an opportunities table, a streaming agent activity log, and a
notifications feed.

### Run the demo locally

```bash
# Option A - the Hugging Face Spaces entry point (forces demo mode)
uv run python app.py

# Option B - the dashboard with the demo flag set explicitly
#   PowerShell:  $env:DEALSCOUT_DEMO_MODE = "1"
#   bash:        export DEALSCOUT_DEMO_MODE=1
uv run python app/dealscout_app.py
```

`app.py` sets `DEALSCOUT_DEMO_MODE=1` **before** importing DealScout, so the demo
boots with only the slim dependencies. The single switch lives in
[`src/dealscout/config.py`](src/dealscout/config.py) and reads the
`DEALSCOUT_DEMO_MODE` environment variable (accepts `1/true/yes/on`); when it is
unset or `false`, the full real pipeline runs exactly as before.

### Deploy to Hugging Face Spaces

1. Create a new **Gradio** Space.
2. Push this repository to it (or point the Space at your GitHub repo).
3. Spaces installs from `requirements.txt` (the slim set) and runs `app.py`
   automatically - demo mode is forced on, so **no secrets are needed**.

Add this front-matter block to the top of the Space's `README.md` so it boots as
a Gradio SDK app:

```yaml
---
title: DealScout
emoji: 📎
colorFrom: green
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
---
```

> **Tip:** if you ever want the hosted Space to use the real pipeline, add your
> keys as Space **secrets** and set `DEALSCOUT_DEMO_MODE=false` - but note that
> live scraping plus model calls are slower and less reliable on shared hardware.

---

## Tests

```bash
uv run pytest
```

The test suite covers the pure logic (dataset parsing, evaluation helpers, and the
agent data models) and runs without any network or model access.

---

## Tech stack

**LLMs & ML:** OpenAI, Anthropic, Groq, HuggingFace Transformers, PEFT/QLoRA,
PyTorch, scikit-learn, XGBoost
**RAG & data:** Chroma, SentenceTransformers, HuggingFace Datasets
**Infra & UI:** Modal (serverless GPU), Gradio, Pushover, LiteLLM, Pydantic
**Demo:** Hugging Face Spaces (Gradio SDK), running on Gradio + Pydantic only

---

## Acknowledgements

DealScout is a personal portfolio project inspired by the capstone of an LLM
engineering course. The dataset is derived from the
[Amazon Reviews 2023](https://huggingface.co/datasets/McAuley-Lab/Amazon-Reviews-2023)
collection by McAuley Lab.

## License

Released under the [MIT License](LICENSE).