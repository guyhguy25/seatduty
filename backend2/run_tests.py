#!/usr/bin/env python3
"""
Simple test runner script for Docker environment.
"""
import subprocess
import sys
import os

def run_tests():
    """Run pytest tests."""
    print("🧪 Running SeatDuty Backend Tests...")
    print("=" * 50)
    
    # Set test database URL
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    try:
        # Run pytest with verbose output
        result = subprocess.run([
            "pytest", 
            "tests/", 
            "-v", 
            "--tb=short",
            "--color=yes"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
            return True
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
