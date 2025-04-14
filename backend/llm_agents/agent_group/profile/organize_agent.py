import asyncio
from llm_agents.agent_factory import get_profile_organize_agent
from llm_agents.prompts.profile import utilis
from schemas.agents.agents_schema import UserPrompt
from schemas.agents.profile.profile_schema import UserProfiles
from utils.config import LOG


#这里没有对profile做分类 即domain做分类 或许需要内部分类并发处理？？？？会更好？？？？
async def organize_profile(profile: UserProfiles, max_items: int = 5) -> UserProfiles:
    """
    Organize and consolidate profile information into a more coherent structure.
    
    Args:
        profile: UserProfiles object containing profile facts to organize
        max_items: Maximum number of organized items to return (default: 5)
        
    Returns:
        Organized profile information as UserProfiles object or None if parsing fails
    """
    try:
        # Get the profile organization agent
        agent = get_profile_organize_agent()
        
        # Format the input for the organization agent
        domain_blocks = {}
        
        # Group facts by domain
        for fact in profile.facts:
            if fact.domain not in domain_blocks:
                domain_blocks[fact.domain] = []
            domain_blocks[fact.domain].append(f"- {fact.attribute}{utilis.llm_tab_separator}{fact.description}")
        
        # Format each domain block
        formatted_blocks = []
        for domain, facts in domain_blocks.items():
            block = f"domain: {domain}\n" + "\n".join(facts)
            formatted_blocks.append(block)
        
        # Combine all domain blocks
        input_text = "\n\n".join(formatted_blocks)
        
        # Create a UserPrompt object
        user_prompt = UserPrompt(input=input_text)
        
        # Process the input
        LOG.info(f"Organizing profile with {len(profile.facts)} facts")
        result = await agent.generate(user_prompt)
        
        # Log the raw result
        LOG.info("Raw organization result:")
        LOG.info(result["message"])
        
        # Try to parse the result into UserProfile objects
        organized_profiles = utilis.parse_profile_to_pydantic(result["message"])
        
        LOG.info(f"Successfully organized profile into {len(organized_profiles.facts)} facts")
        return organized_profiles
    except Exception as e:
        LOG.error(f"Error organizing profile data: {e}")
        return None


async def main():
    """Main function to run examples."""
    # Example: Organizing profile information
    print("Example: Organizing profile information")
    from schemas.agents.profile.profile_schema import UserProfile
    
    # Create a sample unorganized profile
    profile = UserProfiles(facts=[
        UserProfile(domain="education", attribute="school", description="Stanford University"),
        UserProfile(domain="education", attribute="degree", description="Bachelor of Science"),
        UserProfile(domain="education", attribute="major", description="Computer Science"),
        UserProfile(domain="education", attribute="graduation_year", description="2015"),
        UserProfile(domain="education", attribute="gpa", description="3.8"),
        UserProfile(domain="education", attribute="activities", description="Member of Robotics Club"),
        UserProfile(domain="education", attribute="thesis", description="AI Applications in Healthcare"),
        UserProfile(domain="education", attribute="school", description="MIT"),
        UserProfile(domain="education", attribute="degree", description="Master of Science"),
        UserProfile(domain="education", attribute="major", description="Artificial Intelligence"),
        UserProfile(domain="education", attribute="graduation_year", description="2017"),
        UserProfile(domain="education", attribute="gpa", description="3.9"),
        UserProfile(domain="education", attribute="activities", description="Teaching Assistant for Machine Learning course"),
        UserProfile(domain="education", attribute="thesis", description="Deep Learning for Natural Language Processing"),
        #TODO:或许可以分类取搞成功率更高 就是education一个 agent work一个agent
        UserProfile(domain="work", attribute="company", description="Google"),
        UserProfile(domain="work", attribute="position", description="Software Engineer"),
        UserProfile(domain="work", attribute="duration", description="2017-2020"),
        UserProfile(domain="work", attribute="company", description="Microsoft"),
        UserProfile(domain="work", attribute="position", description="Senior Software Engineer"),
        UserProfile(domain="work", attribute="duration", description="2020-present"),
    ])
    
    print(f"Original profile has {len(profile.facts)} facts")
    for fact in profile.facts:
        print(f"- {fact.domain} / {fact.attribute}: {fact.description}")
    
    print("\nOrganizing profile...")
    organized_profile = await organize_profile(profile)
    
    if organized_profile:
        print(f"\nOrganized profile has {len(organized_profile.facts)} facts")
        for fact in organized_profile.facts:
            print(f"- {fact.domain} / {fact.attribute}: {fact.description}")


if __name__ == "__main__":
    asyncio.run(main()) 