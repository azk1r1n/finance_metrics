#!/bin/bash
# Quick test script to verify everything works

echo "=================================================="
echo " Testing Data Helper Module"
echo "=================================================="
echo ""

cd "$(dirname "$0")"

echo "[1/3] Testing VIX Sentiment (FREE - should work)"
echo "--------------------------------------------------"
python vix_sentiment.py
echo ""

echo "[2/3] Testing API Access Levels"
echo "--------------------------------------------------"
python test_api_access.py
echo ""

echo "[3/3] Testing Integration Example"
echo "--------------------------------------------------"
python integrate_with_custom_metrics.py
echo ""

echo "=================================================="
echo " Test Complete!"
echo "=================================================="
echo ""
echo "Summary:"
echo "- VIX Sentiment: Should work (FREE)"
echo "- API Access: Stocks work, Options require upgrade"
echo "- Integration: Shows how to use in CustomMetrics"
echo ""
echo "Next: Read QUICK_START.md to get started!"
echo "=================================================="
