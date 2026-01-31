#!/usr/bin/env python3
"""
Test script for Ollama AI integration
Verifies that Ollama service is working correctly
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.ollama_service import OllamaService
from loguru import logger

def test_ollama_connection():
    """Test basic Ollama connection"""
    print("=" * 60)
    print("Testing Ollama AI Integration")
    print("=" * 60)
    
    # Initialize service
    print("\n1. Initializing Ollama Service...")
    ollama = OllamaService()
    
    if not ollama.is_available():
        print("❌ Ollama is not available")
        print("   Please ensure Ollama is running:")
        print("   - Local: ollama serve")
        print("   - Or set OLLAMA_BASE_URL environment variable")
        return False
    
    print("✅ Ollama service is available")
    
    # Test basic generation
    print("\n2. Testing basic text generation...")
    response = ollama.generate(
        "What is 2+2? Answer in one sentence.",
        temperature=0.7
    )
    
    if response:
        print(f"✅ Generation successful: {response[:100]}...")
    else:
        print("❌ Generation failed")
        return False
    
    # Test chat
    print("\n3. Testing chat interface...")
    messages = [
        {"role": "user", "content": "Hello! Can you help with trading analysis?"}
    ]
    chat_response = ollama.chat(messages)
    
    if chat_response:
        print(f"✅ Chat successful: {chat_response[:100]}...")
    else:
        print("❌ Chat failed")
        return False
    
    # Test trading analysis
    print("\n4. Testing trading performance analysis...")
    trade_data = [
        {"pnl": 10.5, "win": True},
        {"pnl": -5.2, "win": False},
        {"pnl": 8.3, "win": True},
    ]
    performance_metrics = {
        "win_rate": 0.67,
        "total_trades": 3,
        "net_pnl": 13.6,
        "profit_factor": 2.5
    }
    
    analysis = ollama.analyze_trading_performance(trade_data, performance_metrics)
    if analysis:
        print("✅ Trading analysis successful")
        print(f"   Analysis: {str(analysis)[:200]}...")
    else:
        print("⚠️  Trading analysis returned None (may be normal)")
    
    # Test pattern detection
    print("\n5. Testing market pattern detection...")
    market_data = {
        "current_price": 50000,
        "high_24h": 51000,
        "low_24h": 49000,
        "volume_24h": 1000000
    }
    indicators = {
        "rsi": {"value": 65},
        "macd": "bullish",
        "bb_upper": 51000,
        "bb_lower": 49000
    }
    
    patterns = ollama.detect_market_patterns(market_data, indicators)
    if patterns:
        print(f"✅ Pattern detection successful: {len(patterns)} patterns found")
        for pattern in patterns:
            print(f"   - {pattern.get('pattern', 'Unknown')}: {pattern.get('action', 'N/A')}")
    else:
        print("⚠️  No patterns detected (may be normal)")
    
    # List available models
    print("\n6. Checking available models...")
    models = ollama.get_available_models()
    if models:
        print(f"✅ Found {len(models)} models:")
        for model in models:
            print(f"   - {model}")
    else:
        print("⚠️  Could not list models")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    try:
        success = test_ollama_connection()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)








