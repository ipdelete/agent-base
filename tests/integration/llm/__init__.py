"""Real LLM integration tests.

⚠️ WARNING: These tests make real API calls and cost money!

Tests in this directory:
- Make real LLM API calls (OpenAI, Anthropic, Azure)
- Verify tool invocation works correctly with real models
- Test edge cases and error handling
- Track conversation context across multiple turns

Cost Controls:
- Use cheaper models (gpt-4o-mini, claude-sonnet-4-5)
- Keep prompts minimal (5-15 tokens)
- Target: < $0.01 per full test run
- Opt-in only via pytest -m llm

How to Run:
    # Set API keys
    export OPENAI_API_KEY=your-key
    export ANTHROPIC_API_KEY=your-key

    # Run all LLM tests
    pytest -m llm

    # Run specific provider
    pytest -m "llm and requires_openai"

    # Skip LLM tests (default)
    pytest -m "not llm"
"""
