"""CivicSync: An interactive Streamlit dashboard for the Indian election process.

This application provides a top-down, heavy-UI experience to help first-time
voters understand the election structure, timelines, and registration steps.
"""

import os
import streamlit as st
from google import genai
from google.genai import types
from google.genai import errors
from dotenv import load_dotenv

# --- Constants ---
STATES_LIST: list[str] = [
    "Select a State...", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
    "Chhattisgarh", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", 
    "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", 
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", 
    "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal", "Delhi", 
    "Jammu and Kashmir", "Puducherry"
]

MODEL_NAME: str = "gemini-2.5-flash"


def setup_page() -> None:
    """Configures the Streamlit page layout and custom CSS styling."""
    st.set_page_config(
        page_title="Civic Journey",
        page_icon="🗺️",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    st.markdown("""
        <style>
            [data-testid="collapsedControl"] { display: none; }
            section[data-testid="stSidebar"] { display: none; }
            #MainMenu { visibility: hidden; }
            footer { visibility: hidden; }
            header { visibility: hidden; }
            
            .main { background-color: #fafafa; }
            h1 { color: #1f2937; text-align: center; }
            .subtitle { text-align: center; color: #6b7280; margin-bottom: 30px; }
            .stTabs [data-baseweb="tab-list"] { gap: 15px; margin-top: 20px; }
            .stTabs [data-baseweb="tab"] {
                height: 45px;
                white-space: pre-wrap;
                background-color: #f3f4f6;
                border-radius: 6px 6px 0px 0px;
                padding: 10px 20px;
                font-weight: 500;
            }
        </style>
    """, unsafe_allow_html=True)


def init_api() -> str:
    """Initializes the Google Gemini API client and retrieves the API key.
    
    Returns:
        str: The Google API Key.
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.error("⚠️ GOOGLE_API_KEY not found in environment.")
        st.stop()
        
    if "client" not in st.session_state:
        st.session_state.client = genai.Client(api_key=api_key)
        
    return str(api_key)


@st.cache_data(show_spinner=False, ttl=3600)
def generate_civic_content(prompt_text: str, _api_key: str) -> str:
    """Generates AI content using the Gemini model via Streamlit caching.

    Args:
        prompt_text (str): The prompt to send to the Gemini model.
        _api_key (str): The Google API key (underscored to prevent hashing).

    Returns:
        str: The generated text response.
        
    Raises:
        ValueError: If the generated text response is None.
    """
    temp_client = genai.Client(api_key=_api_key)
    
    # Advanced SDK usage: Explicit configuration
    config = types.GenerateContentConfig(
        temperature=0.7,
    )
    
    response = temp_client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt_text,
        config=config
    )
    
    if response.text is None:
        raise ValueError("Received empty response from the model.")
        
    return response.text


def render_header() -> tuple[str, str]:
    """Renders the global setup UI (title and inputs).

    Returns:
        tuple[str, str]: A tuple containing the selected state and voter status.
    """
    st.title("Civic Journey 🇮🇳")
    st.markdown("<div class='subtitle'>Your interactive guide to the Indian election process!</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        selected_state = st.selectbox(
            "Select your State:", 
            STATES_LIST,
            help="Choose the state where you reside or intend to vote."
        )

    with col2:
        st.markdown("<div style='margin-bottom: 5px;'>Are you a First-Time Voter?</div>", unsafe_allow_html=True)
        is_first_time = st.radio(
            "Are you a First-Time Voter?", 
            ["Yes", "No"], 
            horizontal=True, 
            label_visibility="collapsed",
            help="Select Yes if you have never registered to vote before."
        )

    st.markdown("---")
    
    # Cast to str to satisfy type hints since Streamlit's return types are Any
    return str(selected_state), str(is_first_time)


def handle_generation_error(e: Exception) -> None:
    """Handles API generation errors gracefully for the UI.
    
    Args:
        e (Exception): The caught exception.
    """
    if isinstance(e, errors.APIError):
        if "429" in str(e) or "quota" in str(e).lower():
            st.error("⚠️ We are experiencing high traffic (Quota limit reached). Please try again in a minute!")
        else:
            st.error("⚠️ An API error occurred while contacting the server. Please try again.")
    else:
        st.error("⚠️ An unexpected error occurred. Please try again later.")
        # Log securely (e.g., to a console/file) instead of showing raw traceback
        print(f"Secure Log - Unexpected Error: {e}")


def render_process_tab(selected_state: str, api_key: str) -> None:
    """Renders the 'The Process' tab.
    
    Args:
        selected_state (str): The state selected by the user.
        api_key (str): The Google API Key.
    """
    st.header("The Process")
    if selected_state != "Select a State...":
        with st.spinner(f"Loading election process for {selected_state}..."):
            prompt = (
                f"Explain the Assembly and Parliamentary election process for someone in {selected_state}. "
                "Keep it under 100 words. Use an analogy to make it easy for an 18-year-old to "
                "understand how their local vote connects to the state and national government."
            )
            try:
                result = generate_civic_content(prompt, api_key)
                st.info(result)
            except Exception as e:
                handle_generation_error(e)
    else:
        st.info("👈 Please select your state above to see how the election process works in your region.")


def render_timeline_tab(selected_state: str, api_key: str) -> None:
    """Renders the 'The Timeline' tab.
    
    Args:
        selected_state (str): The state selected by the user.
        api_key (str): The Google API Key.
    """
    st.header("The Timeline")
    if selected_state != "Select a State...":
        with st.spinner(f"Loading election timeline for {selected_state}..."):
            prompt = (
                f"Act as an election tracker. It is currently April 2026. Generate a 4-step "
                f"chronological timeline for the next major election in {selected_state}. "
                "Use a bulleted list. If an election is happening right now "
                "(like in Kerala, TN, Assam, WB, Puducherry), highlight the immediate polling dates."
            )
            try:
                result = generate_civic_content(prompt, api_key)
                st.success(result)
            except Exception as e:
                handle_generation_error(e)
    else:
        st.info("👈 Please select your state above to see your election timeline.")


def render_steps_tab(selected_state: str, is_first_time: str, api_key: str) -> None:
    """Renders the 'Your Steps' tab.
    
    Args:
        selected_state (str): The state selected by the user.
        is_first_time (str): 'Yes' or 'No' indicating first-time voter status.
        api_key (str): The Google API Key.
    """
    st.header("Your Steps")
    if selected_state != "Select a State...":
        with st.spinner("Generating your personalized action plan..."):
            if is_first_time == "Yes":
                prompt = (
                    "Act as an election guide. Generate a 3-step guide on exactly how to register "
                    "as a first-time voter using Form 6 via the Voter Helpline App. "
                    "Include which documents to keep ready."
                )
            else:
                prompt = (
                    "Act as an election guide. Generate a 3-step guide for a registered voter on "
                    "how to verify their name on the electoral roll and locate their specific polling booth."
                )
            
            try:
                result = generate_civic_content(prompt, api_key)
                if is_first_time == "Yes":
                    st.success("### Your Action Plan (First-Time Voter)")
                else:
                    st.info("### Your Action Plan (Registered Voter)")
                st.markdown(result)
            except Exception as e:
                handle_generation_error(e)
    else:
        st.info("👈 Please select your state above to get your personalized action plan.")


def main() -> None:
    """Main application entry point."""
    setup_page()
    api_key = init_api()
    
    selected_state, is_first_time = render_header()
    
    tab1, tab2, tab3 = st.tabs(["1. The Process", "2. The Timeline", "3. Your Steps"])
    
    with tab1:
        render_process_tab(selected_state, api_key)
        
    with tab2:
        render_timeline_tab(selected_state, api_key)
        
    with tab3:
        render_steps_tab(selected_state, is_first_time, api_key)

if __name__ == "__main__":
    main()
