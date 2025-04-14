import asyncio
from llm_agents.agent_factory import get_profile_extraction_agent
from llm_agents.prompts.profile import utilis
from schemas.agents.agents_schema import UserPrompt
from schemas.agents.profile.profile_schema import ChatBlob, UserProfiles
from utils.config import LOG


async def extract_profile(chat: ChatBlob) -> UserProfiles:
    """
    Extract profile information from chat messages.
    
    Args:
        chat: ChatBlob containing conversation messages
        
    Returns:
        Extracted profile information as UserProfiles object or None if parsing fails
    """
    # Get the profile extraction agent
    agent = get_profile_extraction_agent()
    
    # Extract only user messages
    user_messages = []
    for msg in chat.messages:
        if msg.role == "user":
            user_messages.append(msg.content)
    
    # Combine all user messages
    text = "\n".join(user_messages)
    user_prompt = UserPrompt(input=text)

    # Process the input
    result = await agent.generate(user_prompt)

    # Log the raw result
    LOG.info("Raw result:")
    LOG.info(result)
    LOG.info("Raw result message:")
    LOG.info(result["message"])

    # Try to parse the result into UserProfile objects
    try:
        profiles = utilis.parse_profile_to_pydantic(result["message"])
        return profiles
    except Exception as e:
        LOG.error(f"Error parsing profile data: {e}")
        return None


async def main():
    """Main function to run examples."""
    # Example: Extracting from chat messages
    print("Example: Extracting from chat messages")
    from schemas.agents.profile.profile_schema import OpenAICompatibleMessage
    
    # Create a sample chat conversation
    chat = ChatBlob(messages=[
        OpenAICompatibleMessage(role="user", content="Hi, my name is Emily."),
        OpenAICompatibleMessage(role="assistant", content="Hello Emily, how can I help you today?"),
        OpenAICompatibleMessage(role="user", content="I'm 28 years old and work as a graphic designer. I've been considering a move to New York."),
        OpenAICompatibleMessage(role="assistant", content="That sounds exciting! What's prompting you to consider moving to New York?"),
        OpenAICompatibleMessage(role="user", content="I've been offered a job at a design agency there with a salary of $85,000.")
    ])
    
    profiles = await extract_profile(chat)
    if profiles:
        print(f"Extracted {len(profiles.facts)} profile facts from chat")
        for fact in profiles.facts:
            print(f"- {fact.domain} / {fact.attribute}: {fact.description}")


if __name__ == "__main__":
    asyncio.run(main())