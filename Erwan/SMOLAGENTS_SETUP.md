# smolagents Setup Guide for OfferFinder

## Installation

### Option 1: pip install (if pip is available)
```bash
pip install smolagents
```

### Option 2: conda install
```bash
conda install -c conda-forge smolagents
```

### Option 3: Manual installation (if pip is not available)
```bash
# Download and install manually
wget https://files.pythonhosted.org/packages/source/s/smolagents/smolagents-0.3.0.tar.gz
tar -xzf smolagents-0.3.0.tar.gz
cd smolagents-0.3.0
python3 setup.py install --user
```

### Option 4: Using requirements.txt
Create a `requirements.txt` file:
```
smolagents>=0.3.0
transformers>=4.30.0
torch>=1.13.0
```

Then install:
```bash
pip install -r requirements.txt
```

## Verification

Test if smolagents is installed correctly:

```python
try:
    from smolagents import CodeAgent, HfApiModel
    print("✓ smolagents is installed and ready!")
except ImportError as e:
    print(f"✗ smolagents not available: {e}")
```

## Quick Start with OfferFinder

Once smolagents is installed, you can use it with OfferFinder:

```python
from offer_manager import OfferFinder

# Auto-initialization (simplest method)
finder = OfferFinder()  # Will auto-create smolagents instance

# Or manual configuration
from smolagents import CodeAgent, LiteLLMModel

# For OpenAI GPT models
model = LiteLLMModel(
    model_id="gpt-3.5-turbo",
    api_key="your-openai-api-key"
)
agent = CodeAgent(tools=[], model=model)
finder = OfferFinder(agent)

# For Anthropic Claude models
model = LiteLLMModel(
    model_id="claude-3-sonnet-20240229",
    api_key="your-anthropic-api-key"
)
agent = CodeAgent(tools=[], model=model)
finder = OfferFinder(agent)
```

## Available Models

smolagents supports multiple model providers through LiteLLM:

### OpenAI Models
- `gpt-4`
- `gpt-3.5-turbo`
- `gpt-4-turbo-preview`

### Anthropic Models
- `claude-3-sonnet-20240229`
- `claude-3-opus-20240229`
- `claude-3-haiku-20240307`

### HuggingFace Models
- `microsoft/DialoGPT-medium`
- `microsoft/DialoGPT-large`
- `facebook/blenderbot-400M-distill`

### Local Models
- Any model compatible with HuggingFace Transformers

## Environment Variables

Set up API keys as environment variables:

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-key"

# For Anthropic
export ANTHROPIC_API_KEY="your-anthropic-key"

# For HuggingFace
export HUGGINGFACE_API_TOKEN="your-hf-token"
```

## Testing the Integration

Run the smolagents demo:

```bash
python3 smolagents_demo.py
```

Expected output with smolagents installed:
```
✓ smolagents package available
✓ Successfully created smolagents LLM adapter
```

Expected output without smolagents:
```
⚠ smolagents package not available
→ Using mock smolagents for demonstration
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure smolagents is installed in the correct Python environment
2. **Model Loading Issues**: Check API keys and network connectivity
3. **Memory Issues**: Some models require significant RAM

### Fallback Behavior

The OfferFinder is designed to work even without smolagents:
- Falls back to mock responses for demonstration
- Maintains compatibility with standard LLM interfaces
- Provides clear error messages when models fail to load

### Support

If you encounter issues:
1. Check the [smolagents documentation](https://github.com/huggingface/smolagents)
2. Verify your Python environment and dependencies
3. Use the mock implementation for development and testing

## Production Recommendations

For production use:
1. Use stable models like `gpt-3.5-turbo` or `claude-3-sonnet`
2. Implement proper error handling and retry logic
3. Set up monitoring for API usage and costs
4. Use environment variables for API keys
5. Consider rate limiting and caching strategies