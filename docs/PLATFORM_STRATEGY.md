# Platform Strategy - THE BENEVOLENT PROTOCOL

> Status note: this document reflects the current repository strategy as represented by code and adjacent docs. It distinguishes between implemented policy, partial implementation, and design intent.

## Overview

The repository currently expresses platform strategy in three places:
- `src/safety/behavioral_constraints.py`
- Windows-focused modules in `src/optimization/`
- design-oriented platform docs, especially for Android

The actual strategy is therefore uneven:
- Windows has the strongest implementation presence
- Linux has explicit policy logic in code
- Android and macOS are mostly design intent in the current repository

## Current Platform Posture

| Platform | Repository Posture | Current Reality |
|----------|--------------------|-----------------|
| Windows | Primary implementation target | Concrete optimization modules exist |
| Linux | Restricted / consent-gated | Safety policy exists in code |
| macOS | Limited / conceptual | Mentioned in docs, little concrete implementation in tree |
| Android | Design target | Guide exists, referenced implementation is not present |

## Windows

### Current Status

Windows is the platform with the clearest implementation footprint in the repo.

Concrete modules:
- `src/optimization/windows_bloatware.py`
- `src/optimization/windows_optimizer.py`

Orchestrator integration:
- the orchestrator initializes Windows-specific modules
- it exposes helper workflows for bloatware removal
- Windows-specific behavior is present, but full end-to-end runtime usage remains partial

### Implemented Strategy

The repository currently supports a Windows-first optimization posture through:
- bloatware scanning/removal
- Windows tuning and privacy-oriented optimizations
- security hardening support through protection/control modules

### Limits

The repo should not currently be described as a verified Windows deployment product:
- orchestrator loop behavior is still skeletal
- integration depth is uneven
- platform modules exist, but production-readiness is not established

## Linux

### Current Status

Linux policy is one of the more explicit cross-platform decisions represented in code.

In `src/safety/behavioral_constraints.py`:
- `is_linux()` checks platform type
- `should_infect()` returns consent-gated behavior for Linux
- `_has_explicit_user_consent()` checks for explicit consent files

### Effective Policy

Current coded intent:
- Linux should not be treated like a default active target
- explicit user consent is required before proceeding

This is the clearest expression of platform restraint in the repository.

### Practical Interpretation

Compared with Windows:
- Linux has policy logic
- Linux does not have a similarly concrete Linux-specific optimization/control layer wired through the runtime
- the project should be described as Linux-restricted rather than Linux-supported in the same sense as Windows

## macOS

### Current Status

macOS appears in project messaging and platform tables, but the repository does not currently contain a dedicated macOS module set comparable to Windows.

Practical interpretation:
- macOS is a design target, not a strongly implemented platform in this repo

### Strategy Statement

The most accurate current statement is:
- intended limited support
- constrained by platform restrictions
- not materially represented by concrete implementation in the tree

## Android

### Current Status

Android remains a documented design target, not a present implementation in the repository.

Current evidence:
- `docs/ANDROID_GUIDE.md` describes Android support as planned/design-oriented
- the repository does not currently include `src/optimization/android_optimizer.py`
- the repository does not currently include `test_android.py`

### Strategy Statement

The repo should describe Android as:
- planned support area
- design guidance exists
- implementation is not currently present in the source tree

## Gaming Mode

### Current Status

Gaming mode is partially implemented and is one of the more concrete behavior strategies in the repo.

Implemented or represented in code:
- `OperationMode` includes `GAMING`, `IDLE`, `STEALTH`, and `NORMAL`
- `BehavioralConstraints` contains gaming-related resource limits
- `detect_gaming_mode()` checks process names and attempts GPU/fullscreen heuristics
- `get_current_mode()` prioritizes gaming, idle, stealth, then normal
- the orchestrator checks `detect_gaming_mode()` and branches between gaming and normal cycles

### What Is Real Today

Current coded behavior supports these claims:
- gaming is intended to be the highest-priority low-impact mode
- gaming mode resource limits are stricter than normal mode
- the orchestrator is aware of gaming mode

### What Is Not Yet Fully Realized

The repo should not currently claim all gaming-mode behavior described in earlier docs:
- no validated system tray integration
- no implemented manual mode-file override path in the current safety module
- no fully realized transition manager in the runtime
- orchestrator gaming-cycle behavior is still stubbed

### Practical Strategy

The accurate current summary is:
- gaming mode exists conceptually and partially in code
- low-impact intent is real
- full runtime behavior is not yet complete

## Resource Management Strategy

### Current Coded Modes

The safety module defines these operational modes:
- `NORMAL`
- `GAMING`
- `IDLE`
- `STEALTH`
- `AGGRESSIVE`

Current resource-limit strategy in code includes:
- normal limits
- stricter gaming limits
- more permissive idle limits

Battery-aware behavior is partially represented through `_is_battery_saver()`, which influences `STEALTH` mode selection.

### Important Caveat

The orchestrator currently does not fully operationalize all mode behaviors:
- it checks for gaming mode
- it does not yet execute a rich differentiated workload per mode
- `current_mode` handling is not yet fully synchronized with the detection helpers

## Platform Priorities

### Accurate Current Priority Order

1. Windows
Current implementation emphasis is strongest here.

2. Linux policy / safety handling
There is explicit code-driven behavior, but not comparable active-platform implementation.

3. macOS and Android as design targets
They remain mostly documentary or conceptual in the current repository.

## What Earlier Docs Overclaimed

Earlier strategy language implied:
- complete Windows behavior orchestration
- implemented Android support
- implemented UI/system tray controls
- mature mode-transition management
- broader platform completeness than the tree currently supports

Those claims should now be treated as design intent rather than current platform strategy.

## Recommended Wording For The Repo

If the project needs a short platform statement, use something close to:

```text
Windows is the primary implementation target in the current repository.
Linux behavior is explicitly restricted and consent-gated.
Gaming mode and resource-aware behavior are partially implemented.
macOS and Android remain design targets with limited or absent concrete implementation.
```

## Near-Term Cleanup / Follow-Up

1. Align `README.md` platform claims with this document
2. Audit `docs/WINDOWS_GUIDE.md` for aspirational features that are not in code
3. Keep Android references clearly marked as planned support
4. Decide whether Linux is a carrier, a consent-only local install target, or both
5. Reconcile `current_mode` state management in the orchestrator with the detection logic in safety

---

**Platform Strategy Status:** Mixed implementation with clear Windows emphasis
**Most Concrete Policy In Code:** Linux consent gating and gaming/resource limits
