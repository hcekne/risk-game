import time
import statistics
from typing import List, Dict, Tuple
from risk_game.llm_clients.openai_client import OpenAIClient
from risk_game.player_agent import PlayerAgent

def test_model_response_quality_and_speed():
    """Test response quality and speed across different OpenAI models with appropriate reasoning settings"""
    
    # Initialize models with appropriate reasoning settings
    model_configs = [
        {"number": 1, "name": "gpt-5", "reasoning": "minimal", "description": "GPT-5 with minimal reasoning"},
        #{"number": 2, "name": "gpt-5-mini", "reasoning": "low", "description": "GPT-5-Mini with low reasoning"},
        #{"number": 4, "name": "gpt-4.1", "reasoning": None, "description": "GPT-4.1 (no reasoning)"},
        {"number": 5, "name": "gpt-5-chat-latest", "reasoning": None, "description": "GPT-5-Chat-Latest (no reasoning)"}
    ]
    
    # Create clients and players
    clients = {}
    players = {}
    
    for config in model_configs:
        if config["reasoning"]:
            client = OpenAIClient(
                model_number=config["number"], 
                use_responses_api=True, 
                reasoning_effort=config["reasoning"]
            )
        else:
            client = OpenAIClient(
                model_number=config["number"], 
                use_responses_api=True
            )
        
        clients[config["number"]] = client
        players[config["number"]] = PlayerAgent(f"Model_{config['number']}_Player", client)
    
    # Test prompts - Risk strategy questions
    test_prompts = [
        "You control 8 territories in Risk. Should you attack aggressively or consolidate? Explain in 50 words.",
        "In Risk, you have 3 cards and can trade for +6 troops. Your opponent is weak. Trade now or wait? Why?",
        "You're attacking with 3 armies vs 2 defenders in Risk. What are your odds and should you attack?",
        "In Risk endgame, you need 2 more territories to win. Plan your attack strategy in 40 words.",
        "You control Australia (+2 bonus) but Europe is available. Switch focus or consolidate? Justify briefly."
    ]
    
    # Initialize results storage
    results = {}
    for config in model_configs:
        results[config["number"]] = {
            "config": config,
            "responses": [], 
            "times": [], 
            "avg_length": [],
            "errors": []
        }
    
    print("🎲 Testing Model Comparison: OpenAI Models with Reasoning Variants")
    print("=" * 70)
    
    for config in model_configs:
        reasoning_info = f" ({config['reasoning']} reasoning)" if config['reasoning'] else " (no reasoning)"
        print(f"Model {config['number']}: {config['name']}{reasoning_info}")
    
    print("=" * 70)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\nTest {i}: {prompt[:60]}...")
        
        for config in model_configs:
            model_num = config["number"]
            model_name = config["name"]
            reasoning_info = f" ({config['reasoning']})" if config['reasoning'] else " (no reasoning)"
            
            print(f"  Testing Model {model_num} ({model_name}{reasoning_info})...")
            
            start_time = time.time()
            try:
                response = clients[model_num].get_chat_completion(prompt)
                elapsed_time = time.time() - start_time
                
                results[model_num]["responses"].append(response)
                results[model_num]["times"].append(elapsed_time)
                results[model_num]["avg_length"].append(len(response))
                
                print(f"    ✅ Completed in {elapsed_time:.2f}s ({len(response)} chars)")
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                error_msg = str(e)
                
                results[model_num]["responses"].append("")
                results[model_num]["times"].append(0)
                results[model_num]["avg_length"].append(0)
                results[model_num]["errors"].append(error_msg)
                
                print(f"    ❌ Failed after {elapsed_time:.2f}s: {error_msg[:50]}...")
        
        # Brief pause between test rounds
        time.sleep(1)
    
    # Calculate and display statistics
    print("\n" + "=" * 70)
    print("📊 RESULTS SUMMARY")
    print("=" * 70)
    
    for config in model_configs:
        model_num = config["number"]
        data = results[model_num]
        
        valid_times = [t for t in data["times"] if t > 0]
        valid_lengths = [l for l in data["avg_length"] if l > 0]
        
        reasoning_info = f" with {config['reasoning']} reasoning" if config['reasoning'] else " (no reasoning)"
        
        print(f"\nMODEL {model_num}: {config['name']}{reasoning_info}")
        print(f"  Successful responses: {len(valid_times)}/{len(test_prompts)}")
        print(f"  Failed responses: {len(data['errors'])}")
        
        if valid_times:
            print(f"  Average response time: {statistics.mean(valid_times):.2f}s")
            print(f"  Fastest response: {min(valid_times):.2f}s")
            print(f"  Slowest response: {max(valid_times):.2f}s")
        
        if valid_lengths:
            print(f"  Average response length: {statistics.mean(valid_lengths):.0f} characters")
            print(f"  Shortest response: {min(valid_lengths)} characters")
            print(f"  Longest response: {max(valid_lengths)} characters")
        
        if data["errors"]:
            print(f"  Sample error: {data['errors'][0][:80]}...")
    
    # Performance comparison
    print(f"\n🏁 PERFORMANCE COMPARISON:")
    valid_model_times = {}
    
    for config in model_configs:
        model_num = config["number"]
        valid_times = [t for t in results[model_num]["times"] if t > 0]
        if valid_times:
            valid_model_times[model_num] = statistics.mean(valid_times)
            reasoning_info = f" ({config['reasoning']})" if config['reasoning'] else ""
            print(f"  Model {model_num}{reasoning_info}: {valid_model_times[model_num]:.2f}s average")
    
    if len(valid_model_times) > 1:
        fastest_model = min(valid_model_times.keys(), key=lambda k: valid_model_times[k])
        fastest_time = valid_model_times[fastest_model]
        
        print(f"\n🥇 FASTEST: Model {fastest_model} ({fastest_time:.2f}s average)")
        
        print("\nSpeed ratios (vs fastest):")
        for model_num, avg_time in valid_model_times.items():
            if model_num != fastest_model:
                ratio = avg_time / fastest_time
                print(f"  Model {model_num}: {ratio:.1f}x slower")
    
    # Show sample responses for comparison
    print(f"\n💬 SAMPLE RESPONSE COMPARISON (Test 1):")
    print(f"Prompt: {test_prompts[0]}")
    
    for config in model_configs:
        model_num = config["number"]
        if results[model_num]["responses"] and results[model_num]["responses"][0]:
            reasoning_info = f" ({config['reasoning']})" if config['reasoning'] else ""
            response_preview = results[model_num]["responses"][0][:150]
            print(f"\nModel {model_num}{reasoning_info}:")
            print(f"  {response_preview}...")
        else:
            print(f"\nModel {model_num}: No valid response")
    
    return results

def test_parsing_accuracy():
    """Test how well each model follows the Risk game response format"""
    
    # Create clients with appropriate reasoning settings
    test_configs = [
        {"number": 1, "reasoning": "minimal"},
        #{"number": 2, "reasoning": "low"},
        #{"number": 4, "reasoning": None},
        {"number": 5, "reasoning": None}
    ]
    
    players = {}
    for config in test_configs:
        if config["reasoning"]:
            client = OpenAIClient(
                model_number=config["number"], 
                use_responses_api=True, 
                reasoning_effort=config["reasoning"]
            )
        else:
            client = OpenAIClient(
                model_number=config["number"], 
                use_responses_api=True
            )
        
        players[config["number"]] = PlayerAgent(f"Model_{config['number']}_Player", client)
    
    # Test format compliance with attack move format
    attack_prompt = """
    You are playing Risk. Choose an attack move in this EXACT format:

    Attack Opponent Territory:|||Brazil, 3|||
    From Territory:###Argentina###
    Reasoning:+++Want to control South America+++

    Your territories: Argentina (5 troops), Chile (3 troops)
    Enemy territories: Brazil (2 troops), Peru (1 troop)
    """
    
    print("\n🎯 Testing Response Format Parsing")
    print("=" * 50)
    
    for config in test_configs:
        model_num = config["number"]
        reasoning_info = f" ({config['reasoning']} reasoning)" if config['reasoning'] else " (no reasoning)"
        
        print(f"\nTesting Model {model_num}{reasoning_info}:")
        
        try:
            response = players[model_num].send_message(attack_prompt)
            print(f"Raw response: {response[:120]}...")
            
            # Try to parse the response
            moves, reasoning, from_territory = players[model_num].parse_response_text(response)
            
            print(f"Parsed successfully:")
            print(f"  Moves: {moves}")
            print(f"  From Territory: {from_territory}")
            print(f"  Reasoning: {reasoning}")
            
            # Check format compliance
            if moves and moves[0].get('territory_name') and from_territory and reasoning:
                print("  ✅ Format compliance: GOOD")
            else:
                print("  ❌ Format compliance: POOR")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")

def test_reasoning_impact():
    """Compare reasoning vs non-reasoning performance on the same model family"""
    
    print("\n🧠 Testing Reasoning Impact")
    print("=" * 50)
    
    # Compare GPT-5 models with different reasoning levels
    reasoning_tests = [
        {"model": 1, "reasoning": "minimal", "label": "GPT-5 (minimal reasoning)"},
        {"model": 5, "reasoning": None, "label": "GPT-5-Chat-Latest (no reasoning)"}
    ]
    
    complex_prompt = """
    In Risk, you're in a 4-player endgame. Player A has 25 territories (strong in Asia), 
    Player B has 15 territories (controls South America + Australia), Player C has 2 territories. 
    You have 8 territories in Africa and North America. 
    
    You have 4 cards (can trade for +10 troops next turn). Player A just got +25 troops from a set.
    
    What's your optimal strategy for the next 2 turns? Consider alliances, timing, and risk/reward.
    """
    
    for test in reasoning_tests:
        print(f"\nTesting {test['label']}:")
        
        if test['reasoning']:
            client = OpenAIClient(test['model'], use_responses_api=True, reasoning_effort=test['reasoning'])
        else:
            client = OpenAIClient(test['model'], use_responses_api=True)
        
        start_time = time.time()
        try:
            response = client.get_chat_completion(complex_prompt)
            elapsed_time = time.time() - start_time
            
            print(f"  Time: {elapsed_time:.2f}s")
            print(f"  Length: {len(response)} characters")
            print(f"  Preview: {response[:200]}...")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")

if __name__ == "__main__":
    print("🧪 Starting Comprehensive Model Comparison Tests")
    print("Testing OpenAI Models with Reasoning Capabilities")
    print("Models: GPT-5 (minimal), GPT-5-Mini (low), GPT-4.1 (none), GPT-5-Chat-Latest (none)")
    
    try:
        # Test response quality and speed across all models
        results = test_model_response_quality_and_speed()
        
        # Test parsing accuracy
        test_parsing_accuracy()
        
        # Test reasoning impact
        test_reasoning_impact()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure your OpenAI API key is set and you have access to these models.")