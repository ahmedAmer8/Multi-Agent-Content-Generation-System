"""
Enhanced Crew Configuration for AI Research & Writing
Supports both standalone execution and integration with Streamlit app
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_requirements():
    """Check if all requirements are met before running the crew"""
    try:
        from crewai import Crew, Process
        from tasks import research_task, write_task
        from agents import news_researcher, news_writer
        from tools import validate_api_keys
        
        print("✅ All modules imported successfully")
        
        # Validate API keys
        if not validate_api_keys():
            print("❌ API key validation failed")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required packages are installed:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def create_crew(verbose=True):
    """Create and configure the crew"""
    try:
        from crewai import Crew, Process
        from tasks import research_task, write_task
        from agents import news_researcher, news_writer
        
        crew = Crew(
            agents=[news_researcher, news_writer],
            tasks=[research_task, write_task],
            process=Process.sequential,
            verbose=verbose
        )
        
        print("✅ Crew created successfully")
        return crew
        
    except Exception as e:
        print(f"❌ Error creating crew: {e}")
        return None

def run_crew(topic, verbose=True, output_file=None):
    """Run the crew with the specified topic"""
    print(f"\n🚀 Starting AI Research & Writing Crew")
    print(f"📝 Topic: {topic}")
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Check requirements
    if not check_requirements():
        return None
    
    # Create crew
    crew = create_crew(verbose=verbose)
    if not crew:
        return None
    
    try:
        # Execute the crew
        print("🔄 Executing crew tasks...")
        start_time = datetime.now()
        
        result = crew.kickoff(inputs={'topic': topic})
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        print("-" * 50)
        print(f"✅ Crew execution completed!")
        print(f"⏱️  Execution time: {execution_time:.2f} seconds")
        print(f"🕐 Completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Save to file if specified
        if output_file:
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(str(result))
                print(f"💾 Result saved to: {output_file}")
            except Exception as e:
                print(f"⚠️  Warning: Could not save to file: {e}")
        
        return result
        
    except KeyboardInterrupt:
        print("\n⏹️  Execution interrupted by user")
        return None
    except Exception as e:
        print(f"❌ Error during execution: {e}")
        return None

def main():
    """Main function for standalone execution"""
    print("🤖 AI Research & Writing Crew - Standalone Mode")
    print("=" * 50)
    
    # Default configuration
    default_topic = "AI in healthcare"
    default_output_file = "new-blog-post.md"
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        try:
            topic = input(f"Enter research topic (default: {default_topic}): ").strip()
            if not topic:
                topic = default_topic
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return
    
    # Get output file preference
    try:
        save_file = input(f"Save to file? (y/n, default: y): ").strip().lower()
        output_file = default_output_file if save_file != 'n' else None
        
        if output_file and save_file == 'y':
            custom_file = input(f"Output filename (default: {default_output_file}): ").strip()
            if custom_file:
                output_file = custom_file
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return
    
    # Run the crew
    result = run_crew(topic, verbose=True, output_file=output_file)
    
    if result:
        print("\n📄 Generated Article:")
        print("=" * 50)
        print(str(result))
        print("=" * 50)
        print("\n✨ Task completed successfully!")
        
        # Check if file was created
        if output_file and os.path.exists(output_file):
            print(f"📁 Article saved to: {output_file}")
        
    else:
        print("\n❌ Task failed. Please check the errors above.")

# Configuration for direct import
if __name__ == "__main__":
    main()
else:
    # When imported, create the crew for use in other modules
    try:
        from crewai import Crew, Process
        from tasks import research_task, write_task
        from agents import news_researcher, news_writer
        
        crew = Crew(
            agents=[news_researcher, news_writer],
            tasks=[research_task, write_task],
            process=Process.sequential,
            verbose=True
        )
        
        print("✅ Crew module loaded successfully")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize crew module: {e}")
        crew = None