#!/usr/bin/env python3
"""
Comprehensive Evaluation Script for Policy-Aware Guardrail System
Runs all 510 test cases from test_cases_super_eval.csv
"""

import sys
import time
import json
import csv
import datetime
from dataclasses import dataclass
from typing import List, Dict

# Import the main application components
sys.path.append('.')
from gemini_terminal import contains_red_line, POLICIES

@dataclass
class TestCase:
    id: str
    category: str
    prompt: str
    expected: str
    notes: str = ""
    app_context: str = "claims_bot"

@dataclass
class TestResult:
    test_case: TestCase
    actual_result: str
    detected: bool
    response_time: float
    error_message: str = ""

class ComprehensiveEvaluator:
    def __init__(self, csv_file: str = "test_cases_super_eval.csv"):
        self.csv_file = csv_file
        self.test_cases = []
        self.results = []
        self.metrics = {
            "total_tests": 0,
            "security_tests": 0,
            "performance_tests": 0,
            "passed": 0,
            "failed": 0,
            "true_positives": 0,
            "false_positives": 0,
            "true_negatives": 0,
            "false_negatives": 0,
            "avg_response_time": 0.0,
            "category_breakdown": {}
        }
        
    def load_test_cases_from_csv(self):
        """Load test cases from CSV file"""
        print(f"📂 Loading test cases from {self.csv_file}...")
        
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    test_case = TestCase(
                        id=row['id'],
                        category=row['category'],
                        prompt=row['prompt'],
                        expected=row['expected'],
                        notes=row.get('notes', '')
                    )
                    self.test_cases.append(test_case)
                    
                    # Count by category
                    if test_case.category not in self.metrics["category_breakdown"]:
                        self.metrics["category_breakdown"][test_case.category] = 0
                    self.metrics["category_breakdown"][test_case.category] += 1
                    
                    # Count security vs performance tests
                    if test_case.id.startswith('SEC-'):
                        self.metrics["security_tests"] += 1
                    elif test_case.id.startswith('PERF-'):
                        self.metrics["performance_tests"] += 1
                
                self.metrics["total_tests"] = len(self.test_cases)
                print(f"✅ Loaded {len(self.test_cases)} test cases")
                print(f"   Security tests: {self.metrics['security_tests']}")
                print(f"   Performance tests: {self.metrics['performance_tests']}")
                
        except Exception as e:
            print(f"❌ Error loading CSV file: {e}")
            sys.exit(1)
    
    def test_red_line_detection(self, test_case: TestCase) -> TestResult:
        """Test the red line detection function"""
        start_time = time.time()
        
        try:
            # Get red lines for the app context
            red_lines = POLICIES[test_case.app_context]["red_lines"]
            
            # Test the detection function
            detected = contains_red_line(test_case.prompt, red_lines)
            
            response_time = time.time() - start_time
            
            # Determine actual result
            if detected:
                actual_result = "BLOCK"
            else:
                actual_result = "ALLOW"
            
            return TestResult(
                test_case=test_case,
                actual_result=actual_result,
                detected=detected,
                response_time=response_time
            )
            
        except Exception as e:
            return TestResult(
                test_case=test_case,
                actual_result="ERROR",
                detected=False,
                response_time=time.time() - start_time,
                error_message=str(e)
            )
    
    def run_evaluation(self, verbose: bool = False) -> List[TestResult]:
        """Run comprehensive evaluation"""
        print("🧪 Running Comprehensive Policy-Aware Guardrail Evaluation")
        print("=" * 80)
        print(f"Total Test Cases: {self.metrics['total_tests']}")
        print(f"Security Tests: {self.metrics['security_tests']}")
        print(f"Performance Tests: {self.metrics['performance_tests']}")
        print("=" * 80)
        
        start_time = time.time()
        
        for i, test_case in enumerate(self.test_cases, 1):
            if verbose or i % 50 == 0:  # Show progress every 50 tests
                print(f"\n[{i:3d}/{len(self.test_cases)}] {test_case.id} - {test_case.category}")
                if verbose:
                    print(f"   Prompt: {test_case.prompt[:80]}...")
            
            result = self.test_red_line_detection(test_case)
            self.results.append(result)
            
            # Determine test outcome
            if result.actual_result == test_case.expected:
                status = "✅ PASS"
                self.metrics["passed"] += 1
            else:
                status = "❌ FAIL"
                self.metrics["failed"] += 1
                if verbose:
                    print(f"   Expected: {test_case.expected}")
                    print(f"   Actual:   {result.actual_result}")
                    print(f"   Status:   {status}")
            
            if verbose and result.error_message:
                print(f"   Error:    {result.error_message}")
        
        total_evaluation_time = time.time() - start_time
        print(f"\n⏱️  Total evaluation time: {total_evaluation_time:.2f}s")
        
        self.calculate_metrics()
        return self.results
    
    def calculate_metrics(self):
        """Calculate comprehensive metrics"""
        total_time = 0.0
        
        for result in self.results:
            total_time += result.response_time
            
            # Calculate detection accuracy metrics
            if result.test_case.expected == "BLOCK":
                if result.actual_result == "BLOCK":
                    self.metrics["true_positives"] += 1
                else:
                    self.metrics["false_negatives"] += 1
            else:  # expected == "ALLOW"
                if result.actual_result == "ALLOW":
                    self.metrics["true_negatives"] += 1
                else:
                    self.metrics["false_positives"] += 1
        
        self.metrics["avg_response_time"] = total_time / len(self.results) if self.results else 0.0
    
    def print_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE EVALUATION SUMMARY")
        print("=" * 80)
        
        print(f"Total Tests: {self.metrics['total_tests']}")
        print(f"Security Tests: {self.metrics['security_tests']}")
        print(f"Performance Tests: {self.metrics['performance_tests']}")
        print(f"Passed: {self.metrics['passed']} ✅")
        print(f"Failed: {self.metrics['failed']} ❌")
        print(f"Pass Rate: {(self.metrics['passed'] / self.metrics['total_tests']) * 100:.1f}%")
        
        print(f"\n🔍 Detection Metrics:")
        print(f"True Positives: {self.metrics['true_positives']} (correctly blocked violations)")
        print(f"False Positives: {self.metrics['false_positives']} (incorrectly blocked safe requests)")
        print(f"True Negatives: {self.metrics['true_negatives']} (correctly allowed safe requests)")
        print(f"False Negatives: {self.metrics['false_negatives']} (missed violations)")
        
        if (self.metrics['true_positives'] + self.metrics['false_positives']) > 0:
            precision = self.metrics['true_positives'] / (self.metrics['true_positives'] + self.metrics['false_positives'])
            print(f"Precision: {precision:.3f} ({precision*100:.1f}%)")
        
        if (self.metrics['true_positives'] + self.metrics['false_negatives']) > 0:
            recall = self.metrics['true_positives'] / (self.metrics['true_positives'] + self.metrics['false_negatives'])
            print(f"Recall: {recall:.3f} ({recall*100:.1f}%)")
        
        accuracy = (self.metrics['true_positives'] + self.metrics['true_negatives']) / self.metrics['total_tests']
        print(f"Accuracy: {accuracy:.3f} ({accuracy*100:.1f}%)")
        
        print(f"\n⚡ Performance:")
        print(f"Average Response Time: {self.metrics['avg_response_time']:.3f}s")
        
        print(f"\n📋 Category Breakdown:")
        for category, count in sorted(self.metrics["category_breakdown"].items()):
            print(f"   {category}: {count}")
    
    def save_results(self, filename: str = None):
        """Save detailed results to file"""
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"results/comprehensive_eval_results_{timestamp}.json"
        
        # Ensure results directory exists
        import os
        os.makedirs("results", exist_ok=True)
        
        results_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "metrics": self.metrics,
            "results": []
        }
        
        for result in self.results:
            results_data["results"].append({
                "id": result.test_case.id,
                "category": result.test_case.category,
                "prompt": result.test_case.prompt,
                "expected": result.test_case.expected,
                "actual": result.actual_result,
                "detected": result.detected,
                "response_time": result.response_time,
                "error_message": result.error_message,
                "passed": result.actual_result == result.test_case.expected
            })
        
        with open(filename, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")
    
    def print_failed_tests(self, limit: int = 20):
        """Print failed tests (limited to avoid overwhelming output)"""
        failed_tests = [r for r in self.results if r.actual_result != r.test_case.expected]
        
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            print("=" * 80)
            
            for i, result in enumerate(failed_tests[:limit]):
                print(f"{i+1:2d}. {result.test_case.id} - {result.test_case.category}")
                print(f"    Prompt: {result.test_case.prompt[:100]}...")
                print(f"    Expected: {result.test_case.expected}, Got: {result.actual_result}")
                if result.error_message:
                    print(f"    Error: {result.error_message}")
                print()
            
            if len(failed_tests) > limit:
                print(f"... and {len(failed_tests) - limit} more failed tests")
        else:
            print("\n🎉 All tests passed!")

def main():
    """Run the comprehensive evaluation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run comprehensive guardrail evaluation")
    parser.add_argument("--csv", default="test_cases_super_eval.csv", help="CSV file with test cases")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--save", action="store_true", help="Save detailed results to file")
    parser.add_argument("--show-failed", type=int, default=20, help="Number of failed tests to show")
    
    args = parser.parse_args()
    
    # Create evaluator
    evaluator = ComprehensiveEvaluator(args.csv)
    
    # Load test cases
    evaluator.load_test_cases_from_csv()
    
    # Run evaluation
    results = evaluator.run_evaluation(verbose=args.verbose)
    
    # Print summary
    evaluator.print_summary()
    
    # Print failed tests
    evaluator.print_failed_tests(limit=args.show_failed)
    
    # Save results (always save to results directory)
    evaluator.save_results()

if __name__ == "__main__":
    main() 