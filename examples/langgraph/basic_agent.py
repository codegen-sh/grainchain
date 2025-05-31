"""
Basic example of using LangGraph with Grainchain sandbox integration.

This example demonstrates how to create a simple agent that can execute
code in a sandbox environment using LangGraph.
"""

import asyncio


# Mock LLM for demonstration (replace with real LLM in practice)
class MockChatModel:
    """
    Mock chat model for demonstration purposes.

    In a real implementation, you would use a proper LLM like:
    - from langchain_openai import ChatOpenAI
    - from langchain_anthropic import ChatAnthropic
    - etc.
    """

    def __init__(self):
        self.tools = []
        self.call_count = 0

    def bind_tools(self, tools):
        """Bind tools to the model."""
        self.tools = tools
        return self

    def invoke(self, messages):
        """Mock invoke method that simulates LLM responses."""
        from langchain_core.messages import AIMessage, HumanMessage

        # Get the last human message
        last_human_message = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                last_human_message = msg.content
                break

        if not last_human_message:
            return AIMessage(content="I'm ready to help!")

        # Simple rule-based responses for demonstration
        if "hello" in last_human_message.lower():
            return AIMessage(
                content="Hello! I can help you execute code in a sandbox. What would you like me to do?"
            )
        elif (
            "python" in last_human_message.lower()
            or "script" in last_human_message.lower()
        ):
            # For demo purposes, just return a simple response instead of tool calls
            return AIMessage(
                content="I would create a Python script for you, but this is a mock LLM demo. In a real implementation with a proper LLM, I would use the sandbox tools to create and execute the script."
            )
        elif (
            "execute" in last_human_message.lower()
            or "run" in last_human_message.lower()
        ):
            # For demo purposes, just return a simple response instead of tool calls
            return AIMessage(
                content="I would execute that command for you, but this is a mock LLM demo. In a real implementation with a proper LLM, I would use the sandbox tools to run the command."
            )
        else:
            return AIMessage(
                content="I can help you with code execution in a sandbox. Try asking me to create a Python script or execute a command!"
            )


async def main():
    """Main example function."""
    print("🌾 Grainchain LangGraph Integration Example")
    print("=" * 50)

    # Import the necessary components
    try:
        from grainchain.langgraph import create_local_sandbox_agent
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed grainchain with langgraph support:")
        print("pip install grainchain[langgraph]")
        return

    # Create a mock LLM (replace with real LLM in practice)
    llm = MockChatModel()
    print("✅ Created mock LLM")

    # Create a local sandbox agent
    try:
        agent = create_local_sandbox_agent(
            llm=llm,
            working_directory="./sandbox_workspace",
            timeout=30,
            system_message=(
                "You are a helpful coding assistant with access to a local sandbox. "
                "You can execute code, create files, and help with programming tasks. "
                "Always be helpful and explain what you're doing."
            ),
        )
        print("✅ Created local sandbox agent")
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return

    # Example interactions
    examples = [
        "Hello! Can you help me with Python?",
        "Create a Python script that prints a greeting",
        "Now execute the Python script",
    ]

    print("\n🚀 Running example interactions:")
    print("-" * 30)

    for i, message in enumerate(examples, 1):
        print(f"\n{i}. User: {message}")

        try:
            # Run the agent (this would normally be async, but we'll use sync for simplicity)
            response = agent.run(message)
            print(f"   Agent: {response}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Cleanup
    try:
        await agent.cleanup()
        print("\n✅ Agent cleanup completed")
    except Exception as e:
        print(f"\n⚠️ Cleanup warning: {e}")


def sync_main():
    """Synchronous wrapper for the main function."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("Note: This example uses a mock LLM for demonstration.")
    print("In a real implementation, you would use a proper LLM like ChatOpenAI.")
    print()

    sync_main()
