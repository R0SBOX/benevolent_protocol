"""
Runtime tests for the Benevolent Protocol orchestrator.
These tests target the newer runtime loop directly.
"""

import asyncio
import os
import sys
import tempfile
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.orchestrator import BenevolentProtocol
from src.optimization.performance_tuner import PlannedOptimization, OptimizationResult
from src.protection.vulnerability_scanner import Vulnerability, VulnerabilitySeverity
from src.protection.malware_scanner import MalwareThreat, ThreatLevel, ThreatType


@dataclass
class FakeProfile:
    os_type: str = "Linux"
    os_version: str = "test"
    cpu_model: str = "Test CPU"
    cpu_usage: float = 32.0
    memory_usage: float = 72.0
    disk_usage: float = 68.0
    memory_total_gb: float = 16.0
    cpu_cores: int = 8
    profile_timestamp: str = "2026-04-09T00:00:00"


class StubProfiler:
    def __init__(self, profile):
        self.profile_data = profile

    async def profile(self):
        return self.profile_data


class StubConstraints:
    def __init__(self):
        class Mode:
            value = "normal"
        self.current_mode = Mode()

    def refresh_mode(self):
        return self.current_mode

    def emergency_stop_check(self):
        return False

    def check_action_allowed(self, action):
        return getattr(action, "name", "") != "blocked_task"


class StubTuner:
    def __init__(self, plan, failing=None):
        self.plan = plan
        self.failing = set(failing or [])
        self.applied = []

    async def create_optimization_plan(self, profile):
        return list(self.plan)

    async def apply_optimization(self, task):
        self.applied.append(task.name)
        success = task.name not in self.failing
        return OptimizationResult(
            success=success,
            action=task.name,
            description=f"Applied {task.name}" if success else f"Failed {task.name}",
            before_value=None,
            after_value=None,
            impact="positive" if success else "neutral",
            reversible=task.reversible,
            rollback_command=""
        )


class StubVulnerabilityScanner:
    def __init__(self, vulnerabilities):
        self.vulnerabilities = vulnerabilities
        self.calls = 0

    async def scan(self):
        self.calls += 1
        return list(self.vulnerabilities)


class StubMalwareScanner:
    def __init__(self, threats):
        self.threats = threats
        self.calls = 0

    async def scan(self):
        self.calls += 1
        return list(self.threats)


def make_protocol():
    tmpdir = tempfile.TemporaryDirectory()
    protocol = BenevolentProtocol(protocol_dir=tmpdir.name)
    protocol._tmpdir = tmpdir
    return protocol


def test_normal_cycle_applies_only_allowed_and_successful_work():
    protocol = make_protocol()
    profile = FakeProfile()
    allowed = PlannedOptimization(
        id="allowed",
        name="allowed_task",
        action="memory_optimization",
        description="allowed",
        priority="high",
        expected_cpu_percent=2,
        expected_memory_mb=32,
        reversible=True,
        platforms=["linux"],
    )
    blocked = PlannedOptimization(
        id="blocked",
        name="blocked_task",
        action="cpu_optimization",
        description="blocked",
        priority="medium",
        expected_cpu_percent=2,
        expected_memory_mb=16,
        reversible=True,
        platforms=["linux"],
    )
    vuln = Vulnerability(
        id="TEST-001",
        name="Firewall inactive",
        description="test",
        severity=VulnerabilitySeverity.HIGH,
        category="network",
        affected_component="firewall",
        remediation="enable",
        cve_id=None,
        is_patchable=False,
        requires_restart=False,
    )
    threat = MalwareThreat(
        id="THREAT-001",
        name="Test miner",
        threat_type=ThreatType.CRYPTOMINER,
        threat_level=ThreatLevel.MEDIUM,
        file_path=None,
        process_name="miner",
        description="test",
        indicators=["high_cpu_usage"],
        is_removable=False,
        requires_restart=False,
        hash=None,
    )

    protocol.profiler = StubProfiler(profile)
    protocol.constraints = StubConstraints()
    protocol.tuner = StubTuner([allowed, blocked])
    protocol.vuln_scanner = StubVulnerabilityScanner([vuln])
    protocol.malware_scanner = StubMalwareScanner([threat])
    protocol.config["optimization_interval"] = 0
    protocol.config["protection_scan_interval"] = 0

    asyncio.run(protocol._normal_mode_cycle())

    assert protocol.telemetry.get_stats()["optimizations_applied"] == 1
    assert protocol.tuner.applied == ["allowed_task"]
    assert protocol._last_cycle_summary["optimizations_considered"] == 2
    assert protocol._last_cycle_summary["optimizations_applied"] == 1
    assert protocol._last_cycle_summary["blocked_optimizations"] == ["blocked_task"]
    assert protocol._last_cycle_summary["vulnerabilities_found"] == 1
    assert protocol._last_cycle_summary["malware_threats_found"] == 1


def test_optimize_system_tracks_failures_in_results_and_telemetry():
    protocol = make_protocol()
    profile = FakeProfile()
    failing = PlannedOptimization(
        id="failing",
        name="failing_task",
        action="disk_optimization",
        description="failing",
        priority="medium",
        expected_cpu_percent=2,
        expected_memory_mb=16,
        reversible=False,
        platforms=["linux"],
    )

    protocol.profiler = StubProfiler(profile)
    protocol.constraints = StubConstraints()
    protocol.tuner = StubTuner([failing], failing={"failing_task"})

    result = asyncio.run(protocol.optimize_system(profile))

    stats = protocol.telemetry.get_stats()
    assert result["plan"] == ["failing_task"]
    assert result["applied"] == []
    assert len(result["failed"]) == 1
    assert stats["optimizations_applied"] == 0
    assert stats["errors_count"] == 1


def test_status_includes_last_profile_and_cycle_summary():
    protocol = make_protocol()
    protocol._last_profile = FakeProfile()
    protocol._last_cycle_summary = {"mode": "normal", "optimizations_applied": 1}

    status = protocol.get_status()

    assert status["last_profile"]["cpu_model"] == "Test CPU"
    assert status["last_cycle_summary"]["optimizations_applied"] == 1
