from smolagents import CodeAgent, LiteLLMModel
from schedule_agent import AddEventTool, RemoveEventTool, CheckConflictsTool, UpdateEventTool, ScheduleManager, BeautifulScheduleTool  # Import the code I provided
from schedule_web_view import ScheduleWebViewTool  # Import the web view for the schedule


from .key import key  # Import your API key from a separate file

ANTHROPIC_API_KEY = key
# Create your base CodeAgent
schedule_manager = ScheduleManager()
model = LiteLLMModel(model_id="claude-3-5-sonnet-20240620",
                     api_key=ANTHROPIC_API_KEY)

base_agent = CodeAgent(
    tools=[AddEventTool(schedule_manager), RemoveEventTool(schedule_manager), CheckConflictsTool(schedule_manager), UpdateEventTool(schedule_manager), ScheduleWebViewTool(schedule_manager)],  # Your existing tools
    model=model,  # or your preferred model
    add_base_tools=False,
    additional_authorized_imports=["datetime", "json", "typing", "pydantic"],  # Add any additional imports you need
)

# Create the enhanced schedule agent
schedule_agent = base_agent

"""response = schedule_agent.run("Delete all my activities for tomarow")
response = schedule_agent.run("Add a team meeting tomorrow from 5 PM to 6 PM. It is not very important")
response = schedule_agent.run("When could I put a meetting with the team, tomarrow before 6 PM?")
schedule_agent.run("I finally need to play soccer tomarrow afternoon. Can you remove the least important meeting so I can do that and put my soccer game. It should last 1hour?")"""
# response = schedule_agent.run("Add a team meeting today from 5 PM to 6 PM")
schedule_agent.run("Can you show me my schedule for the week?")
