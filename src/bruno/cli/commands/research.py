import asyncio
import hashlib
import os
from typing import Annotated
import typer
from google.api_core.exceptions import ResourceExhausted
from langchain_core.messages import HumanMessage
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel

from bruno.agent.graph import create_bruno_agent
from bruno.agent.tools.mcp_tools import load_mcp_tools
from bruno.agent.tools.rag_tools import rag_search
from bruno.agent.tools.web_tools import web_search
from bruno.cli.formatters import display_error, display_response, display_spinner
from bruno.config import get_settings


async def run_research(topic: str, depth: str = "shallow"):
    settings = get_settings()

    if not settings.gemini_api_key:
        display_error("BRUNO_GEMINI_API_KEY is not set. Run `bruno config init`.")
        raise typer.Exit(1)

    query = f"{topic} (Provide a {depth} research summary)"

    try:
        # Generate a thread ID based on the current directory
        cwd = os.getcwd()
        thread_id = hashlib.md5(cwd.encode()).hexdigest()
        config = {"configurable": {"thread_id": f"research_{thread_id}"}}
        
        state_input = {
            "messages": [HumanMessage(content=query)],
            "user_query": query,
            "intent": "research",
        }
        
        mcp_client = await load_mcp_tools(settings)
        async with mcp_client as client:
            mcp_tools = client.get_tools()
            all_tools = [rag_search, web_search] + mcp_tools

            agent = create_bruno_agent(settings, tools=all_tools)
            
            content = ""
            with Live(Panel(Markdown("Researching..."), title="[bold bright_cyan]Bruno[/bold bright_cyan]", border_style="bright_cyan"), refresh_per_second=15) as live:
                async for event in agent.astream_events(state_input, config, version="v2"):
                    if event["event"] == "on_chat_model_stream":
                        chunk = event["data"]["chunk"]
                        if isinstance(chunk.content, str) and chunk.content:
                            content += chunk.content
                            live.update(Panel(Markdown(content), title="[bold bright_cyan]Bruno[/bold bright_cyan]", border_style="bright_cyan"))
                    elif event["event"] == "on_chat_model_start":
                        content = ""
                        live.update(Panel(Markdown("Researching..."), title="[bold bright_cyan]Bruno[/bold bright_cyan]", border_style="bright_cyan"))
                    elif event["event"] == "on_tool_start":
                        tool_name = event["name"]
                        live.update(Panel(Markdown(content + f"\n\n*Running tool: `{tool_name}`...*"), title="[bold bright_cyan]Bruno[/bold bright_cyan]", border_style="bright_cyan"))

    except ResourceExhausted:
        display_error("Your free tier is over and stop the work when my free tier is completely used up.")
        raise typer.Exit(1)
    except Exception as e:
        if "429" in str(e) or "quota" in str(e).lower():
            display_error("Your free tier is over and stop the work when my free tier is completely used up.")
            raise typer.Exit(1)
        display_error(f"Agent execution failed: {e}")

def research_cmd(
    topic: str = typer.Argument(..., help="The research topic"),
    depth: Annotated[str, typer.Option("--depth", "-d", help="'shallow' or 'deep'")] = "shallow",
):
    """Research a development topic."""
    asyncio.run(run_research(topic, depth))
