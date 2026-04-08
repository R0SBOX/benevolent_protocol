#!/usr/bin/env python3
"""
Windows Optimization Demo
Tests and demonstrates Windows-specific optimizations
"""

import sys
from pathlib import Path
from typing import TextIO

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.optimization.windows_bloatware import WindowsBloatwareRemover
from src.optimization.windows_optimizer import WindowsSystemOptimizer


def _safe_print(text: str = "", stream: TextIO = sys.stdout):
    """
    Print text while degrading unsupported console characters on narrow encodings.
    This keeps the demo script usable on default Windows cp1252 consoles.
    """
    encoding = getattr(stream, "encoding", None) or "utf-8"
    try:
        print(text, file=stream)
    except UnicodeEncodeError:
        sanitized = text.encode(encoding, errors="replace").decode(encoding)
        print(sanitized, file=stream)


def _print_header(title: str):
    _safe_print("=" * 60)
    _safe_print(title)
    _safe_print("=" * 60)
    _safe_print()


def test_bloatware_scanner():
    """Test Windows bloatware scanner"""
    _print_header("Windows Bloatware Scanner Test")

    # Check if running on Windows
    if sys.platform != "win32":
        _safe_print("This test requires Windows")
        _safe_print("   Showing mock results instead...")
        _safe_print()

        # Mock demonstration
        _safe_print("Sample Bloatware Database:")
        remover = WindowsBloatwareRemover()
        for item in remover.bloatware_database[:5]:  # Show first 5
            _safe_print(f"   - {item.name}")
            _safe_print(f"     Safe to remove: {item.safe_to_remove}")
            _safe_print(f"     Category: {item.category}")
            _safe_print()

        _safe_print("Database loaded successfully")
        _safe_print("   Run on Windows to scan actual installed apps")
        return

    # Actual Windows scan
    remover = WindowsBloatwareRemover()

    _safe_print("Scanning for installed bloatware...")
    installed = remover.scan_installed_bloatware()

    _safe_print(f"\nResults: {len(installed)} bloatware apps found\n")

    # Categorize
    safe = [item for item in installed if item.safe_to_remove]
    caution = [item for item in installed if not item.safe_to_remove]

    if safe:
        _safe_print(f"Safe to Remove ({len(safe)}):")
        for item in safe:
            _safe_print(f"   - {item.name}")
        _safe_print()

    if caution:
        _safe_print(f"Review Before Removing ({len(caution)}):")
        for item in caution:
            _safe_print(f"   - {item.name} - {item.description}")
        _safe_print()


def test_system_optimizer():
    """Test Windows system optimizer"""
    _print_header("Windows System Optimizer Test")

    # Check if running on Windows
    if sys.platform != "win32":
        _safe_print("This test requires Windows")
        _safe_print("   Showing available optimizations instead...")
        _safe_print()

        # Show available optimizations
        optimizer = WindowsSystemOptimizer()
        report = optimizer.get_optimization_report()

        _safe_print("Available Optimizations by Category:\n")

        for category, opts in report["optimizations"].items():
            _safe_print(f"{category.upper()} ({len(opts)} optimizations):")
            for opt in opts[:3]:  # Show first 3 per category
                _safe_print(f"   - {opt['name']}")
                _safe_print(f"     Impact: {opt['impact']} | Restart: {opt['requires_restart']}")
            if len(opts) > 3:
                _safe_print(f"   ... and {len(opts) - 3} more")
            _safe_print()

        _safe_print("Optimization database loaded successfully")
        _safe_print("   Run on Windows to apply optimizations")
        return

    # Actual Windows optimization
    optimizer = WindowsSystemOptimizer()
    report = optimizer.get_optimization_report()

    _safe_print("Optimization Report:\n")

    for category, count in report["by_category"].items():
        _safe_print(f"   {category.capitalize()}: {count} optimizations")

    _safe_print(f"\n   Total: {report['total_optimizations']} available")
    _safe_print()

    # Show what would be applied
    _safe_print("Safe Optimizations (Auto-Apply):")
    _safe_print("   - Privacy optimizations")
    _safe_print("   - Security optimizations")
    _safe_print("   - Low/Medium impact only")
    _safe_print()

    _safe_print("Manual Review Recommended:")
    _safe_print("   - Performance optimizations")
    _safe_print("   - Service modifications")
    _safe_print("   - High impact changes")


def show_windows_features():
    """Display Windows-specific features"""
    _print_header("THE BENEVOLENT PROTOCOL - Windows Features")

    _safe_print("BLOATWARE REMOVAL:")
    _safe_print("   - Candy Crush Saga")
    _safe_print("   - Microsoft Solitaire Collection")
    _safe_print("   - Minecraft Trial")
    _safe_print("   - Skype App")
    _safe_print("   - Maps, Weather, News, Sports apps")
    _safe_print("   - Paint 3D, 3D Viewer")
    _safe_print("   - Mixed Reality Portal")
    _safe_print("   - Feedback Hub, Tips")
    _safe_print("   - Mail, Calendar, Photos (user review)")
    _safe_print()

    _safe_print("PERFORMANCE OPTIMIZATIONS:")
    _safe_print("   - Disable SysMain (Superfetch) for SSDs")
    _safe_print("   - Set High Performance power plan")
    _safe_print("   - Disable transparency effects")
    _safe_print("   - Disable UI animations")
    _safe_print("   - Disable hibernation (frees several GB)")
    _safe_print("   - Reduce System Restore space")
    _safe_print("   - Disable Windows Search indexing")
    _safe_print()

    _safe_print("PRIVACY OPTIMIZATIONS:")
    _safe_print("   - Set telemetry to basic")
    _safe_print("   - Disable advertising ID")
    _safe_print("   - Disable app launch tracking")
    _safe_print("   - Disable location tracking")
    _safe_print()

    _safe_print("SECURITY OPTIMIZATIONS:")
    _safe_print("   - Enable Windows Defender")
    _safe_print("   - Enable Windows Firewall")
    _safe_print("   - Disable Remote Registry")
    _safe_print()

    _safe_print("SERVICE OPTIMIZATIONS:")
    _safe_print("   - Disable Print Spooler (if no printer)")
    _safe_print("   - Disable Fax Service")
    _safe_print("   - Disable Xbox Services (if not gaming)")
    _safe_print()

    _safe_print("GAMING MODE:")
    _safe_print("   - Auto-detect gaming activity")
    _safe_print("   - Drop to 5% CPU during gameplay")
    _safe_print("   - Security monitoring only")
    _safe_print("   - No optimizations during gaming")
    _safe_print()

    _safe_print("LINUX POLICY:")
    _safe_print("   - Do NOT infect Linux systems")
    _safe_print("   - Respect Linux users' expertise")
    _safe_print("   - Explicit opt-in only")
    _safe_print()


def main():
    """Run all Windows feature tests"""
    _safe_print()
    show_windows_features()
    _safe_print()
    test_bloatware_scanner()
    _safe_print()
    test_system_optimizer()
    _safe_print()
    _print_header("Windows Features Test Complete")


if __name__ == "__main__":
    main()
