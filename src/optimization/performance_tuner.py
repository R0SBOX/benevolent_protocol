"""
Performance Optimizer Module
Safely optimizes system performance without harmful side effects
"""

import os
import platform
import subprocess
from datetime import datetime
import psutil
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class OptimizationResult:
    """Result of an optimization operation"""
    success: bool
    action: str
    description: str
    before_value: Any
    after_value: Any
    impact: str  # "positive", "neutral", "negative"
    reversible: bool
    rollback_command: str


@dataclass
class PlannedOptimization:
    """A conservative optimization candidate derived from current system state."""
    id: str
    name: str
    action: str
    description: str
    priority: str
    expected_cpu_percent: int
    expected_memory_mb: int
    reversible: bool
    platforms: List[str]


@dataclass
class AppliedOptimizationRecord:
    """Tracks optimization execution and rollback state."""
    task_id: str
    task_name: str
    applied_at: str
    result: OptimizationResult
    rolled_back: bool = False
    rollback_attempted_at: Optional[str] = None
    rollback_success: Optional[bool] = None


class PerformanceOptimizer:
    """
    Safely optimizes system performance.
    All operations include safety checks and rollback capabilities.
    """

    def __init__(self):
        self.optimizations_performed = []
        self.platform = platform.system().lower()
        self.optimization_history: List[AppliedOptimizationRecord] = []

    async def create_optimization_plan(self, profile) -> List[PlannedOptimization]:
        """
        Create a conservative optimization plan based on measured system state.
        The plan intentionally stays small and only includes locally-supported
        actions that are cheap enough to safety-gate.
        """
        plan: List[PlannedOptimization] = []

        if self.platform != "linux":
            return plan

        if profile.memory_usage >= 70 and os.path.exists('/proc/sys/vm/drop_caches'):
            plan.append(PlannedOptimization(
                id="memory-cache-clear",
                name="memory_cache_clear",
                action="memory_optimization",
                description="Clear reclaimable Linux page caches when memory pressure is elevated.",
                priority="high" if profile.memory_usage >= 85 else "medium",
                expected_cpu_percent=5,
                expected_memory_mb=64,
                reversible=False,
                platforms=["linux"]
            ))

        if profile.cpu_usage >= 60 and self._has_cpu_governor_control():
            plan.append(PlannedOptimization(
                id="cpu-governor-performance",
                name="cpu_governor",
                action="cpu_optimization",
                description="Switch CPU governor to performance mode when sustained CPU pressure is observed.",
                priority="medium",
                expected_cpu_percent=3,
                expected_memory_mb=16,
                reversible=True,
                platforms=["linux"]
            ))

        if profile.disk_usage >= 75 and os.path.exists('/sys/block'):
            plan.append(PlannedOptimization(
                id="disk-scheduler-tune",
                name="disk_scheduler",
                action="disk_optimization",
                description="Tune Linux block scheduler for better responsiveness on busy disks.",
                priority="medium",
                expected_cpu_percent=3,
                expected_memory_mb=16,
                reversible=True,
                platforms=["linux"]
            ))

        priority_rank = {"high": 0, "medium": 1, "low": 2}
        return sorted(plan, key=lambda item: priority_rank.get(item.priority, 99))

    async def apply_optimization(self, task: PlannedOptimization) -> OptimizationResult:
        """Apply a planned optimization by action identifier."""
        if task.name == "memory_cache_clear":
            result = self.optimize_memory()
        elif task.name == "cpu_governor":
            result = self.optimize_cpu_governor()
        elif task.name == "disk_scheduler":
            result = self.optimize_disk_scheduler()
        else:
            result = OptimizationResult(
                success=False,
                action=task.name,
                description=f"Unknown optimization task: {task.name}",
                before_value=None,
                after_value=None,
                impact="neutral",
                reversible=False,
                rollback_command=""
            )

        if result.success:
            self.optimizations_performed.append(result)
            self.optimization_history.append(AppliedOptimizationRecord(
                task_id=task.id,
                task_name=task.name,
                applied_at=datetime.now().isoformat(),
                result=result,
            ))

        return result

    def _has_cpu_governor_control(self) -> bool:
        """Check if Linux CPU governor control paths exist."""
        for i in range(psutil.cpu_count() or 0):
            path = f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_governor"
            if os.path.exists(path):
                return True
        return False

    def optimize_memory(self) -> OptimizationResult:
        """
        Optimize memory usage by clearing caches.
        Safe operation that can improve performance.
        """
        try:
            before = psutil.virtual_memory().percent

            # Linux: Clear page cache, dentries, and inodes
            if os.path.exists('/proc/sys/vm/drop_caches'):
                subprocess.run(
                    ['sync'],
                    timeout=10
                )
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3')  # Clear all caches

                after = psutil.virtual_memory().percent

                return OptimizationResult(
                    success=True,
                    action="memory_cache_clear",
                    description="Cleared system memory caches",
                    before_value=before,
                    after_value=after,
                    impact="positive" if after < before else "neutral",
                    reversible=False,
                    rollback_command=""  # Cannot undo cache clear
                )
        except Exception as e:
            return OptimizationResult(
                success=False,
                action="memory_cache_clear",
                description=f"Failed to clear memory caches: {e}",
                before_value=None,
                after_value=None,
                impact="neutral",
                reversible=False,
                rollback_command=""
            )

    def optimize_cpu_governor(self) -> OptimizationResult:
        """
        Set CPU governor to 'performance' mode.
        Improves CPU responsiveness.
        """
        try:
            # Check current governor
            cpu_paths = []
            for i in range(psutil.cpu_count()):
                path = f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_governor"
                if os.path.exists(path):
                    cpu_paths.append(path)

            if not cpu_paths:
                return OptimizationResult(
                    success=False,
                    action="cpu_governor",
                    description="CPU governor control not available",
                    before_value=None,
                    after_value=None,
                    impact="neutral",
                    reversible=False,
                    rollback_command=""
                )

            # Read current governor
            with open(cpu_paths[0], 'r') as f:
                before = f.read().strip()

            # Set to performance mode
            for path in cpu_paths:
                with open(path, 'w') as f:
                    f.write('performance')

            # Verify change
            with open(cpu_paths[0], 'r') as f:
                after = f.read().strip()

            return OptimizationResult(
                success=True,
                action="cpu_governor",
                description="Set CPU governor to performance mode",
                before_value=before,
                after_value=after,
                impact="positive",
                reversible=True,
                rollback_command=f"echo '{before}' | tee {' '.join(cpu_paths)}"
            )

        except Exception as e:
            return OptimizationResult(
                success=False,
                action="cpu_governor",
                description=f"Failed to set CPU governor: {e}",
                before_value=None,
                after_value=None,
                impact="neutral",
                reversible=False,
                rollback_command=""
            )

    def optimize_disk_scheduler(self) -> OptimizationResult:
        """
        Optimize disk I/O scheduler for performance.
        Changes from CFQ to deadline or noop for SSDs.
        """
        try:
            # Find block devices
            block_devices = []
            for device in os.listdir('/sys/block/'):
                if device.startswith(('sd', 'nvme', 'vd')):
                    block_devices.append(device)

            if not block_devices:
                return OptimizationResult(
                    success=False,
                    action="disk_scheduler",
                    description="No block devices found",
                    before_value=None,
                    after_value=None,
                    impact="neutral",
                    reversible=False,
                    rollback_command=""
                )

            optimizations = []

            for device in block_devices:
                scheduler_path = f"/sys/block/{device}/queue/scheduler"

                if not os.path.exists(scheduler_path):
                    continue

                # Read current scheduler
                with open(scheduler_path, 'r') as f:
                    current = f.read().strip()

                # Determine optimal scheduler
                if 'nvme' in device:
                    optimal = 'none'  # NVMe doesn't need scheduler
                else:
                    optimal = 'mq-deadline'  # Good for both SSD and HDD

                # Set scheduler
                try:
                    with open(scheduler_path, 'w') as f:
                        f.write(optimal)

                    optimizations.append({
                        "device": device,
                        "before": current,
                        "after": optimal
                    })
                except:
                    continue

            if optimizations:
                return OptimizationResult(
                    success=True,
                    action="disk_scheduler",
                    description=f"Optimized disk schedulers for {len(optimizations)} devices",
                    before_value=[o["before"] for o in optimizations],
                    after_value=[o["after"] for o in optimizations],
                    impact="positive",
                    reversible=True,
                    rollback_command="; ".join([
                        f"echo '{o['before']}' > /sys/block/{o['device']}/queue/scheduler"
                        for o in optimizations
                    ])
                )
            else:
                return OptimizationResult(
                    success=False,
                    action="disk_scheduler",
                    description="No disk schedulers optimized",
                    before_value=None,
                    after_value=None,
                    impact="neutral",
                    reversible=False,
                    rollback_command=""
                )

        except Exception as e:
            return OptimizationResult(
                success=False,
                action="disk_scheduler",
                description=f"Failed to optimize disk schedulers: {e}",
                before_value=None,
                after_value=None,
                impact="neutral",
                reversible=False,
                rollback_command=""
            )

    def run_all_optimizations(self) -> List[OptimizationResult]:
        """
        Run all safe performance optimizations.
        Returns list of results for each optimization.
        """
        optimizations = [
            self.optimize_memory(),
            self.optimize_cpu_governor(),
            self.optimize_disk_scheduler()
        ]

        # Filter out failed optimizations
        successful = [opt for opt in optimizations if opt.success]

        return successful

    def rollback_optimization(self, result: OptimizationResult) -> bool:
        """
        Rollback a specific optimization if it had negative impact.
        """
        if not result.reversible or not result.rollback_command:
            return False

        try:
            subprocess.run(
                result.rollback_command,
                shell=True,
                timeout=10,
                check=True
            )
            return True
        except:
            return False

    def rollback_last_optimization(self) -> Dict[str, Any]:
        """Rollback the most recent reversible optimization."""
        for record in reversed(self.optimization_history):
            if record.rolled_back or not record.result.reversible:
                continue

            record.rollback_attempted_at = datetime.now().isoformat()
            success = self.rollback_optimization(record.result)
            record.rollback_success = success
            record.rolled_back = success
            return {
                "success": success,
                "task_name": record.task_name,
                "task_id": record.task_id,
                "rolled_back": success,
            }

        return {
            "success": False,
            "message": "No reversible optimization available for rollback",
        }

    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Return optimization execution history in a status-safe shape."""
        return [
            {
                "task_id": record.task_id,
                "task_name": record.task_name,
                "applied_at": record.applied_at,
                "rolled_back": record.rolled_back,
                "rollback_attempted_at": record.rollback_attempted_at,
                "rollback_success": record.rollback_success,
                "action": record.result.action,
                "description": record.result.description,
                "impact": record.result.impact,
                "reversible": record.result.reversible,
            }
            for record in self.optimization_history
        ]


# Example usage
if __name__ == "__main__":
    optimizer = PerformanceOptimizer()

    print("=== Running Performance Optimizations ===\n")

    results = optimizer.run_all_optimizations()

    for result in results:
        print(f"✓ {result.description}")
        print(f"  Before: {result.before_value}")
        print(f"  After: {result.after_value}")
        print(f"  Impact: {result.impact}")
        print(f"  Reversible: {result.reversible}")
        print()
