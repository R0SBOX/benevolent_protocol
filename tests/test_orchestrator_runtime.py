"""
Runtime tests for the Benevolent Protocol orchestrator.
These tests target the newer runtime loop directly.
"""

import asyncio
import hashlib
import hmac
import json
import os
import sys
import tempfile
from dataclasses import dataclass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.orchestrator import BenevolentProtocol
from src.optimization.performance_tuner import PlannedOptimization, OptimizationResult
from src.protection.malware_remover import RemovalResult
from src.protection.malware_scanner import MalwareThreat, ThreatLevel, ThreatType
from src.protection.vulnerability_scanner import Vulnerability, VulnerabilitySeverity


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


@dataclass
class FakeRecommendation:
    item_id: str
    title: str
    action_type: str
    recommended_action: str
    safe_for_auto: bool
    requires_restart: bool
    priority: str


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
        self.rollback_called = False

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
            rollback_command="rollback-test" if task.reversible else ""
        )

    def get_optimization_history(self):
        return [
            {
                "task_name": name,
                "rolled_back": False,
            }
            for name in self.applied
        ]

    def rollback_last_optimization(self):
        self.rollback_called = True
        return {"success": True, "task_name": self.applied[-1] if self.applied else None}


class StubVulnerabilityScanner:
    def __init__(self, vulnerabilities):
        self.vulnerabilities = vulnerabilities
        self.calls = 0

    async def scan(self):
        self.calls += 1
        return list(self.vulnerabilities)

    def get_remediation_recommendations(self, vulnerabilities=None):
        items = vulnerabilities if vulnerabilities is not None else self.vulnerabilities
        return [
            FakeRecommendation(
                item_id=item.id,
                title=item.name,
                action_type="hardening",
                recommended_action=item.remediation,
                safe_for_auto=item.is_patchable,
                requires_restart=item.requires_restart,
                priority=item.severity.value,
            )
            for item in items
        ]


class StubMalwareScanner:
    def __init__(self, threats):
        self.threats = threats
        self.calls = 0
        self.detected_threats = list(threats)

    async def scan(self):
        self.calls += 1
        self.detected_threats = list(self.threats)
        return list(self.threats)

    def get_remediation_recommendations(self, threats=None):
        items = threats if threats is not None else self.threats
        return [
            FakeRecommendation(
                item_id=item.id,
                title=item.name,
                action_type="quarantine_file",
                recommended_action="Quarantine the threat",
                safe_for_auto=item.is_removable,
                requires_restart=item.requires_restart,
                priority=item.threat_level.value,
            )
            for item in items
        ]


class StubMalwareRemover:
    def __init__(self, success_ids=None):
        self.success_ids = set(success_ids or [])
        self.calls = []

    def remove_threats(self, threats):
        self.calls.append([item.id for item in threats])
        return [
            RemovalResult(
                threat_id=item.id,
                threat_name=item.name,
                action="file_removal",
                success=item.id in self.success_ids,
                message="removed" if item.id in self.success_ids else "skipped",
                requires_restart=item.requires_restart,
                backup_path=None,
            )
            for item in threats
        ]


class StubSecurityHardener:
    def __init__(self):
        self.calls = []

    def harden_system(self, vulnerabilities):
        self.calls.append([item.id for item in vulnerabilities])
        return [
            type(
                "HardeningResult",
                (),
                {
                    "vulnerability_id": item.id,
                    "action": "apply_fix",
                    "success": True,
                    "message": "applied",
                },
            )()
            for item in vulnerabilities
        ]


def make_protocol():
    tmpdir = tempfile.TemporaryDirectory()
    protocol = BenevolentProtocol(protocol_dir=tmpdir.name)
    protocol._tmpdir = tmpdir
    return protocol


def sign_command(secret, payload):
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


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


def test_status_includes_last_profile_cycle_summary_and_optimization_history():
    protocol = make_protocol()
    protocol._last_profile = FakeProfile()
    protocol._last_cycle_summary = {"mode": "normal", "optimizations_applied": 1}
    protocol.tuner = StubTuner([])
    protocol.tuner.applied = ["allowed_task"]

    status = protocol.get_status()

    assert status["last_profile"]["cpu_model"] == "Test CPU"
    assert status["last_cycle_summary"]["optimizations_applied"] == 1
    assert status["optimization_history"][0]["task_name"] == "allowed_task"


def test_scan_reports_include_structured_recommendations():
    protocol = make_protocol()
    vuln = Vulnerability(
        id="TEST-VULN",
        name="Firewall inactive",
        description="test",
        severity=VulnerabilitySeverity.HIGH,
        category="network",
        affected_component="firewall",
        remediation="Enable the firewall",
        cve_id=None,
        is_patchable=True,
        requires_restart=False,
    )
    threat = MalwareThreat(
        id="TEST-THREAT",
        name="Test miner",
        threat_type=ThreatType.CRYPTOMINER,
        threat_level=ThreatLevel.HIGH,
        file_path="/tmp/test-miner",
        process_name=None,
        description="test",
        indicators=["hash_match"],
        is_removable=True,
        requires_restart=False,
        hash=None,
    )
    protocol.vuln_scanner = StubVulnerabilityScanner([vuln])
    protocol.malware_scanner = StubMalwareScanner([threat])

    vuln_report = asyncio.run(protocol.scan_vulnerabilities())
    malware_report = asyncio.run(protocol.scan_malware())

    assert vuln_report["recommendations"][0]["item_id"] == "TEST-VULN"
    assert malware_report["recommendations"][0]["item_id"] == "TEST-THREAT"


def test_command_driven_remediation_and_rollback_flow():
    protocol = make_protocol()
    profile = FakeProfile()
    vuln = Vulnerability(
        id="TEST-HARDEN",
        name="Firewall inactive",
        description="test",
        severity=VulnerabilitySeverity.HIGH,
        category="network",
        affected_component="firewall",
        remediation="Enable the firewall",
        cve_id=None,
        is_patchable=True,
        requires_restart=False,
    )
    threat = MalwareThreat(
        id="TEST-REMOVE",
        name="Test miner",
        threat_type=ThreatType.CRYPTOMINER,
        threat_level=ThreatLevel.HIGH,
        file_path="/tmp/test-miner",
        process_name=None,
        description="test",
        indicators=["hash_match"],
        is_removable=True,
        requires_restart=False,
        hash=None,
    )
    reversible = PlannedOptimization(
        id="reversible",
        name="reversible_task",
        action="cpu_optimization",
        description="reversible",
        priority="medium",
        expected_cpu_percent=2,
        expected_memory_mb=16,
        reversible=True,
        platforms=["linux"],
    )

    protocol.profiler = StubProfiler(profile)
    protocol.constraints = StubConstraints()
    protocol.tuner = StubTuner([reversible])
    protocol.vuln_scanner = StubVulnerabilityScanner([vuln])
    protocol.malware_scanner = StubMalwareScanner([threat])
    protocol.malware_remover = StubMalwareRemover(success_ids={"TEST-REMOVE"})
    protocol.hardener = StubSecurityHardener()

    optimize_payload = json.dumps({
        "command_id": "cmd-opt",
        "command_type": "optimize",
        "timestamp": "2026-04-09T00:00:00",
        "source": "test-controller",
        "parameters": {}
    })
    optimize_result = asyncio.run(
        protocol.handle_signed_command(
            optimize_payload,
            sign_command(protocol.config["control_secret"], optimize_payload)
        )
    )

    quarantine_payload = json.dumps({
        "command_id": "cmd-qua",
        "command_type": "quarantine",
        "timestamp": "2026-04-09T00:00:00",
        "source": "test-controller",
        "parameters": {"threat_ids": ["TEST-REMOVE"]}
    })
    quarantine_result = asyncio.run(
        protocol.handle_signed_command(
            quarantine_payload,
            sign_command(protocol.config["control_secret"], quarantine_payload)
        )
    )

    harden_payload = json.dumps({
        "command_id": "cmd-hard",
        "command_type": "harden",
        "timestamp": "2026-04-09T00:00:00",
        "source": "test-controller",
        "parameters": {"vulnerability_ids": ["TEST-HARDEN"]}
    })
    harden_result = asyncio.run(
        protocol.handle_signed_command(
            harden_payload,
            sign_command(protocol.config["control_secret"], harden_payload)
        )
    )

    rollback_payload = json.dumps({
        "command_id": "cmd-roll",
        "command_type": "rollback",
        "timestamp": "2026-04-09T00:00:00",
        "source": "test-controller",
        "parameters": {}
    })
    rollback_result = asyncio.run(
        protocol.handle_signed_command(
            rollback_payload,
            sign_command(protocol.config["control_secret"], rollback_payload)
        )
    )

    assert optimize_result["success"]
    assert quarantine_result["data"]["removed"] == 1
    assert harden_result["data"]["hardened"] == 1
    assert rollback_result["data"]["success"]
    assert protocol.tuner.rollback_called
    assert protocol.telemetry.get_stats()["threats_removed"] == 1
