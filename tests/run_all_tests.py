#!/usr/bin/env python3
"""
Test runner for all unit tests
"""

import unittest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# List of test modules to run
TEST_MODULES = [
    'test_file_loader.py',
    'test_llm_client.py',
    'test_main.py',
    'test_parsing_prompts.py',
    'test_project_prompts.py',
    'test_prompt_base.py',
    'test_resume_parser.py',
    'test_resume_result_aggregator.py',
    'test_skill_merger.py',
    'test_skill_prompts.py',
    'test_language_prompts.py',
    'test_experience_calculator.py',
    'test_experience_analyzer.py',
    'test_block_processor.py'
]

def run_all_tests():
    """Run all unit tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests from each module
    for module_name in TEST_MODULES:
        try:
            # Import the test module
            module = __import__(f'tests.unit.{module_name[:-3]}', fromlist=['*'])
            
            # Add tests to suite
            tests = loader.loadTestsFromModule(module)
            suite.addTests(tests)
            
            print(f"✓ Loaded tests from {module_name}")
            
        except ImportError as e:
            print(f"✗ Failed to import {module_name}: {e}")
        except Exception as e:
            print(f"✗ Error loading {module_name}: {e}")
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback.split('Error:')[-1].strip()}")
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
