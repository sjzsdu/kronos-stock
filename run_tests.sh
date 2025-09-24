#!/bin/bash

# Test runner script for kronos-stock project

set -e

echo "🧪 Kronos Stock Test Suite"
echo "=========================="

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest not found. Installing test dependencies..."
    pip install -r requirements-test.txt
fi

# Function to run tests with different configurations
run_tests() {
    local test_type=$1
    local test_path=$2
    local extra_args=$3
    
    echo ""
    echo "🔍 Running $test_type tests..."
    echo "Path: $test_path"
    
    if [ -n "$extra_args" ]; then
        pytest $test_path $extra_args
    else
        pytest $test_path
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "unit")
        run_tests "Unit" "tests/models tests/services" "-m unit"
        ;;
    "api")
        run_tests "API" "tests/api" "-m api"
        ;;
    "integration")
        run_tests "Integration" "tests/integration" "-m integration"
        ;;
    "coverage")
        run_tests "Coverage" "tests/" "--cov=app --cov-report=html --cov-report=term"
        echo "📊 Coverage report generated in htmlcov/index.html"
        ;;
    "quick")
        run_tests "Quick" "tests/" "-x --tb=line"
        ;;
    "verbose")
        run_tests "Verbose" "tests/" "-v -s"
        ;;
    "all")
        echo "🏃‍♂️ Running all tests..."
        pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 [unit|api|integration|coverage|quick|verbose|all]"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only"
        echo "  api         - Run API tests only"
        echo "  integration - Run integration tests only"
        echo "  coverage    - Run tests with coverage report"
        echo "  quick       - Run tests and stop on first failure"
        echo "  verbose     - Run tests with verbose output"
        echo "  all         - Run all tests (default)"
        exit 1
        ;;
esac

echo ""
echo "✅ Tests completed!"