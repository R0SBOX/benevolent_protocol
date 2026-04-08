# THE BENEVOLENT PROTOCOL - Project Structure

## Overview

This document describes the repository as it exists now. Earlier versions of this file referred to a different "white paper" driven structure that does not match the current codebase.

## Directory Structure

```text
benevolent_protocol/
├── config/
│   ├── config.json
│   └── config.schema.json
├── deploy/
│   ├── benevolent-protocol.service
│   ├── bootstrap.ps1
│   ├── install.bat
│   ├── install.ps1
│   ├── install-standalone.ps1
│   └── install.sh
├── docs/
│   ├── ANDROID_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── CONCEPT.md
│   ├── DEPLOYMENT.md
│   ├── MODE_DIAGRAM.md
│   ├── PLATFORM_STRATEGY.md
│   ├── PROJECT_STRUCTURE.md
│   ├── PROPAGATION_GUIDE.md
│   └── WINDOWS_GUIDE.md
├── src/
│   ├── analysis/
│   │   └── system_profiler.py
│   ├── control/
│   │   ├── command_receiver.py
│   │   ├── heartbeat_manager.py
│   │   ├── kill_switch.py
│   │   ├── telemetry_sender.py
│   │   └── update_receiver.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py
│   │   └── README.md
│   ├── optimization/
│   │   ├── performance_tuner.py
│   │   ├── windows_bloatware.py
│   │   └── windows_optimizer.py
│   ├── propagation/
│   │   ├── network_scanner.py
│   │   ├── propagation_engine.py
│   │   └── stealth_operations.py
│   ├── protection/
│   │   ├── malware_remover.py
│   │   ├── malware_scanner.py
│   │   ├── security_hardener.py
│   │   └── vulnerability_scanner.py
│   └── safety/
│       └── behavioral_constraints.py
├── tests/
│   ├── test_control.py
│   └── test_integration.py
├── README.md
├── STATUS.md
├── BUILD_REPORT.md
├── requirements.txt
└── top-level exploratory test scripts
```

## Functional Areas

### `src/core`
- Contains the legacy `ProtocolCore` implementation and the newer orchestrator.
- This is the main place where lifecycle integration is intended to happen.

### `src/analysis`
- Contains host profiling logic.

### `src/optimization`
- Contains performance and Windows-focused optimization modules.

### `src/safety`
- Contains the behavioral constraints and mode/resource logic.

### `src/protection`
- Contains vulnerability scanning, malware scanning/removal, and security hardening modules.

### `src/propagation`
- Contains network scanning, propagation, and stealth-related modules.

### `src/control`
- Contains kill switch, command receiver, telemetry, heartbeat, and update modules.

## Notes

- The repository includes both planning-era documents and implementation-era documents.
- Where docs disagree with code, treat the source tree as canonical.
- The current structure does not include the earlier `ethics/`, `trust/`, `implementations/`, or white-paper-specific layout that older docs described.
