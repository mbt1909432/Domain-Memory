import asyncio
from llm_agents.agent_factory import get_profile_summary_agent
from schemas.agents.agents_schema import UserPrompt
from schemas.agents.profile.profile_schema import UserProfiles, ProfileSummary
from utils.config import LOG
from llm_agents.prompts.profile import utilis


async def summarize_profile(profile: UserProfiles) -> ProfileSummary:
    """
    Create a concise summary of a user profile.

    Args:
        profile: UserProfiles object containing profile facts to summarize

    Returns:
        ProfileSummary object containing a concise summary of the profile
    """
    try:
        # Get the profile summary agent
        agent = get_profile_summary_agent()

        # Format the profile information for the summary agent
        if hasattr(profile, 'facts') and profile.facts:
            # Format the profile data using the utility function
            formatted_profile = utilis.format_profile_data(profile)

            # Create a UserPrompt object
            user_prompt = UserPrompt(input=formatted_profile)

            # Process the input
            LOG.info(f"Summarizing profile with {len(profile.facts)} facts")
            result = await agent.generate(user_prompt)

            # Log the raw result
            LOG.info("Raw summary result:")
            LOG.info(result["message"])

            # Create a ProfileSummary object
            summary = ProfileSummary(summary=result["message"])

            LOG.info(f"Successfully created profile summary")
            return summary
        else:
            LOG.warning("No profile facts provided for summarization")
            return ProfileSummary(summary="No profile information available.")
    except Exception as e:
        LOG.error(f"Error summarizing profile data: {e}")
        return ProfileSummary(summary="Unable to generate profile summary due to an error.")


async def main():
    """Main function to run examples."""
    # Example: Summarizing profile information
    print("Example: Summarizing profile information")
    from schemas.agents.profile.profile_schema import UserProfile

    # Create a sample profile
    profile = UserProfiles(facts=[
        UserProfile(domain="basic_info", attribute="name", description="Emily Johnson"),
        UserProfile(domain="basic_info", attribute="age", description="28 years old"),
        UserProfile(domain="work", attribute="profession", description="Graphic Designer"),
        UserProfile(domain="work", attribute="experience", description="5 years of professional experience"),
        UserProfile(domain="career", attribute="job_offer",
                    description="Received offer at a design agency in New York with $85,000 salary"),
        UserProfile(domain="plan", attribute="relocation",
                    description="Considering moving to New York for a new job opportunity")
    ])

    print(f"Original profile has {len(profile.facts)} facts")
    for fact in profile.facts:
        print(f"- {fact.domain} / {fact.attribute}: {fact.description}")

    print("\nSummarizing profile...")
    profile_summary = await summarize_profile(profile)

    if profile_summary:
        print("\nProfile Summary:")
        print(profile_summary.summary)


if __name__ == "__main__":
    asyncio.run(main())