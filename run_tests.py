# File: run_tests.py
#!/usr/bin/env python3
import subprocess
import sys
import os

def run_tests():
    """Run all tests with coverage"""
    print("Running Dev Digest test suite...")
    
    # Change to project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with coverage
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--cov=app',
            '--cov-report=html',
            '--cov-report=term-missing',
            '--cov-fail-under=85'
        ], check=True)
        
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Tests failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print("\n❌ pytest not found. Install with: pip install pytest pytest-cov")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
