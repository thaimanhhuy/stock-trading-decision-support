# Codebase Exploration - Documentation Index

This exploration has created three comprehensive documents to help you understand the Stock Trading Decision Support System:

## Documentation Files

### 1. **CODEBASE_EXPLORATION.md** (31 KB)
   **Purpose**: Complete deep-dive exploration of the entire system
   
   **Covers**:
   - Project overview and structure
   - How models are trained (detailed pipeline)
   - Where models are stored (persistence)
   - How data is fetched (Yahoo Finance integration)
   - Backend framework and API endpoints
   - Current model types (LSTM, GRU, ensemble)
   - Technical indicators used
   - Data flow diagrams
   - Configuration files summary
   - Key dependencies
   - Key classes and methods
   - Testing structure
   - Entry points and deployment options
   
   **Best for**: Understanding the complete system architecture and implementation details

### 2. **QUICK_REFERENCE.md** (9 KB)
   **Purpose**: Fast lookup guide for common tasks
   
   **Contains**:
   - Quick command reference
   - File locations map
   - Configuration files map
   - Model architecture diagrams
   - API endpoints reference
   - Key classes and methods tables
   - Technical indicators list
   - Directory structure
   - Development setup
   - Common workflows
   - Troubleshooting guide
   - Parameter tuning guide
   
   **Best for**: Day-to-day development and quick lookups

### 3. **ARCHITECTURE.md** (36 KB)
   **Purpose**: Visual system architecture and design overview
   
   **Contains**:
   - High-level ASCII architecture diagrams
   - Data flow diagrams
   - Component dependency maps
   - Configuration hierarchy
   - Storage architecture
   - Model selection and deployment flow
   - Performance characteristics
   - Scalability considerations
   - Layer-by-layer breakdown
   
   **Best for**: Understanding system design and how components interact

---

## Quick Navigation

### For Different Use Cases:

#### "I want to understand how models are trained"
Start with: **CODEBASE_EXPLORATION.md** → Section 3 "HOW MODELS ARE TRAINED"
Quick ref: **QUICK_REFERENCE.md** → Section "Model Training Architecture"

#### "I want to use the API"
Start with: **CODEBASE_EXPLORATION.md** → Section 6 "API ENDPOINTS"
Quick ref: **QUICK_REFERENCE.md** → Section "API Endpoints"

#### "I want to train a model on a new stock"
Start with: **QUICK_REFERENCE.md** → Section "Common Workflows" → "Workflow 1"
Details: **CODEBASE_EXPLORATION.md** → Sections 3 & 5

#### "I want to understand the overall system"
Start with: **ARCHITECTURE.md** → "High-Level Architecture"
Then: **CODEBASE_EXPLORATION.md** → Section 1 & 2

#### "I'm debugging a problem"
Start with: **QUICK_REFERENCE.md** → Section "Troubleshooting"
Details: **CODEBASE_EXPLORATION.md** → Relevant section

#### "I want to modify the system"
Start with: **ARCHITECTURE.md** → "Component Dependencies"
Then: **CODEBASE_EXPLORATION.md** → Sections 12 "Key Classes & Methods"

---

## Key File Locations Summary

### Training
- **Entry Point**: `scripts/train_models.py`
- **Models**: `src/models/lstm_model.py`, `src/models/gru_model.py`
- **Data Fetcher**: `src/data_ingestion/yahoo_fetcher.py`
- **Data Processor**: `src/preprocessing/data_processor.py`

### API & Predictions
- **API Server**: `src/api/main.py`
- **Signal Generation**: `src/trading_engine/signal_generator.py`
- **Model Evaluator**: `src/models/model_evaluator.py`

### Configuration
- **Main Config**: `config/config.yaml`
- **Model Config**: `config/model_config.yaml`
- **Trading Config**: `config/trading_config.yaml`
- **Settings**: `src/config/settings.py`

### Storage
- **Raw Data**: `data/raw/{symbol}.csv`
- **Trained Models**: `models/saved_models/{symbol}.keras`
- **Scalers**: `models/scalers/{symbol}_scaler.pkl`

---

## System Overview (One Pager)

```
DATA SOURCE (Yahoo Finance)
        ↓
DOWNLOAD & VALIDATE (download_historical_data.py)
        ↓
PREPROCESSING (Add indicators, normalize, create sequences)
        ↓
MODEL TRAINING (LSTM + GRU, saved to models/saved_models/)
        ↓
API SERVER (FastAPI at /api/v1/)
        ↓
PREDICTIONS & SIGNALS (/predictions/, /signals/ endpoints)
        ↓
RISK MANAGEMENT & TRADING SIGNALS (Buy/Sell/Hold)
```

---

## Current Implementation Status

### Implemented
✓ LSTM model for price prediction
✓ GRU model for price prediction
✓ Model ensemble (weighted average)
✓ FastAPI REST API
✓ Technical indicators (SMA, EMA, RSI, MACD, Bollinger Bands, ATR)
✓ Data normalization and scaling
✓ Model persistence (SavedModel format)
✓ Backtesting engine
✓ Risk management (stop-loss, take-profit)
✓ Drift detection
✓ Vietnamese stock support
✓ Comprehensive logging

### Future Enhancements (Configured but Disabled)
□ Transformer models
□ Hyperparameter tuning
□ Distributed training
□ Real-time data streaming
□ Model registry
□ Advanced monitoring

---

## Key Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Training Data Window | 60 days | Configurable in config |
| Model Types | 2 | LSTM + GRU |
| Ensemble Method | Weighted average | 0.5 weight each |
| Sequence-to-Sequence | 1-to-1 | Predicts 1 day ahead |
| Normalization | MinMaxScaler | 0-1 range |
| Supported Markets | 2 | US stocks + Vietnamese stocks |
| API Framework | FastAPI | With Uvicorn server |
| Supported Stock Symbols | Unlimited | Yahoo Finance compatible |

---

## Testing the System

### Quick Start Test
```bash
# 1. Download data
python scripts/download_historical_data.py --symbols AAPL --period 2y

# 2. Train models
python scripts/train_models.py --symbol AAPL --models all

# 3. Start API
python -m src.api.main

# 4. Test predictions
curl http://localhost:8000/api/v1/predictions/AAPL
curl http://localhost:8000/api/v1/signals/AAPL
```

---

## Documentation Structure

```
CODEBASE_EXPLORATION.md (THIS IS THE MAIN DOCUMENT)
├── 1. Project Overview
├── 2. Project Structure
├── 3. How Models Are Trained ⭐ CRITICAL
├── 4. Where Models Are Stored ⭐ CRITICAL
├── 5. How Data Is Fetched ⭐ CRITICAL
├── 6. Backend Framework & API ⭐ CRITICAL
├── 7. Current Model Types ⭐ CRITICAL
├── 8. Technical Indicators
├── 9. Data Flow Diagram
├── 10. Configuration Files
├── 11. Key Dependencies
├── 12. Key Classes & Methods
├── 13. Testing
├── 14. Entry Points
└── 15. Deployment Options

QUICK_REFERENCE.md (USE FOR DAY-TO-DAY WORK)
├── Quick Command Reference
├── File Locations Map
├── Configuration Files Map
├── Model Training Architecture
├── API Endpoints
├── Key Classes & Methods
├── Technical Indicators
├── Directory Structure
├── Development Setup
├── Common Workflows
├── Troubleshooting
└── Key Parameters to Tune

ARCHITECTURE.md (USE FOR DESIGN UNDERSTANDING)
├── High-Level Architecture (ASCII diagram)
├── Data Flow: Training to Prediction
├── Component Dependencies
├── Configuration Hierarchy
├── Storage Architecture
├── Model Selection & Deployment
├── Performance Characteristics
└── Scalability Considerations
```

---

## Critical Sections Reference

### If you need to:

1. **Train a model**
   - CODEBASE_EXPLORATION.md Section 3
   - QUICK_REFERENCE.md "Model Training Architecture"
   - ARCHITECTURE.md "Data Flow: Training to Prediction"

2. **Get predictions from API**
   - CODEBASE_EXPLORATION.md Section 6.3
   - QUICK_REFERENCE.md "API Endpoints"
   - ARCHITECTURE.md "API & SERVICE LAYER"

3. **Understand data flow**
   - CODEBASE_EXPLORATION.md Section 9
   - ARCHITECTURE.md "Data Flow: Training to Prediction"

4. **Find a specific class or method**
   - CODEBASE_EXPLORATION.md Section 12
   - QUICK_REFERENCE.md "Key Classes & Methods"

5. **Configure the system**
   - CODEBASE_EXPLORATION.md Section 10
   - QUICK_REFERENCE.md "Configuration Files Map"
   - CONFIGURATION.md (existing in project)

6. **Deploy the system**
   - CODEBASE_EXPLORATION.md Section 15
   - DOCKER_DEPLOYMENT.md (existing in project)
   - HEROKU_DEPLOYMENT.md (existing in project)

---

## Files Examined During Exploration

### Scripts
- ✓ scripts/train_models.py
- ✓ scripts/download_historical_data.py
- ✓ scripts/run_backtest.py
- ✓ scripts/test_vietnamese_stocks.py

### Core Modules (src/)
- ✓ src/api/main.py
- ✓ src/models/base_model.py
- ✓ src/models/lstm_model.py
- ✓ src/models/gru_model.py
- ✓ src/models/model_trainer.py
- ✓ src/models/model_evaluator.py
- ✓ src/data_ingestion/yahoo_fetcher.py
- ✓ src/data_ingestion/data_storage.py
- ✓ src/preprocessing/data_processor.py
- ✓ src/preprocessing/sliding_window.py
- ✓ src/preprocessing/technical_indicators.py
- ✓ src/trading_engine/signal_generator.py
- ✓ src/config/settings.py

### Configuration
- ✓ config/config.yaml
- ✓ config/model_config.yaml
- ✓ config/trading_config.yaml
- ✓ config/logging_config.yaml
- ✓ config/vietnam_stocks.yaml

### Project Files
- ✓ setup.py
- ✓ requirements.txt
- ✓ README.md

---

## Next Steps

1. **Read** CODEBASE_EXPLORATION.md for comprehensive understanding
2. **Reference** QUICK_REFERENCE.md for specific tasks
3. **Study** ARCHITECTURE.md for system design insights
4. **Start** with Quick Start Test in Testing section
5. **Explore** the actual code files with understanding of system flow

---

## Questions This Documentation Answers

- How do I train a model on a new stock?
- Where are trained models stored?
- How does the API work?
- What models are being used?
- How is data fetched and preprocessed?
- How do I get predictions?
- What's the system architecture?
- How are technical indicators calculated?
- Where is configuration managed?
- How do I deploy this system?

---

**Created**: November 19, 2025
**System Version**: 0.1.0
**Documentation Scope**: Complete codebase exploration and analysis

