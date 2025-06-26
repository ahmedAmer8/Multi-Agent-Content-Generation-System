import streamlit as st
import os
import sys
from datetime import datetime
import time
from pathlib import Path
import asyncio

try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())
    
    
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from crewai import Crew, Process
    from tasks import research_task, write_task
    from agents import news_researcher, news_writer
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.error("Make sure all your project files (agents.py, tasks.py, tools.py, crew.py) are in the same directory as this Streamlit app.")
    st.stop()

# Set page config
st.set_page_config(
    page_title="AI Research & Writing Crew",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stAlert > div {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    
    .crew-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    
    .output-container {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .api-key-status {
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem 0;
        font-size: 0.8rem;
    }
    
    .key-found {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .key-missing {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for API keys
if 'use_env_keys' not in st.session_state:
    st.session_state.use_env_keys = True

# Main header
st.markdown('<h1 class="main-header">🤖 AI Research & Writing Crew</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🛠️ Configuration")
    
    # API Keys section
    st.subheader("🔑 API Keys")
    
    # Check for environment variables
    env_google_key = os.getenv('GOOGLE_API_KEY')
    env_serper_key = os.getenv('SERPER_API_KEY')
    
    # API Key status display
    st.markdown("**Environment Status:**")
    
    if env_google_key:
        st.markdown('<div class="api-key-status key-found">✅ Google API Key: Found in environment</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-key-status key-missing">❌ Google API Key: Not found in environment</div>', 
                   unsafe_allow_html=True)
    
    if env_serper_key:
        st.markdown('<div class="api-key-status key-found">✅ Serper API Key: Found in environment</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-key-status key-missing">❌ Serper API Key: Not found in environment</div>', 
                   unsafe_allow_html=True)
    
    st.divider()
    
    # API Key input method selection
    use_env_keys = st.radio(
        "Choose API Key Method:",
        options=[True, False],
        format_func=lambda x: "Use Environment Variables (.env file)" if x else "Enter Keys Manually",
        index=0 if st.session_state.use_env_keys else 1,
        help="Choose whether to use keys from .env file or enter them manually"
    )
    
    st.session_state.use_env_keys = use_env_keys
    
    # Manual API key inputs (only show if not using env vars)
    google_api_key = None
    serper_api_key = None
    
    if not use_env_keys:
        st.markdown("**Manual API Key Entry:**")
        google_api_key = st.text_input(
            "Google API Key", 
            type="password", 
            help="Enter your Google Gemini API key",
            placeholder="Your Google API key here..."
        )
        serper_api_key = st.text_input(
            "Serper API Key", 
            type="password", 
            help="Enter your Serper API key for web search",
            placeholder="Your Serper API key here..."
        )
    
    # Set environment variables based on selection
    if use_env_keys:
        # Use environment variables
        final_google_key = env_google_key
        final_serper_key = env_serper_key
    else:
        # Use manually entered keys
        final_google_key = google_api_key
        final_serper_key = serper_api_key
        
        # Set them in environment for the session
        if google_api_key:
            os.environ['GOOGLE_API_KEY'] = google_api_key
        if serper_api_key:
            os.environ['SERPER_API_KEY'] = serper_api_key
    
    st.divider()
    
    # API Key validation status
    st.subheader("🔍 Current Status")
    
    key_status_container = st.container()
    
    with key_status_container:
        if final_google_key:
            st.success("✅ Google API Key: Ready")
        else:
            st.error("❌ Google API Key: Missing")
            
        if final_serper_key:
            st.success("✅ Serper API Key: Ready")
        else:
            st.error("❌ Serper API Key: Missing")
    
    st.divider()
    
    # Crew Information
    st.subheader("📋 Crew Information")
    st.markdown("""
    **Agents:**
    - 🔬 **Senior Researcher**: Uncovers groundbreaking technologies
    - ✍️ **Writer**: Creates compelling tech stories
    
    **Process:** Sequential execution
    
    **Model:** Google Gemini 1.5 Flash
    
    **Tools:** SerperDev Web Search
    """)
    
    # Quick setup guide
    with st.expander("🚀 Quick Setup Guide"):
        st.markdown("""
        ### Method 1: Environment Variables (Recommended)
        1. Create a `.env` file in your project root
        2. Add your keys:
        ```
        GOOGLE_API_KEY=your_google_key_here
        SERPER_API_KEY=your_serper_key_here
        ```
        3. Restart the app
        
        ### Method 2: Manual Entry
        1. Select "Enter Keys Manually" above
        2. Enter your API keys in the fields
        3. Start using the app
        
        ### Get API Keys:
        - [Google AI Studio](https://makersuite.google.com/app/apikey)
        - [Serper.dev](https://serper.dev/)
        """)

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🚀 Run Research & Writing Task")
    
    # Topic input
    topic = st.text_input(
        "Research Topic",
        value="AI in healthcare",
        help="Enter the topic you want the crew to research and write about",
        placeholder="e.g., AI in healthcare, blockchain technology, quantum computing..."
    )
    
    # Advanced options
    with st.expander("⚙️ Advanced Options"):
        verbose_mode = st.checkbox("Verbose Mode", value=True, help="Show detailed execution logs")
        save_to_file = st.checkbox("Save Output to File", value=True, help="Save the final article to a markdown file")
        
        if save_to_file:
            output_filename = st.text_input(
                "Output Filename", 
                value="new-blog-post.md",
                help="Filename for the generated article"
            )
        
        # Additional configuration options
        st.markdown("**Model Configuration:**")
        col_temp, col_verbose = st.columns(2)
        
        with col_temp:
            temperature = st.slider(
                "Temperature", 
                min_value=0.0, 
                max_value=1.0, 
                value=0.5, 
                step=0.1,
                help="Controls randomness in responses (0=deterministic, 1=creative)"
            )
        
        with col_verbose:
            max_tokens = st.selectbox(
                "Response Length",
                options=["Standard", "Extended", "Comprehensive"],
                help="Controls the length of generated content"
            )

with col2:
    st.header("📊 Execution Status")
    
    # Status indicators
    status_container = st.container()
    
    # Progress tracking
    if 'execution_status' not in st.session_state:
        st.session_state.execution_status = 'ready'
    
    status_colors = {
        'ready': '🟢',
        'running': '🟡',
        'completed': '✅',
        'error': '❌'
    }
    
    with status_container:
        st.markdown(f"**Status:** {status_colors.get(st.session_state.execution_status, '🔘')} {st.session_state.execution_status.title()}")
        
        # Show execution time if available
        if 'execution_time' in st.session_state:
            st.markdown(f"**Duration:** {st.session_state.execution_time:.2f} seconds")
        
        # Show current step if running
        if 'current_step' in st.session_state and st.session_state.execution_status == 'running':
            st.markdown(f"**Current Step:** {st.session_state.current_step}")

# Execution section
st.divider()

# API Key validation before showing the button
keys_ready = final_google_key and final_serper_key

if not keys_ready:
    st.warning("⚠️ Please configure your API keys in the sidebar before proceeding.")
    if not use_env_keys:
        st.info("💡 Tip: You can also create a `.env` file with your keys for easier management.")

# Main execution button
button_disabled = not (topic.strip() and keys_ready)
button_help = "Enter a topic and configure API keys to start" if button_disabled else "Click to start the research and writing process"

if st.button(
    "🚀 Start Research & Writing", 
    type="primary", 
    use_container_width=True,
    disabled=button_disabled,
    help=button_help
):
    if not topic.strip():
        st.error("Please enter a research topic!")
    elif not keys_ready:
        st.error("Please configure your API keys in the sidebar!")
    else:
        st.session_state.execution_status = 'running'
        start_time = time.time()
        
        # Create progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        step_info = st.empty()
        
        try:
            # Initialize crew
            st.session_state.current_step = "Initializing crew..."
            status_text.text("🔧 Initializing crew...")
            step_info.info("Setting up AI agents and tasks")
            progress_bar.progress(10)
            time.sleep(1)  # Brief pause for UX
            
            crew = Crew(
                agents=[news_researcher, news_writer],
                tasks=[research_task, write_task],
                process=Process.sequential,
                verbose=verbose_mode
            )
            
            st.session_state.current_step = "Starting research phase..."
            status_text.text("🔍 Starting research task...")
            step_info.info("Senior Researcher is analyzing the topic and gathering information")
            progress_bar.progress(30)
            
            # Execute crew
            with st.spinner("🤖 Crew is working on your request..."):
                result = crew.kickoff(inputs={'topic': topic})
            
            # Calculate execution time
            execution_time = time.time() - start_time
            st.session_state.execution_time = execution_time
            
            progress_bar.progress(100)
            status_text.text("✅ Execution completed!")
            step_info.success(f"Research and writing completed in {execution_time:.2f} seconds!")
            st.session_state.execution_status = 'completed'
            st.session_state.current_step = "Completed"
            
            # Display results
            st.success("🎉 Research and writing completed successfully!")
            
            # Show the result
            st.header("📝 Generated Article")
            st.markdown("---")
            
            # Display the result in a nice container
            with st.container():
                st.markdown(str(result))
            
            # File handling
            if save_to_file:
                try:
                    # Check if output file was created by the task
                    if os.path.exists(output_filename):
                        st.success(f"📁 Article automatically saved to: {output_filename}")
                        
                        # Provide download button
                        with open(output_filename, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                    else:
                        # Create the file manually if it wasn't created by the task
                        file_content = str(result)
                        with open(output_filename, 'w', encoding='utf-8') as f:
                            f.write(file_content)
                        st.success(f"📁 Article saved to: {output_filename}")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Article",
                        data=file_content,
                        file_name=output_filename,
                        mime="text/markdown",
                        help="Download the generated article as a markdown file"
                    )
                    
                except Exception as file_error:
                    st.warning(f"File save error: {str(file_error)}")
                    # Still provide download option
                    st.download_button(
                        label="📥 Download Article",
                        data=str(result),
                        file_name=output_filename,
                        mime="text/markdown"
                    )
            
            # Store result in session state for later access
            st.session_state.last_result = str(result)
            st.session_state.last_topic = topic
            st.session_state.last_execution_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        except Exception as e:
            st.session_state.execution_status = 'error'
            st.session_state.current_step = "Error occurred"
            
            # More detailed error handling
            error_msg = str(e)
            st.error(f"❌ An error occurred: {error_msg}")
            
            # Provide specific guidance based on error type
            if "api key" in error_msg.lower():
                st.error("🔑 API Key Error: Please check your API keys and try again.")
                st.info("💡 Make sure your API keys are valid and have sufficient quota.")
            elif "serper" in error_msg.lower():
                st.error("🔍 Search Error: Issue with web search functionality.")
                st.info("💡 Check your Serper API key and internet connection.")
            elif "google" in error_msg.lower() or "gemini" in error_msg.lower():
                st.error("🤖 Model Error: Issue with Google Gemini API.")
                st.info("💡 Check your Google API key and quota limits.")
            else:
                st.error("🔧 General Error: Please check your configuration and try again.")
            
            # Show detailed error in expander for debugging
            with st.expander("🔍 Detailed Error Information"):
                st.code(error_msg)

# Display previous results if available
if 'last_result' in st.session_state:
    st.divider()
    st.header("📚 Previous Results")
    
    with st.expander(f"Last execution: {st.session_state.get('last_topic', 'Unknown')} - {st.session_state.get('last_execution_time', 'Unknown time')}"):
        st.markdown(st.session_state.last_result)
        
        # Add download button for previous result
        if st.session_state.last_result:
            st.download_button(
                label="📥 Download Previous Result",
                data=st.session_state.last_result,
                file_name=f"previous-article-{st.session_state.get('last_topic', 'unknown').replace(' ', '-')}.md",
                mime="text/markdown"
            )

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Built with ❤️ using Streamlit, CrewAI, and Google Gemini</p>
    <p><strong>🔧 Setup Complete!</strong> Your AI research crew is ready to work!</p>
</div>
""", unsafe_allow_html=True)

# Instructions panel
with st.expander("📖 Instructions & Setup"):
    st.markdown("""
    ### 🚀 How to use this app:
    
    1. **Set up API Keys**: 
       - **Option A**: Create a `.env` file with your keys (recommended)
       - **Option B**: Enter keys manually in the sidebar
    2. **Choose a Topic**: Enter the research topic you want to explore
    3. **Configure Options**: Adjust settings in the Advanced Options if needed
    4. **Run the Crew**: Click the "Start Research & Writing" button
    5. **View Results**: The generated article will appear below
    6. **Download**: Save your article as a markdown file
    
    ### 🔑 Required API Keys:
    
    - **Google API Key**: Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)
    - **Serper API Key**: Get it from [Serper.dev](https://serper.dev/)
    
    ### 📋 What this app does:
    
    1. **Research Phase**: The Senior Researcher agent searches for the latest information about your topic
    2. **Analysis Phase**: Analyzes trends, pros/cons, and market opportunities
    3. **Writing Phase**: The Writer agent creates a compelling article based on the research
    4. **Output**: You get a well-structured markdown article ready for publication
    
    ### 🛠️ Project Structure:
    
    - `agents.py`: Defines the AI agents (Researcher & Writer)
    - `tasks.py`: Defines the research and writing tasks
    - `tools.py`: Sets up the web search tool
    - `crew.py`: Orchestrates the multi-agent workflow
    - `app.py`: This Streamlit web application
    - `requirements.txt`: Python dependencies
    - `.env`: Your API keys (create this file)
    
    ### 💡 Tips:
    
    - Use specific, focused topics for better results
    - The verbose mode shows detailed execution logs
    - Articles are automatically saved as markdown files
    - You can download previous results anytime
    """)

# Add system info in a collapsible section
with st.expander("🔧 System Information"):
    st.markdown(f"""
    **Application Status:**
    - Streamlit Version: {st.__version__}
    - Python Version: {sys.version.split()[0]}
    - Current Working Directory: {os.getcwd()}
    - Environment Variables Status:
      - GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not Set'}
      - SERPER_API_KEY: {'✅ Set' if os.getenv('SERPER_API_KEY') else '❌ Not Set'}
    
    **Session State:**
    - Execution Status: {st.session_state.execution_status}
    - API Key Method: {'Environment Variables' if st.session_state.use_env_keys else 'Manual Entry'}
    - Previous Results Available: {'Yes' if 'last_result' in st.session_state else 'No'}
    """)