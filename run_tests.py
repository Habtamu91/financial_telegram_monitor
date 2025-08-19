#!/usr/bin/env python3
"""
Test runner for Financial Telegram Monitor
Runs all unit and integration tests with coverage reporting.
"""

import unittest
import sys
import os
from io import StringIO

def run_tests():
    """Run all tests and return results."""
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    
    # Load unit tests
    unit_suite = loader.discover('tests/unit', pattern='test_*.py')
    
    # Load integration tests
    integration_suite = loader.discover('tests/integration', pattern='test_*.py')
    
    # Combine all test suites
    all_tests = unittest.TestSuite([unit_suite, integration_suite])
    
    # Run tests with detailed output
    stream = StringIO()
    runner = unittest.TextTestRunner(
        stream=stream,
        verbosity=2,
        descriptions=True,
        failfast=False
    )
    
    print("=" * 70)
    print("FINANCIAL TELEGRAM MONITOR - TEST SUITE")
    print("=" * 70)
    
    result = runner.run(all_tests)
    
    # Print results
    output = stream.getvalue()
    print(output)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Error:')[-1].strip()}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / 
                   max(result.testsRun, 1)) * 100
    
    print(f"\nSuccess Rate: {success_rate:.1f}%")
    
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        return True
    else:
        print("❌ SOME TESTS FAILED!")
        return False

def run_specific_test(test_module):
    """Run a specific test module."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName(test_module)
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_module = sys.argv[1]
        success = run_specific_test(test_module)
    else:
        # Run all tests
        success = run_tests()
    
    sys.exit(0 if success else 1)



