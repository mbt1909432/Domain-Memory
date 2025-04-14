import asyncio
import llm_agents.agent_factory
from llm_agents.agent_factory import get_profile_update_agent
from llm_agents.prompts.profile import utilis
from schemas.agents.agents_schema import UserPrompt
from schemas.agents.profile.profile_schema import  ProfileUpdateInput,  ProfileUpdateResult
from utils.config import LOG
from typing import List, Optional


async def update_profile(profile_input: ProfileUpdateInput) -> Optional[ProfileUpdateResult]:
    """
    Update profile information by merging old and new descriptions.
    
    Args:
        profile_input: ProfileUpdateInput containing domain, attribute, old_description and new_description
        
    Returns:
        ProfileUpdateResult with action and updated description, or None if parsing fails
    """
    try:
        # Get the profile update agent
        agent = get_profile_update_agent()
        
        # Format the input for the update agent
        input_text = f"""## domain attribute
{profile_input.domain} {profile_input.attribute}

## Old Description
{profile_input.old_description}

## New Description
{profile_input.new_description}"""
        
        # Create a UserPrompt object
        user_prompt = UserPrompt(input=input_text)
        
        # Process the update
        result = await agent.generate(user_prompt)
        
        if result is None:
            LOG.error("LLM API returned None response")
            return None
            
        if "message" not in result:
            LOG.error("LLM API response missing 'message' field")
            return None
            
        # Log the raw result
        LOG.info("Raw update result:")
        LOG.info(result)
        LOG.info("Raw result message:")
        LOG.info(result["message"])
        
        # Try to parse the result
        try:
            # The result should be in format "- ACTION::DESCRIPTION"
            # We'll parse it manually since it doesn't match our standard profile format
            message = result["message"].strip()
            
            # Find lines that start with "- "
            for line in message.split("\n"):
                line = line.strip()
                if line.startswith("- "):
                    # Remove the "- " prefix
                    content = line[2:]
                    
                    # Split by the separator
                    parts = content.split(utilis.llm_tab_separator, 1)
                    if len(parts) == 2:
                        action, description = parts
                        return ProfileUpdateResult(
                            action=action.strip(),
                            description=description.strip(),
                            domain=profile_input.domain,
                            attribute=profile_input.attribute
                        )
            
            LOG.warning("Could not find valid update format in response")
            return None
        except Exception as e:
            LOG.error(f"Error parsing update result: {e}")
            return None
            
    except Exception as e:
        LOG.error(f"Error in update_profile: {e}")
        return None



async def main():
    """Main function to run examples."""
    # Example 1: Update age information
    print("Example 1: Direct update of age information")
    update_input = ProfileUpdateInput(
        domain="basic_info",
        attribute="age",
        old_description="User is 39 years old",
        new_description="User is 40 years old"
    )
    update1 = await update_profile(update_input)
    print(f"Update result: {update1}")
    print("\n" + "=" * 80 + "\n")
    
    # Example 2: Merge food preferences
    print("Example 2: Merge food preferences")
    update_input2 = ProfileUpdateInput(
        domain="interest",
        attribute="food",
        old_description="Love cheese pizza",
        new_description="Love chicken pizza"
    )
    update2 = await update_profile(update_input2)
    print(f"Update result: {update2}")
    print("\n" + "=" * 80 + "\n")
    


if __name__ == "__main__":
    asyncio.run(main()) 