#!/usr/bin/env python3
"""
Test runner for group functionality.
Run this script to execute all group-related tests.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all group tests."""
    print("🧪 Running Group Management Tests...")
    print("=" * 50)
    
    # Change to the backend2 directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with verbose output
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_groups.py", 
        "-v", 
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n✅ All group tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Some tests failed with exit code {e.returncode}")
        return False

def run_specific_test_class(test_class):
    """Run a specific test class."""
    print(f"🧪 Running {test_class} tests...")
    print("=" * 50)
    
    cmd = [
        sys.executable, "-m", "pytest", 
        f"tests/test_groups.py::{test_class}", 
        "-v", 
        "--tb=short",
        "--color=yes"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ {test_class} tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_class} tests failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_class = sys.argv[1]
        success = run_specific_test_class(test_class)
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1)
