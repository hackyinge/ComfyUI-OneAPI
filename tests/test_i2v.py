import requests
import json
import base64
import os
import sys
import uuid

def test_i2v_openai(server_url, image_source, prompt, model="LTX2-SWZ", is_url=False):
    """
    使用 OpenAI 兼容格式测试 I2V
    """
    mode_name = "URL" if is_url else "Base64"
    print(f"\n--- Testing I2V ({mode_name}) via /v1/chat/completions ---")
    print(f"Target Model/Workflow: {model}")
    
    if is_url:
        img_url = image_source
    else:
        with open(image_source, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode('utf-8')
        img_url = f"data:image/png;base64,{img_base64}"
    
    url = f"{server_url}/v1/chat/completions"
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": img_url}}
                ]
            }
        ]
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, json=payload, timeout=600)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse matches OpenAI format:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
            content = result['choices'][0]['message']['content']
            print(f"\nAssistant Response:\n{content}")
            
            if "http" in content:
                print("\nSuccess! Video link found in response.")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    SERVER = "http://127.0.0.1:8188"
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tests/test_i2v.py base64 <image_path> <prompt> [model]")
        print("  python tests/test_i2v.py url <image_url> <prompt> [model]")
        sys.exit(1)
        
    mode = sys.argv[1]
    image_src = sys.argv[2]
    prompt_text = sys.argv[3]
    model_name = sys.argv[4] if len(sys.argv) > 4 else "LTX2-SWZ"
    
    if mode == "base64":
        test_i2v_openai(SERVER, image_src, prompt_text, model=model_name, is_url=False)
    elif mode == "url":
        test_i2v_openai(SERVER, image_src, prompt_text, model=model_name, is_url=True)
    else:
        print(f"Unknown mode: {mode}")
