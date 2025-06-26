"""
Tools configuration for AI Research & Writing Crew
Handles web search functionality using SerperDev API
"""

from dotenv import load_dotenv
import os
import sys

# Load environment variables from .env file
load_dotenv()

def setup_serper_tool():
    """
    Set up the SerperDev tool with proper error handling
    """
    # Get API key from environment
    serper_api_key = os.getenv('SERPER_API_KEY')
    
    if not serper_api_key:
        print("⚠️  Warning: SERPER_API_KEY not found in environment variables")
        print("   Please set your Serper API key in:")
        print("   1. .env file: SERPER_API_KEY=your_key_here")
        print("   2. Or set it manually in the Streamlit sidebar")
        print("   Get your key from: https://serper.dev/")
    else:
        print("✅ Serper API key loaded successfully")
    
    # Set the environment variable for the tool
    os.environ['SERPER_API_KEY'] = serper_api_key or ""
    
    try:
        from crewai_tools import SerperDevTool
        
        # Initialize the tool
        tool = SerperDevTool()
        print("✅ SerperDev tool initialized successfully")
        return tool
        
    except ImportError as e:
        print(f"❌ Error importing SerperDevTool: {e}")
        print("   Please install crewai-tools: pip install crewai-tools")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error initializing SerperDev tool: {e}")
        print("   Please check your SERPER_API_KEY")
        # Return None so the app can handle the error gracefully
        return None

def validate_api_keys():
    """
    Validate that all required API keys are present
    """
    required_keys = {
        'GOOGLE_API_KEY': 'Google Gemini API',
        'SERPER_API_KEY': 'Serper Web Search API'
    }
    
    missing_keys = []
    
    for key, description in required_keys.items():
        if not os.getenv(key):
            missing_keys.append(f"{key} ({description})")
    
    if missing_keys:
        print("\n⚠️  Missing API Keys:")
        for key in missing_keys:
            print(f"   - {key}")
        print("\nPlease set these in your .env file or Streamlit sidebar")
        return False
    
    print("✅ All required API keys are present")
    return True

# Initialize the tool
tool = setup_serper_tool()

# Export for use in other modules
__all__ = ['tool', 'setup_serper_tool', 'validate_api_keys']

if __name__ == "__main__":
    # Test the tool setup when run directly
    print("Testing tool setup...")
    validate_api_keys()
    if tool:
        print("✅ Tools setup completed successfully")
    else:
        print("❌ Tools setup failed")