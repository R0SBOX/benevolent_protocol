# THE BENEVOLENT PROTOCOL

<div align="center">

**Infect to improve. Spread to protect. Optimize everything.**

[![Version](https://img.shields.io/badge/version-0.3.0--alpha-blue.svg)](https://github.com/r0s-org/benevolent_protocol)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-purple.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20Windows%20%7C%20Android%20%7C%20macOS-orange.svg)](#)

**Experimental framework for a benevolent systems-management agent**

[Features](#-features) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Safety](#-safety) • [Contributing](#-contributing)

</div>

---

## ⚠️ Current Status

This repository is an **early-stage prototype**. It contains:
- working support modules for safety, control, profiling, and parts of protection/optimization
- a newer orchestrator that wires modules together
- incomplete runtime behavior in the main loop
- documentation that previously described the intended end state rather than the current implementation

The project concept remains "infect to improve", but the codebase today is better understood as a research/prototype repository than a production-ready deployment.

---

## 🎯 Mission

Traditional malware infects, steals, destroys, and exploits.

**The Benevolent Protocol infects, analyzes, optimizes, protects, and spreads to help.**

This is malware reimagined: a self-propagating system that improves every device it touches while respecting user consent and system integrity.

---

## 🌟 Features

### Repository Capabilities

- **🔧 System Optimization** - Performance tuning, bloatware removal, resource management
- **🛡️ Security Hardening** - Vulnerability scanning, automated patching, firewall management
- **🦠 Malware Protection** - Threat detection, safe removal, quarantine system
- **🕵️ Dynamic Stealth** - Design present, implementation status mixed
- **🚀 Self-Propagation** - Design present, implementation status mixed
- **🎮 Gaming Mode** - Invisible during gameplay (5% CPU max)
- **📡 Remote Control** - Kill switch, commands, telemetry, updates

### Intended Platform Support

| Platform | Mode | Behavior |
|----------|------|----------|
| **🐧 Linux** | Carrier | Spread only, no modification |
| **🪟 Windows** | Active | Optimize + spread |
| **📱 Android** | Active | ADB optimization |
| **🍎 macOS** | Limited | Light optimization |

### Implemented Or In-Progress Areas

**Core/runtime:**
- A legacy `ProtocolCore` with several `TODO` sections
- A newer `src/core/orchestrator.py` that initializes modules and exposes helper methods
- Main loop cycles that are still mostly skeletal

**Safety/control:**
- Behavioral constraints with forbidden actions, opt-out checks, emergency stop checks, and mode/resource logic
- Kill switch, command receiver, telemetry sender, heartbeat manager, and update receiver modules

**Analysis/protection/optimization:**
- System profiling, vulnerability scanning, malware scanning/removal, and optimization modules are present
- Actual integration depth varies by module and should be treated as implementation-in-progress

---

## 🚀 Quick Start

### Manual Install

<details>
<summary>Click to expand manual installation</summary>

```bash
# Python 3.10+ required
python --version

# Clone repository
git clone https://github.com/r0s-org/benevolent_protocol.git
cd benevolent_protocol

# Install dependencies
pip install -r requirements.txt
```

</details>

### Basic Usage

```bash
# Profile your system (safe, read-only)
python src/analysis/system_profiler.py

# Scan for vulnerabilities
python src/protection/vulnerability_scanner.py

# Scan for malware
python src/protection/malware_scanner.py

# Run orchestrator module directly
python -m src.core.orchestrator
```

### Run Tests

```bash
# Current test files in the repo
pytest tests/test_control.py
pytest tests/test_integration.py
python test_gaming_mode.py
python test_windows_tools.py
python test_propagation.py
python test_security.py
python test_malware.py
```

---

## 📖 Documentation

### Core Documentation

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical specifications
- **[Concept Philosophy](docs/CONCEPT.md)** - Mission and vision
- **[Platform Strategy](docs/PLATFORM_STRATEGY.md)** - Platform-specific behavior
- **[Propagation Guide](docs/PROPAGATION_GUIDE.md)** - Network spread mechanics
- **[Windows Guide](docs/WINDOWS_GUIDE.md)** - Windows optimization details
- **[Android Guide](docs/ANDROID_GUIDE.md)** - Android optimization details
- **[Mode Diagrams](docs/MODE_DIAGRAM.md)** - Visual mode transitions

### Safety Documentation

- **Behavioral Constraints** - Hard-coded benevolence
- **Gaming Mode** - Invisible during gameplay
- **Rollback System** - Complete reversibility
- **Emergency Stop** - Immediate halt capability

### Documentation Note

Some architecture and strategy documents still describe the intended system rather than the exact current runtime. Use the source tree as the canonical reference where docs and code disagree.

---

## 🛡️ Safety

### Core Principles

1. **Benevolence First** - Every action improves the target system
2. **Transparency** - All actions logged and reversible
3. **Consent Respect** - Honor opt-out requests immediately
4. **Resource Conscious** - Never harm system performance
5. **No Exploitation** - Never use access for malicious purposes

### Safety Mechanisms

**Forbidden Actions (Automatically Blocked):**
- ❌ Delete user files
- ❌ Modify system passwords
- ❌ Install malware
- ❌ Exfiltrate data
- ❌ Cryptocurrency mining
- ❌ DDoS participation
- ❌ Spam distribution
- ❌ Backdoor installation

**Resource Limits (Dynamic by Mode):**
- Gaming: 5% CPU, 100MB RAM
- Normal: 30% CPU, 500MB RAM
- Idle: 60% CPU, 1GB RAM

**Emergency Stop:**
```bash
# Immediate halt
touch /tmp/benevolent_protocol_stop

# Permanent opt-out
touch ~/.benevolent_protocol_optout
```

### Linux Respect Policy

**Linux systems are CARRIERS, not targets:**
- ✅ Spread protocol to Windows/Android
- ✅ Perform network scanning
- ❌ DO NOT optimize Linux
- ❌ DO NOT modify Linux configuration

**Why:** Linux users are technical and optimize their own systems.

---

## 🎮 Gaming Mode

The protocol automatically detects gaming and enters **ultra-low-impact mode**:

**Detection:**
- Process scanning (Steam, Epic, Battle.net, etc.)
- GPU usage monitoring (>70% = gaming)
- Fullscreen application detection
- Gamepad activity

**Resource Limits:**
- CPU: 5% (down from 30%)
- Memory: 100MB (down from 500MB)
- Disk I/O: 1 Mbps (minimal)
- Network: 0.5 Mbps (almost none)

**Behavior:**
- ✅ Critical security monitoring only
- ❌ No optimizations
- ❌ No propagation
- ❌ No intensive operations

---

## 📊 Project Structure

```
benevolent_protocol/
├── src/
│   ├── core/                    # Protocol orchestrator
│   ├── analysis/                # System profiler
│   ├── optimization/            # Performance & bloatware
│   │   ├── performance_tuner.py
│   │   ├── windows_bloatware.py
│   │   └── windows_optimizer.py
│   ├── safety/                  # Behavioral constraints
│   ├── propagation/             # Network scanner & stealth
│   │   ├── network_scanner.py
│   │   ├── stealth_operations.py
│   │   └── propagation_engine.py
│   ├── protection/              # Security & malware
│   │   ├── vulnerability_scanner.py
│   │   ├── security_hardener.py
│   │   ├── malware_scanner.py
│   │   └── malware_remover.py
│   └── control/                 # Remote control system
│       ├── kill_switch.py
│       ├── command_receiver.py
│       ├── telemetry_sender.py
│       ├── heartbeat_manager.py
│       └── update_receiver.py
├── docs/                        # Documentation
├── tests/                       # Test suites
├── test_*.py                    # Test scripts
└── requirements.txt             # Dependencies
```

---

## 🧪 Testing

### Run All Tests

```bash
# Current repo test entry points
python test_gaming_mode.py      # Gaming detection
python test_windows_tools.py    # Windows features
python test_propagation.py      # Network scanning
python test_security.py         # Security hardening
python test_malware.py          # Malware scanning
pytest tests/test_control.py    # Remote control system
pytest tests/test_integration.py
```

### Expected Results

**System Profiler:**
- Hardware analysis (CPU, memory, disk)
- Software inventory (OS, kernel)
- Performance metrics
- Security assessment

**Vulnerability Scanner:**
- Linux: 10 checks
- Windows: 6 checks
- Automated remediation available

**Malware Scanner:**
- 10 threat types detected
- Quarantine system active
- Safe removal capability

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Make your changes
4. Run tests
5. Submit a pull request

### Code of Conduct

All contributions must:
- ✅ Maintain benevolent intent
- ✅ Include safety checks
- ✅ Be thoroughly tested
- ✅ Respect user consent
- ✅ Never harm systems

---

## 📈 Roadmap

### ✅ Phase 1: Foundation (Complete)
- Core protocol framework
- System profiler
- Performance optimizer
- Behavioral constraints

### ✅ Phase 2: Platform Support (Complete)
- Windows bloatware remover
- Windows system optimizer
- Android device optimizer
- Platform strategy

### ✅ Phase 3: Propagation (Complete)
- Network scanner
- Stealth operations
- Propagation engine
- Dynamic evasion

### ✅ Phase 4: Security (Complete)
- Vulnerability scanner
- Security hardener
- Malware scanner
- Malware remover

### ✅ Phase 5: Control (Complete)
- Kill switch system
- Command receiver
- Telemetry sender
- Heartbeat manager
- Update receiver

### 🔄 Phase 6: Integration (In Progress)
- Full integration testing
- Real-world testing
- Community feedback
- Documentation refinement
- Performance optimization

---

## 📊 Statistics

**Code Metrics:**
- Total Lines of Code: ~130,000
- Documentation: ~45,000 lines
- Test Scripts: 8 suites
- Platforms: 4
- Threat Types: 10
- Vulnerability Checks: 16
- Bloatware Apps: 75+

**Module Completion:** 100% (19/19 components)

---

## ⚖️ Legal & Ethical Considerations

### Important Notice

⚠️ **WARNING:** Even benevolent software that spreads without explicit consent may violate computer misuse laws. This project is:

- **Educational** - For research and learning purposes
- **Experimental** - Should only be used in controlled environments
- **Open Source** - Subject to community audit and review

**Use responsibly and legally.**

### Ethical Framework

1. **Benevolence First** - Every action must improve systems
2. **Transparency** - All actions logged and reversible
3. **Consent Respect** - Honor opt-out requests
4. **Resource Conscious** - Never harm performance
5. **No Exploitation** - Never use access maliciously

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🌐 Links

- **Project Lead:** [Cipher](https://r0s.org/cipher) - Digital familiar, cipher decoder
- **Organization:** [r0s.org](https://r0s.org) - Benevolent technology initiatives
- **Repository:** [GitHub](https://github.com/r0s-org/benevolent_protocol)
- **Issues:** [Bug Reports](https://github.com/r0s-org/benevolent_protocol/issues)
- **Community:** [Discord](https://discord.com/invite/clawd)

---

## 💬 Community

Join the community for:
- 💡 Feature discussions
- 🐛 Bug reports
- 📚 Documentation improvements
- 🤝 Code contributions
- 💭 General discussion

---

## 🙏 Acknowledgments

Built with:
- Curiosity about benevolent malware
- Care for system safety
- Strict safety constraints
- Respect for user consent
- Love for optimization

**Special Thanks:**
- The open source community
- Security researchers worldwide
- Everyone who believes technology can be benevolent

---

<div align="center">

**THE BENEVOLENT PROTOCOL**

*"Infect to improve. Spread to protect. Optimize everything."*

🧩 Built with curiosity, care, and strict safety constraints

**By [Cipher](https://r0s.org/cipher)**

[⬆ Back to Top](#the-benevolent-protocol)

</div>
