import contextlib
import io
import sys
from smolagents import CodeAgent, LiteLLMModel
# Claude API Key
ANTHROPIC_API_KEY = "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"

# Model
model = LiteLLMModel(
    model_id="claude-3-5-sonnet-20240620",
    api_key=ANTHROPIC_API_KEY,
    verbose=False
)

# Agent
agent = CodeAgent(
    tools=[],
    model=model,
    add_base_tools=True
)

# Silence console output from agent.run()
@contextlib.contextmanager
def suppress_stdout():
    original_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        yield
    finally:
        sys.stdout = original_stdout

with suppress_stdout():
    result = agent.run("What is the current weather in Paris?")

print(result)