# Windows Usage Guide - THE BENEVOLENT PROTOCOL

> Status note: this guide reflects the current repository state. Windows is the strongest implementation area in the repo, but the project should still be treated as a prototype rather than a verified end-to-end Windows product.

## Overview

Windows has the most concrete platform support in the current codebase.

Relevant modules:
- `src/optimization/windows_bloatware.py`
- `src/optimization/windows_optimizer.py`
- `src/core/orchestrator.py`
- `src/safety/behavioral_constraints.py`

What this means in practice:
- Windows-specific optimization modules exist
- the orchestrator initializes those modules
- helper workflows for scanning and optimization are present
- the main runtime loop is still only partially realized

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Inspect The System

```bash
# Profile the host
python src/analysis/system_profiler.py

# Exercise Windows-focused tooling
python test_windows_tools.py
```

### 3. Run The Current Orchestrator

```bash
python -m src.core.orchestrator
```

This currently gives you:
- configuration loading
- module initialization
- initial system profiling
- heartbeat startup
- a partial main loop

It does not yet represent a fully realized Windows operations pipeline.

## Windows-Specific Modules

### Bloatware Removal

Primary module:
- `src/optimization/windows_bloatware.py`

Current intended usage pattern:

```python
from src.optimization.windows_bloatware import WindowsBloatwareRemover

remover = WindowsBloatwareRemover()
installed = remover.scan_installed_bloatware()

for item in installed:
    print(item.name, item.safe_to_remove)
```

The repository presents this module as one of the more concrete Windows-specific features.

Important caveat:
- treat removal operations carefully and review detected applications before applying destructive changes

### Windows Optimization

Primary module:
- `src/optimization/windows_optimizer.py`

Current intended usage pattern:

```python
from src.optimization.windows_optimizer import WindowsSystemOptimizer

optimizer = WindowsSystemOptimizer()

for opt in optimizer.optimizations:
    print(opt.name, opt.category, opt.impact)
```

Practical interpretation:
- the optimizer module exists and contains Windows-specific actions
- repository docs should not overstate those actions as fully validated across production Windows environments

## Bloatware Strategy

The repository’s Windows bloatware support is aimed at common preinstalled or low-value applications.

Representative categories in the current code/docs:
- games and trialware
- consumer apps
- optional Microsoft utilities
- nonessential tooling

Use the module as a scanner first.

Recommended workflow:
1. scan installed items
2. review `safe_to_remove`
3. remove selectively
4. verify outcome manually

## Optimization Strategy

The Windows optimizer module is aimed at areas such as:
- service configuration
- privacy settings
- visual effects
- system behavior tuning
- security-related settings

The exact set of optimizations should be taken from the code, not from older high-level docs.

Recommended workflow:
1. inspect optimizer entries
2. review impact and rollback data
3. apply selectively
4. verify whether restart is required

## Gaming Mode

### Current Status

Gaming mode is partially implemented in the repository.

What is represented in code:
- gaming-related resource limits in `BehavioralConstraints`
- process-based gaming detection
- additional GPU/fullscreen heuristics
- orchestrator branching between gaming and non-gaming cycles

What is not fully realized:
- a complete transition manager
- validated manual override behavior via mode files
- a fully implemented gaming workload policy in the orchestrator loop

### Accurate Current Claim

The safest current description is:
- Windows gaming awareness exists
- low-impact intent is encoded
- full runtime gaming behavior is still partial

### Resource Limits

The safety module defines stricter gaming-mode limits than normal-mode limits, including:
- CPU reduction
- reduced memory budget
- lower network budget
- minimal disk activity intent

Those limits are part of the policy layer. The main loop does not yet fully operationalize every behavior implied by that policy.

## Linux Policy In The Windows Context

This Windows guide previously mixed in strong claims about Linux behavior.

The current repository position is:
- Linux behavior is consent-gated in `src/safety/behavioral_constraints.py`
- Linux should not be described here as a Windows feature
- platform-wide policy belongs primarily in `docs/PLATFORM_STRATEGY.md`

See:
- [PLATFORM_STRATEGY.md](/home/r0s/projects/benevolent_protocol/docs/PLATFORM_STRATEGY.md)

## Advanced Usage

### Orchestrator Helper Methods

The orchestrator exposes helper workflows such as:
- `optimize_system()`
- `remove_bloatware()`
- `scan_vulnerabilities()`
- `scan_malware()`
- `harden_security()`

That makes it useful as a convenience integration point even though the main loop remains partial.

### Example

```python
import asyncio
from src.core.orchestrator import BenevolentProtocol

async def main():
    protocol = BenevolentProtocol()

    results = await protocol.optimize_system()
    print(results)

asyncio.run(main())
```

Important caveat:
- helper methods depend on cross-module API compatibility and should still be treated as prototype behavior

## Expected Results

The older guide gave precise improvement percentages. Those numbers are not currently verified by this repository alone.

A more accurate expectation is:
- you can inspect Windows-specific optimization definitions
- you can scan for bloatware candidates
- you can exercise Windows modules directly
- you should validate system-specific results manually

## Safety Notes

Before making Windows changes:
1. review optimizer entries and removal candidates
2. ensure you understand rollback coverage
3. prefer testing in a disposable or recoverable environment first
4. do not assume all documented behavior is production-hardened

## Testing

Current relevant test entry points:

```bash
python test_windows_tools.py
python test_gaming_mode.py
pytest tests/test_control.py
pytest tests/test_integration.py
```

Important limitation:
- async pytest support may need to be configured in the environment before all test files pass cleanly

## Summary

The most accurate current Windows summary is:
- Windows is the strongest implementation area in the repository
- Windows-specific optimizer and bloatware modules exist
- gaming-aware and safety-aware policy exists
- the orchestrator integrates these pieces only partially today

If you need exact behavior, use the source files as the canonical reference:
- `src/optimization/windows_bloatware.py`
- `src/optimization/windows_optimizer.py`
- `src/safety/behavioral_constraints.py`
- `src/core/orchestrator.py`

---

**Windows Guide Status:** Updated to match current repository state
**Best Windows Entry Point:** `src/core/orchestrator.py` plus direct Windows module inspection
