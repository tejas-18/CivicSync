# CivicSync: Interactive Election Guide 🇮🇳

CivicSync is a modern, lightweight Streamlit dashboard designed to help first-time voters understand the Indian election process, track timelines, and easily register to vote. Built for Round 2 of PromptWars.

## Features

*   **The Process**: Demystifies the Assembly and Parliamentary election process with GenZ-friendly analogies.
*   **The Timeline**: Generates a dynamic 4-step chronological timeline for the next major election in any selected state.
*   **Your Steps**: Personalized, dynamic action plans for registering to vote (using Form 6 via the Voter Helpline App) or verifying electoral roll status.
*   **AI-Powered**: Integrates Google's `gemini-2.0-flash` model for high-speed, dynamic content generation.

## Prerequisites

*   Python 3.10+
*   Google Gemini API Key

## Setup & Installation

1.  Clone this repository.
2.  Set up your virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: .\venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Environment Variables:
    Copy `.env.example` to `.env` and add your Google API key:
    ```
    GOOGLE_API_KEY=your_actual_key_here
    ```

## Running the App

```bash
streamlit run main.py
```

## Running Tests

This project includes a comprehensive test suite covering the core AI logic and error handling.
```bash
pytest tests/
```

## Sample Prompts

The application runs customized system instructions against the Gemini SDK. Some examples include:
*   *Process Guide:* "Explain the Assembly and Parliamentary election process for someone in Maharashtra. Keep it under 100 words. Use an analogy to make it easy for an 18-year-old to understand..."
*   *Timeline Tracker:* "Act as an election tracker. It is currently April 2026. Generate a 4-step chronological timeline for the next major election in Kerala..."
*   *Action Plan:* "Act as an election guide. Generate a 3-step guide on exactly how to register as a first-time voter using Form 6 via the Voter Helpline App."
