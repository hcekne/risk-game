from risk_game.llm_clients.anthropic_client import AnthropicClient

def test_anthropic_thinking():
    """Quick test of Anthropic client with and without thinking"""
    
    print("🧠 Testing Anthropic Client with Thinking Support")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        {"model": 1, "thinking": False, "desc": "Claude Opus 4.1 (no thinking)"},
        {"model": 1, "thinking": True, "desc": "Claude Opus 4.1 (with thinking)"},
        {"model": 4, "thinking": True, "desc": "Claude 3.5 Sonnet (thinking ignored)"}
    ]
    
    simple_prompt = "In Risk, should I attack with 3 armies vs 1 defender? Answer in 30 words."
    
    for test in test_cases:
        print(f"\nTesting: {test['desc']}")
        
        try:
            client = AnthropicClient(
                model_number=test['model'],
                enable_thinking=test['thinking'],
                thinking_budget=2000
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