"""
Real LLM example using OpenAI with Grainchain LangGraph integration.

This example shows how to use a real LLM (OpenAI) with the sandbox agent.
You'll need to set your OPENAI_API_KEY environment variable.
"""

import asyncio
import os


async def main():
    """Main example function with real LLM."""
    print("⏳ Grainchain LangGraph + OpenAI Example")
    print("=" * 50)

    # Check for API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key:")
        print("export OPENAI_API_KEY='your-api-key-here'")
        return

    # Import the necessary components
    try:
        from langchain_openai import ChatOpenAI

        from grainchain.langgraph import create_local_sandbox_agent

        print("✅ Imported required modules")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you have installed the required packages:")
        print("pip install grainchain[langgraph] langchain-openai")
        return

    # Create OpenAI LLM
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",  # Use a cost-effective model for the example
            temperature=0.1,
            api_key=api_key,
        )
        print("✅ Created OpenAI LLM")
    except Exception as e:
        print(f"❌ Error creating LLM: {e}")
        return

    # Create a local sandbox agent
    try:
        agent = create_local_sandbox_agent(
            llm=llm,
            working_directory="./sandbox_workspace",
            timeout=60,
            system_message=(
                "You are a helpful coding assistant with access to a local sandbox environment. "
                "You can execute commands, create files, install packages, and help with programming tasks. "
                "When users ask you to write code, create the files and execute them to show the results. "
                "Always explain what you're doing and show the output of your commands."
            ),
        )
        print("✅ Created local sandbox agent")
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return

    # Interactive mode
    print("\n🚀 Interactive mode started!")
    print("Type your requests below (or 'quit' to exit):")
    print("-" * 50)

    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                break

            if not user_input:
                continue

            print("Agent: ", end="", flush=True)

            # Run the agent
            response = await agent.arun(user_input)
            print(response)

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

    # Cleanup
    try:
        await agent.cleanup()
        print("\n✅ Agent cleanup completed")
    except Exception as e:
        print(f"\n⚠️ Cleanup warning: {e}")


def example_requests():
    """Show some example requests users can try."""
    print("\n💡 Example requests you can try:")
    print("- Create a Python script that calculates fibonacci numbers")
    print("- Write a simple web scraper and run it")
    print("- Create a data analysis script with matplotlib")
    print("- Install a Python package and use it")
    print("- Create a simple REST API with Flask")
    print("- Write and run unit tests for a function")


if __name__ == "__main__":
    print("This example requires OpenAI API access.")
    print("Make sure you have set your OPENAI_API_KEY environment variable.")

    example_requests()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
