import asyncio
import os
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama

async def main():
    # 1. MCP-Client definieren und Server starten
    client = MultiServerMCPClient({
        "HomeAssistant": {
            "command": "python",
            "args": ["./../Server/mcpServer.py"],
            "transport": "stdio",
        }
    })

    # 2. Werkzeuge vom MCP-Server holen (async/Awaiting ist hier korrekt)
    tools = await client.get_tools()

    # 3. Ollama-LLM instanziieren
    llm = ChatOllama(
        model="llama3.1",           # ggf. llama3.1:7b o. Ä., je nachdem, was gepullt wurde
        base_url="http://127.0.0.1:11434"
    )

    # 4. ReAct-Agent bauen
    agent = create_react_agent(llm, tools)

    # 5. Prompt definieren
    prompt = "Setze die Temperatur im wohnzimmer auf 25 Grad."

    response_async = await agent.ainvoke({
        "messages": [{"role": "user", "content": prompt}]
    })
    answer_async = response_async["messages"][-1].content
    print(answer_async)

if __name__ == "__main__":
    asyncio.run(main())
