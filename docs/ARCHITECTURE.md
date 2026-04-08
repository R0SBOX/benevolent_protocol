# Technical Architecture - THE BENEVOLENT PROTOCOL

> Status note: this document reflects the current repository architecture. It separates implemented modules, partial integration, and design intent. Earlier versions described a broader target architecture that did not match the source tree.

## System Overview

The repository currently has two architectural layers:

1. A legacy core scaffold in `src/core/__init__.py`
2. A newer orchestrator in `src/core/orchestrator.py` that initializes most modules and provides the practical top-level runtime entry point

The codebase is therefore best understood as a partially integrated prototype rather than a completed runtime.

```text
┌─────────────────────────────────────────────────────────────┐
│                    BENEVOLENT PROTOCOL                     │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                Core Orchestrator Layer                │  │
│  │  - legacy ProtocolCore scaffold                       │  │
│  │  - newer BenevolentProtocol orchestrator              │  │
│  └───────────────────────────────────────────────────────┘  │
│              ↓                 ↓                 ↓          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   ANALYSIS   │  │    SAFETY    │  │   CONTROL    │      │
│  │ system_prof. │  │ constraints  │  │ kill/telem.  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│              ↓                 ↓                 ↓          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ OPTIMIZATION │  │ PROTECTION   │  │ PROPAGATION  │      │
│  │ tuner/winopt │  │ vuln/malware │  │ scan/spread  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Current Runtime Architecture

### 1. Legacy Core (`src/core/__init__.py`)

Purpose:
- Defines `ProtocolCore` / `BenevolentProtocol`
- Provides basic lifecycle methods such as `initialize()`, `run()`, and `shutdown()`

Current state:
- still contains major `TODO` sections for safety verification, subsystem initialization, and protocol-cycle behavior
- useful as a scaffold, not as the primary integrated runtime

### 2. Orchestrator (`src/core/orchestrator.py`)

Purpose:
- initializes the main modules across the repository
- loads configuration
- starts heartbeat
- profiles the host
- exposes helper methods such as optimization, vulnerability scanning, malware scanning, and security hardening

Current state:
- module wiring is present
- start/stop lifecycle is implemented
- the main loop exists
- gaming and normal cycles are still skeletal

In practice, this file is the closest thing to the current top-level runtime entry point.

## Module Map

### Core (`src/core/`)

Files:
- `__init__.py`
- `orchestrator.py`
- `README.md`

Responsibilities:
- lifecycle management
- top-level configuration loading
- coordination of other modules
- protocol status reporting

### Analysis (`src/analysis/`)

Files:
- `system_profiler.py`

Responsibilities:
- hardware/software profiling
- system inventory
- runtime environment inspection

Integration status:
- directly used by the orchestrator

### Optimization (`src/optimization/`)

Files:
- `performance_tuner.py`
- `windows_bloatware.py`
- `windows_optimizer.py`

Responsibilities:
- performance tuning
- Windows-specific bloatware removal
- Windows system optimization

Integration status:
- instantiated by the orchestrator
- helper methods exist to run optimization and Windows bloatware workflows
- end-to-end safety/integration depth should still be treated as partial

### Safety (`src/safety/`)

Files:
- `behavioral_constraints.py`

Responsibilities:
- forbidden-action checks
- resource limits
- opt-out detection
- emergency stop checks
- operating mode selection and gaming detection

Integration status:
- one of the more concrete modules in the repository
- directly referenced by the orchestrator

Notes:
- some code paths need maintenance, for example shell/subprocess helpers inside gaming or idle detection paths

### Protection (`src/protection/`)

Files:
- `security_hardener.py`
- `vulnerability_scanner.py`
- `malware_scanner.py`
- `malware_remover.py`

Responsibilities:
- vulnerability scanning
- security hardening
- malware detection and cleanup

Integration status:
- orchestrator exposes helper methods that call these modules
- runtime sequencing is present at the API level, not fully realized in the loop behavior

### Propagation (`src/propagation/`)

Files:
- `network_scanner.py`
- `propagation_engine.py`
- `stealth_operations.py`

Responsibilities:
- network discovery
- propagation logic
- stealth/evasion behavior

Integration status:
- modules are instantiated by the orchestrator
- continuous, validated end-to-end propagation flow is not currently represented by the main loop

### Control (`src/control/`)

Files:
- `kill_switch.py`
- `command_receiver.py`
- `telemetry_sender.py`
- `heartbeat_manager.py`
- `update_receiver.py`

Responsibilities:
- emergency deactivation
- command parsing/execution
- telemetry and status reporting
- heartbeat/liveness
- update handling

Integration status:
- these modules are among the most directly testable parts of the repo
- kill switch hooks and heartbeat startup are wired into the orchestrator

## Current Data Flow

The intended end-to-end architecture is broader than the runtime that currently executes. The actual high-level flow today is closer to this:

```text
1. LOAD CONFIGURATION
   ↓
2. INITIALIZE MODULE INSTANCES
   ↓
3. PROFILE CURRENT SYSTEM
   ↓
4. START HEARTBEAT
   ↓
5. ENTER MAIN LOOP
   ↓
6. CHECK KILL SWITCH
   ↓
7. DETECT GAMING / NORMAL MODE
   ↓
8. RUN LIGHTWEIGHT CYCLE LOGIC
   ↓
9. EXPOSE HELPER METHODS FOR:
   - optimization
   - vulnerability scanning
   - malware scanning
   - security hardening
```

The older aspirational flow included payload delivery, persistence establishment, full spread, and continuous monitoring. Those concepts remain part of project intent, but they are not the best description of the current runtime.

## Configuration Architecture

Current behavior:
- the orchestrator defaults to `/etc/benevolent_protocol/config.json`
- if the file exists, it merges that file into internal defaults

Observed default areas:
- telemetry
- heartbeat interval
- optimization interval
- propagation enable/disable flag
- gaming mode toggle
- resource limits
- control secret

The repository does not currently document or implement a verified CLI/config discovery layer beyond constructor-based path injection and the default config path.

## Testing Architecture

Current test shape:
- `tests/test_control.py` focuses on kill switch, command receiver, telemetry, heartbeat, and update behavior
- `tests/test_integration.py` focuses on interactions among control-related modules
- several top-level test scripts exist for exploratory or platform-specific module checks

Important limitation:
- async tests currently rely on `pytest.mark.asyncio`, but async pytest support is not configured in the present environment by default

## Technology Stack

### Primary Language
- Python 3.10+

### Libraries Referenced In Current Code
- `asyncio`
- `psutil`
- `json`
- standard-library logging, signal, pathlib, dataclasses, enum, datetime

### Documentation vs. Code Note

Earlier architecture text referenced Rust, Go, and multiple modules such as:
- `vulnerability_detector.py`
- `payload_delivery.py`
- `persistence_manager.py`
- `performance_analyzer.py`
- `security_auditor.py`
- `rollback_manager.py`

Those files are not part of the current repository and should be treated as design intent rather than present architecture.

## Architectural Risks / Gaps

1. Dual-core architecture
The repository currently has both a legacy core scaffold and a newer orchestrator, which creates ambiguity about the real entry point.

2. Partial loop behavior
The orchestrator initializes many subsystems, but the main loop does not yet exercise most of them.

3. Documentation drift
Several planning-era documents still describe the target system rather than the current implementation.

4. Test environment assumptions
The async test suite assumes pytest async support that may not be configured in all environments.

## Recommended Near-Term Direction

1. Treat `src/core/orchestrator.py` as the canonical runtime entry point
2. Decide whether to merge or retire the legacy `ProtocolCore`
3. Align orchestrator method calls with verified module APIs
4. Move aspirational architecture into a separate "target architecture" document if needed
5. Keep this document limited to the architecture that exists in the repository

---

**Architecture Status:** Partially implemented, partially integrated
**Best Current Entry Point:** `src/core/orchestrator.py`
