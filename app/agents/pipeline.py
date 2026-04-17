from app.agents.agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

def run_research_pipeline(topic: str, max_iterations: int = 3) -> dict:
    # Initialize state with the topic to avoid KeyErrors
    state = {
        "topic": topic,
        "search_results": "No results yet.",
        "scraped_content": "",
        "report": "",
        "feedback": "",
        "iteration": 0
    }

    # --- STEP 1: INITIAL SEARCH ---
    # We first perform a broad search so the agents actually have something to read
    print(f"\n{'='*50}\nStep 1: Search agent is gathering intelligence...\n{'='*50}")
    search_agent = build_search_agent()
    
    # Logic Fix: Prompt the agent to perform the initial search first
    initial_search = search_agent.invoke({
        "messages": [("user", f"Search for high-quality articles and data regarding: {topic}")]
    })
    state['search_results'] = initial_search['messages'][-1].content

    # --- STEP 2: READER/SCRAPER ---
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [("user", 
            f"From these search results about '{topic}', pick the single most authoritative URL "
            f"and scrape its full text:\n\n{state['search_results'][:1000]}"
        )]
    })
    state["scraped_content"] = reader_result['messages'][-1].content
    print("Scraping complete.")

    # --- STEP 3 & 4: WRITER-CRITIC ITERATION ---
    # This loop ensures the report isn't finished until the critic is satisfied
    while state["iteration"] < max_iterations:
        state["iteration"] += 1
        print(f"\n{'='*50}\nStep 3: Writer drafting report (Attempt {state['iteration']})...\n{'='*50}")

        research_combined = (
            f"SEARCH RESULTS: \n {state['search_results']}\n\n"
            f"DETAILED SCRAPED CONTENT: \n {state['scraped_content']}\n\n"
            f"PREVIOUS CRITIQUE (if any): \n {state.get('feedback', 'None')}"
        )

        state["report"] = writer_chain.invoke({
            "topic": topic,
            "research": research_combined
        })

        print(f"\n{'='*50}\nStep 4: Critic reviewing the draft...\n{'='*50}")
        state["feedback"] = critic_chain.invoke({
            "report": state["report"]
        })

        # Logic: If the critic provides a "Pass" or "Approved", we break the loop
        # Note: You can customize this condition based on your critic_chain output format
        print(f"Critic Feedback: {state['feedback'][:200]}...")
        
        if "APPROVE" in state["feedback"].upper() or "PASS" in state["feedback"].upper():
            print("\n Report approved by critic.")
            break
        else:
            print(f"\n Revision requested. Restarting Loop {state['iteration'] + 1}...")

    return state

if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    final_state = run_research_pipeline(topic)
    print(f"\n{'#'*50}\nFINAL REPORT\n{'#'*50}\n", final_state["report"])