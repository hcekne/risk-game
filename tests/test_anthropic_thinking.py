import pytest
from risk_game.llm_clients.anthropic_client import AnthropicClient

pytestmark = pytest.mark.live_api

def test_anthropic_thinking():
    """Quick test of Anthropic client with and without thinking"""
    
    print("🧠 Testing Anthropic Client with Thinking Support")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {
            "model_name": "claude-sonnet-4-6",
            "thinking": False,
            "thinking_effort": None,
            "desc": "Claude Sonnet 4.6 (no thinking)",
        },
        {
            "model_name": "claude-sonnet-4-6",
            "thinking": True,
            "thinking_effort": "medium",
            "desc": "Claude Sonnet 4.6 (adaptive thinking)",
        },
        {
            "model_name": "claude-haiku-4-5-20251001",
            "thinking": True,
            "thinking_effort": None,
            "desc": "Claude Haiku 4.5 (manual thinking)",
        },
    ]
    
    simple_prompt = "In Risk, should I attack with 3 armies vs 1 defender? Answer in 30 words."
    
    for test in test_cases:
        print(f"\nTesting: {test['desc']}")
        
        try:
            client = AnthropicClient(
                model_name=test["model_name"],
                enable_thinking=test['thinking'],
                thinking_budget=2000,
                thinking_effort=test["thinking_effort"],
            )
            
            print(f"  Model: {client.model_type}")
            print(f"  Supports thinking: {client.supports_thinking}")
            print(f"  Thinking enabled: {client.enable_thinking}")
            
            response = client.get_chat_completion(simple_prompt)
            print(f"  ✅ Response ({len(response)} chars): {response[:80]}...")
            
        except Exception as e:
            print(f"  ❌ Error: {e}")

if __name__ == "__main__":
    test_anthropic_thinking()
