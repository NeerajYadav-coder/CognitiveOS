import requests
import json
import time

def test_full_cognitive_pipeline():
    url = "http://localhost:8000/api/v1/process"
    payload = {
        "raw_input": "i am thinking about how to build a company but not just a company like something where people can think together and maybe use ai but not just normal ai like something that feels organic and how does that connect to like ant colonies and software architecture its all very confusing but i want to write a technical paper about it for my blog",
        "session_id": "test-diagnostic-session"
    }

    print("\n🚀 Starting Full Brain Diagnostic...")
    print("------------------------------------")
    
    try:
        start_time = time.time()
        response = requests.post(url, json=payload, timeout=120)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SUCCESS (Total Time: {elapsed:.2f}s)")
            print("\n🧠 ENGINE EXECUTION TRACE:")
            for engine in data.get("execution_trace", []):
                print(f"  • {engine}")
            
            print("\n✨ SYNTHESIZED PROMPT:")
            print(f"  {data.get('synthesized_prompt')}")
            
        else:
            print(f"❌ FAILED: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {str(e)}")

if __name__ == "__main__":
    test_full_cognitive_pipeline()
