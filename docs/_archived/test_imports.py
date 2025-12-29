#!/usr/bin/env python3
"""
Test script to verify system setup and imports.
Run this after installing requirements to verify the system is ready.
"""

import sys
import importlib.util

def check_module(module_name, package_name=None):
    """Check if a module is installed."""
    package = package_name or module_name
    spec = importlib.util.find_spec(module_name)
    if spec is None:
        print(f"❌ {package} not installed")
        return False
    else:
        print(f"✅ {package} installed")
        return True

def main():
    print("=" * 60)
    print("Deepfake Detection System - Dependency Check")
    print("=" * 60)
    print()

    required_modules = [
        ('numpy', 'numpy'),
        ('cv2', 'opencv-python'),
        ('PIL', 'Pillow'),
    ]

    optional_modules = [
        ('anthropic', 'anthropic'),
        ('openai', 'openai'),
        ('dotenv', 'python-dotenv'),
    ]

    print("Required Dependencies:")
    all_required = all(check_module(mod, pkg) for mod, pkg in required_modules)

    print("\nOptional Dependencies (for API access):")
    any_llm = any(check_module(mod, pkg) for mod, pkg in optional_modules[:2])
    check_module('dotenv', 'python-dotenv')

    print("\n" + "=" * 60)

    if not all_required:
        print("❌ Some required dependencies are missing.")
        print("\nInstall with:")
        print("  pip install -r requirements.txt")
        sys.exit(1)

    if not any_llm:
        print("⚠️  No LLM API packages installed.")
        print("   You can still use mock mode for testing:")
        print("   python detect.py --video <video> --provider mock")
        print("\n   Or install an LLM package:")
        print("   pip install anthropic  # for Claude")
        print("   pip install openai     # for GPT-4")

    print("\n✅ System is ready!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env and add your API keys")
    print("2. Run: python detect.py --video <path> --provider mock")
    print("3. Or with real API: python detect.py --video <path>")
    print()

if __name__ == '__main__':
    main()
