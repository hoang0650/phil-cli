#!/usr/bin/env python3
"""
Test script to verify Phil-AI connection and functionality
"""
import asyncio
import httpx
import yaml
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config

async def test_phil_ai_connection():
    """Test connection to Phil-AI models"""
    print("🧪 Testing Phil-AI Connection...")
    
    # Get model configuration
    model_config = Config.get_model_config()
    print(f"📋 Model Config: {model_config}")
    
    # Test each model endpoint
    test_results = {}
    
    # Test Brain Model
    try:
        brain_endpoint = model_config["brain"]["endpoint"]
        brain_model = model_config["brain"]["model_name"]
        print(f"🧠 Testing Brain Model: {brain_model} at {brain_endpoint}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{brain_endpoint}/chat/completions",
                json={
                    "model": brain_model,
                    "messages": [
                        {"role": "system", "content": "You are a helpful AI assistant."},
                        {"role": "user", "content": "Hello, can you hear me?"}
                    ],
                    "max_tokens": 50
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                test_results["brain"] = {
                    "status": "connected",
                    "response": result["choices"][0]["message"]["content"][:100] + "..."
                }
                print("✅ Brain model connected successfully")
            else:
                test_results["brain"] = {
                    "status": "failed",
                    "error": f"Status {response.status_code}: {response.text}"
                }
                print(f"❌ Brain model failed: {response.status_code}")
                
    except Exception as e:
        test_results["brain"] = {
            "status": "error",
            "error": str(e)
        }
        print(f"❌ Brain model error: {e}")
    
    # Test Vision Model
    try:
        vision_endpoint = model_config["vision"]["endpoint"]
        vision_model = model_config["vision"]["model_name"]
        print(f"👁️ Testing Vision Model: {vision_model} at {vision_endpoint}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{vision_endpoint}/chat/completions",
                json={
                    "model": vision_model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "What do you see?"},
                                {"type": "image_url", "image_url": {"url": "https://via.placeholder.com/150"}}
                            ]
                        }
                    ],
                    "max_tokens": 50
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                test_results["vision"] = {
                    "status": "connected",
                    "response": result["choices"][0]["message"]["content"][:100] + "..."
                }
                print("✅ Vision model connected successfully")
            else:
                test_results["vision"] = {
                    "status": "failed",
                    "error": f"Status {response.status_code}: {response.text}"
                }
                print(f"❌ Vision model failed: {response.status_code}")
                
    except Exception as e:
        test_results["vision"] = {
            "status": "error",
            "error": str(e)
        }
        print(f"❌ Vision model error: {e}")
    
    # Test Audio Models (Ears & Mouth)
    try:
        whisper_endpoint = model_config["ears"]["endpoint"]
        print(f"👂 Testing Ears Model (Whisper) at {whisper_endpoint}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{whisper_endpoint}/health")
            
            if response.status_code == 200:
                test_results["ears"] = {
                    "status": "connected",
                    "health": response.json()
                }
                print("✅ Ears model (Whisper) connected successfully")
            else:
                test_results["ears"] = {
                    "status": "failed",
                    "error": f"Status {response.status_code}"
                }
                print(f"❌ Ears model failed: {response.status_code}")
                
    except Exception as e:
        test_results["ears"] = {
            "status": "error",
            "error": str(e)
        }
        print(f"❌ Ears model error: {e}")
    
    # Test TTS Model
    try:
        tts_endpoint = model_config["mouth"]["endpoint"]
        print(f"🗣️ Testing Mouth Model (F5-TTS) at {tts_endpoint}")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{tts_endpoint}/health")
            
            if response.status_code == 200:
                test_results["mouth"] = {
                    "status": "connected",
                    "health": response.json()
                }
                print("✅ Mouth model (F5-TTS) connected successfully")
            else:
                test_results["mouth"] = {
                    "status": "failed",
                    "error": f"Status {response.status_code}"
                }
                print(f"❌ Mouth model failed: {response.status_code}")
                
    except Exception as e:
        test_results["mouth"] = {
            "status": "error",
            "error": str(e)
        }
        print(f"❌ Mouth model error: {e}")
    
    return test_results

async def test_huggingface_upload():
    """Test HuggingFace upload capability"""
    print("\n📦 Testing HuggingFace Upload Capability...")
    
    try:
        # Check if HF_TOKEN is available
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            print("⚠️  HF_TOKEN not found in environment")
            return {"status": "warning", "message": "HF_TOKEN not set"}
        
        # Test token validity
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://huggingface.co/api/whoami",
                headers={"Authorization": f"Bearer {hf_token}"}
            )
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ HuggingFace token valid for user: {user_info.get('name', 'unknown')}")
                return {"status": "valid", "user": user_info.get('name')}
            else:
                print(f"❌ HuggingFace token invalid: {response.status_code}")
                return {"status": "invalid", "error": response.status_code}
                
    except Exception as e:
        print(f"❌ HuggingFace test error: {e}")
        return {"status": "error", "error": str(e)}

async def main():
    """Main test function"""
    print("🚀 Starting Phil-AI System Test...")
    print("=" * 50)
    
    # Test connection to models
    connection_results = await test_phil_ai_connection()
    
    # Test HuggingFace upload capability
    hf_results = await test_huggingface_upload()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print("=" * 50)
    
    print("\n🔌 Model Connections:")
    for model, result in connection_results.items():
        status = "✅" if result["status"] == "connected" else "❌"
        print(f"{status} {model.capitalize()}: {result['status']}")
        if "error" in result:
            print(f"   Error: {result['error']}")
    
    print(f"\n📦 HuggingFace: {hf_results['status']}")
    if "user" in hf_results:
        print(f"   User: {hf_results['user']}")
    
    # Overall status
    connected_models = sum(1 for r in connection_results.values() if r["status"] == "connected")
    total_models = len(connection_results)
    
    print(f"\n🎯 Overall: {connected_models}/{total_models} models connected")
    
    if connected_models == total_models and hf_results["status"] == "valid":
        print("✅ Phil-AI system is ready for training and deployment!")
        return True
    else:
        print("⚠️  Some components need attention. Check the errors above.")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)