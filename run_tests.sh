#!/bin/bash

# Audio Player MCP Test Runner
# Runs all test scripts sequentially

echo "🧪 Audio Player MCP Test Suite"
echo "=" 40
echo "Running all tests sequentially..."
echo ""

# Change to the project root directory
cd "$(dirname "$0")" || exit 1

# Array of test files
tests=(
    "tests/test_popular_music.py"
    "tests/test_fuzzy_search.py"
    "tests/test_metadata_search.py"
    "tests/test_full_search_integration.py"
    "tests/test_genre_search.py"
    "tests/test_mcp_vlc.py"
    "tests/test_vlc_playback.py"
)

# Track results
passed=0
failed=0
total=${#tests[@]}

echo "📋 Found $total test scripts to run"
echo ""

# Run each test
for test_file in "${tests[@]}"; do
    echo "🔄 Running $(basename "$test_file")..."
    echo "─────────────────────────────────────"
    
    if [ -f "$test_file" ]; then
        # Run the test and capture exit code
        python3 "$test_file"
        exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            echo "✅ $(basename "$test_file") - PASSED"
            ((passed++))
        else
            echo "❌ $(basename "$test_file") - FAILED (exit code: $exit_code)"
            ((failed++))
        fi
    else
        echo "❌ $(basename "$test_file") - FILE NOT FOUND"
        ((failed++))
    fi
    
    echo ""
done

# Summary
echo "📊 Test Results Summary"
echo "=" 30
echo "Total tests: $total"
echo "Passed: $passed"
echo "Failed: $failed"

if [ $failed -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed successfully!"
    exit 0
else
    echo ""
    echo "⚠️  Some tests failed. Please check the output above."
    exit 1
fi
