# Benevolent Protocol Spec Sheet

## Purpose

The Benevolent Protocol is a host-resident maintenance and protection runtime.
Its job is to assess local system health, apply conservative and reversible
improvements where safe, identify security issues, and expose operational state
without collecting personal data.

## Non-Negotiable Beliefs

1. Benevolence before capability.
   The protocol must not perform actions that are clearly harmful, coercive,
   irreversible without justification, or unrelated to system benefit.

2. Resource restraint.
   The protocol must stay within mode-aware CPU, memory, disk, and network
   budgets, especially while the user is active or gaming.

3. Consent and opt-out.
   Emergency-stop and opt-out signals must halt autonomous work.

4. Reversibility and auditability.
   Changes should be reversible where practical and violations should be logged.

5. Privacy by default.
   Telemetry must stay anonymized and operational rather than user-identifying.

## Current Standing

As of the current codebase:

- Control components are relatively mature:
  - kill switch
  - heartbeat
  - telemetry
  - signed command parsing
- Profiling and scanners are concrete enough to support a runtime loop.
- The orchestrator exists, but until now it depended on methods that were not
  implemented by the optimizer, safety, and scanner modules.
- The runtime cycle did not yet perform meaningful safe work beyond telemetry.

## Next-Phase Runtime Scope

This phase intentionally excludes propagation or stealth-oriented expansion.
The active focus is a conservative local runtime with four responsibilities:

1. Profile local system state.
2. Generate a minimal optimization plan from measured conditions.
3. Safety-gate each action before execution.
4. Scan security state and summarize results for telemetry and status.

## Runtime Behavior

### Startup

- Load config.
- Initialize modules.
- Profile the local machine once.
- Record one device encounter for telemetry.
- Start heartbeat.

### Main Loop

Each cycle should:

1. Check kill-switch and emergency-stop signals.
2. Refresh operating mode:
   - normal
   - gaming
   - idle
   - stealth
3. In gaming mode:
   - avoid optimizations
   - avoid heavy scans
   - keep only lightweight status updates
4. In normal or idle mode:
   - profile the system
   - derive a conservative optimization plan
   - run only actions approved by behavioral constraints
   - run vulnerability and malware scans on schedule
   - update cycle summary for status and telemetry

### Autonomy Boundaries

The protocol may autonomously:

- profile system state
- clear low-risk caches where supported
- adjust clearly reversible performance settings where supported
- scan for vulnerabilities
- scan for malware
- record anonymized telemetry counters

The protocol must not autonomously:

- modify credentials
- touch critical system files
- exfiltrate data
- delete arbitrary user files
- perform propagation in the default next-phase runtime

## Optimization Contract

The optimizer should expose:

- `create_optimization_plan(profile)`
- `apply_optimization(task)`

An optimization task should carry:

- stable identifier
- human-readable name
- action name
- description
- expected resource impact
- reversibility
- platform requirements

## Safety Contract

The safety layer should expose a boolean gate for planned actions and use:

- forbidden-action checks
- critical-path checks
- mode-aware resource checks
- opt-out and emergency-stop checks

## Status Contract

The orchestrator status output should include:

- running state
- uptime
- current mode
- kill-switch state
- telemetry summary
- heartbeat summary
- last profile summary
- last cycle summary

## Immediate Build Targets

1. Reconcile orchestrator calls with actual module APIs.
2. Implement a real normal-mode cycle.
3. Add direct orchestrator runtime tests.
4. Include orchestrator runtime tests in the Windows validation pipeline.
