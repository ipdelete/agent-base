# Real LLM Integration Tests

⚠️ **WARNING: These tests make real API calls and cost money!**

## Overview

This directory contains integration tests that make **real LLM API calls** to verify:
- Tools are correctly invoked by actual LLMs
- Error handling works in practice
- Conversation context is maintained
- Behavior is consistent across providers

## Why Real LLM Tests?

While mocked tests (in `tests/unit/` and `tests/integration/`) verify logic, they **cannot** verify:
- LLMs actually understand our tool schemas
- Tool calling format is correct for each provider
- Prompts and instructions work as expected
- Provider-specific behavior and quirks

These tests complement mocked tests by verifying real-world behavior.

## Cost Controls

**Target Cost**: < $0.01 per full test run

**Strategies**:
1. **Use cheaper models**:
   - OpenAI: `gpt-4o-mini` (not gpt-4o)
   - Anthropic: `claude-sonnet-4-5` (not opus)

2. **Keep prompts minimal**: 5-15 tokens per prompt

3. **Opt-in only**: Tests only run when explicitly requested

4. **Automatic skipping**: Tests skip if API keys not present

**Estimated Costs** (as of Nov 2025):
- OpenAI (gpt-4o-mini): ~$0.003 per test run
- Anthropic (claude-sonnet-4-5): ~$0.004 per test run
- **Total**: ~$0.007 per run with both providers

## How to Run

### Setup

```bash
# Set API keys for providers you want to test
export OPENAI_API_KEY=sk-your-key-here
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Azure OpenAI
export AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
export AZURE_OPENAI_DEPLOYMENT=gpt-5-codex

# Azure AI Foundry
export AZURE_PROJECT_ENDPOINT=https://your-account.services.ai.azure.com/api/projects/your-project
export AZURE_MODEL_DEPLOYMENT=gpt-4o
```

### Run Tests

```bash
# Run ALL LLM integration tests
pytest -m llm

# Run only OpenAI tests
pytest -m "llm and requires_openai"

# Run only Anthropic tests
pytest -m "llm and requires_anthropic"

# Run specific test file
pytest tests/integration/llm/test_openai_integration.py -v

# Run with verbose output
pytest -m llm -vv

# Skip LLM tests (default in CI)
pytest -m "not llm"
```

### Test Organization

```
tests/integration/llm/
├── conftest.py                      # Fixtures for real agents
├── test_openai_integration.py       # OpenAI-specific tests
├── test_anthropic_integration.py    # Anthropic-specific tests
├── test_tool_invocation.py          # Cross-provider tool tests
└── README.md                        # This file
```

## Test Structure

### Fixtures (`conftest.py`)

- `openai_agent` - Real OpenAI agent (skips if no API key)
- `anthropic_agent` - Real Anthropic agent (skips if no API key)
- `azure_openai_agent` - Real Azure OpenAI agent (skips if no credentials)
- `azure_ai_foundry_agent` - Real Azure AI Foundry agent (skips if no credentials)

### Test Files

**test_openai_integration.py**:
- Basic prompt/response
- Tool invocation
- Error handling
- Conversation context

**test_anthropic_integration.py**:
- Basic prompt/response
- Streaming responses
- Tool invocation
- Error handling

**test_tool_invocation.py**:
- Cross-provider tool calling comparison
- Consistent error handling
- Tool response format interpretation

## Pytest Markers

All tests in this directory automatically get:
- `@pytest.mark.llm` - Indicates real LLM API call
- `@pytest.mark.slow` - Tests take >1s

Additionally, tests should have provider markers:
- `@pytest.mark.requires_openai` - Requires OpenAI API key
- `@pytest.mark.requires_anthropic` - Requires Anthropic API key
- `@pytest.mark.requires_azure` - Requires Azure credentials

## CI/CD Integration

**Default CI Behavior**: LLM tests are **SKIPPED**
```yaml
# .github/workflows/ci.yml
pytest -m "not llm"  # Excludes these tests
```

**Optional**: Create nightly workflow to run LLM tests with secrets:
```yaml
# .github/workflows/llm-tests.yml (future)
schedule:
  - cron: '0 2 * * *'  # 2 AM daily
steps:
  - run: pytest -m llm
    env:
      OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## Writing New LLM Tests

### Use the Template

```bash
# Copy template
cp tests/templates/test_llm_template.py tests/integration/llm/test_your_feature.py

# Customize for your tests
```

### Best Practices

1. **Always use markers**:
   ```python
   @pytest.mark.llm
   @pytest.mark.requires_openai
   @pytest.mark.slow
   async def test_something(openai_agent):
       pass
   ```

2. **Keep prompts minimal**:
   ```python
   # Good - short and focused
   response = await agent.run("Say 'test'")

   # Avoid - unnecessarily long
   response = await agent.run(
       "Please say the word test and only that word, nothing else, just test"
   )
   ```

3. **Use relaxed assertions**:
   ```python
   # LLMs are non-deterministic
   assert "expected" in response.lower()  # Flexible

   # Avoid exact matches
   # assert response == "exact text"  # Too strict
   ```

4. **Document costs in docstrings**:
   ```python
   async def test_something(self, openai_agent):
       \"\"\"Test description.

       Cost: ~$0.0003
       \"\"\"
   ```

## Troubleshooting

### Tests Skip Automatically

**Symptom**: All LLM tests show as "SKIPPED"

**Cause**: API keys not set

**Solution**:
```bash
export OPENAI_API_KEY=your-key
pytest -m llm -v  # Should now run
```

### Tests Fail with Authentication Error

**Symptom**: Tests fail with 401 or authentication error

**Cause**: Invalid or expired API key

**Solution**: Check your API key is valid and active

### High Costs

**Symptom**: Tests cost more than expected

**Solutions**:
1. Check you're using cheaper models (gpt-4o-mini, not gpt-4o)
2. Reduce number of tests
3. Make prompts shorter
4. Run tests less frequently

## Future Enhancements

- [ ] Actual cost tracking per test (log to file)
- [ ] Performance benchmarking across providers
- [ ] Prompt regression testing (track quality over time)
- [ ] Multi-agent coordination tests
- [ ] Long conversation context tests
- [ ] Parallel tool calling tests

## Related Documentation

- [ADR-0008](../../../docs/decisions/0008-testing-strategy-and-coverage-targets.md) - Testing strategy
- [Test Templates](../../templates/) - Templates for new tests
- [CONTRIBUTING.md](../../../CONTRIBUTING.md) - General testing guidelines
