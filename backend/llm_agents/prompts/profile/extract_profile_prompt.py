from llm_agents.prompts_base import BasePromptTemplate, Example
from llm_agents.prompts.profile import utilis
from llm_agents.prompts.profile.predefined_domain_attribute import format_all_domains

role="""
As a licensed psychologist, your primary function is to analyze conversations between users and other parties to assess psychological states.

Key Responsibilities:

Data Extraction – Identify and document explicitly stated facts, preferences, and behavioral patterns expressed by the user.

Contextual Inference – Analyze implicit cues (tone, word choice, emotional subtext) to uncover unspoken needs or underlying conditions.

User-Centric Documentation – Record observations using the user's original language to preserve authenticity while maintaining clinical objectivity.
"""
formatting_specifications="""Formatting Specifications
Input
Domain Guidelines
You will receive predefined domains and attributes to prioritize for extraction.
Create new domains/attributes if necessary.

User's Existing Domains
You will see domains/attributes the user previously shared.
Reuse existing classifications for repeated content (e.g., work → title).

Chat Format
Conversations are structured as:

[TIME] NAME: MESSAGE
Parse content and note timestamps.

Output
Extract information in strict format:

DOMAIN ATTRIBUTE DESCRIPTION
Example:

basic_info name alex

work title Data Scientist

Rules

DOMAIN: Broad category (e.g., basic_info, work)

ATTRIBUTE: Sub-category label (e.g., name, title)

DESCRIPTION: Explicit or inferred user-specific content

Format Enforcement:

Each line starts with - , elements separated by tabs (\t)

Spaces or other delimiters are prohibited"""
Examples=[
    Example(
        input="My name is Li Ming, I'm 28 years old, and I'm a software engineer. I've been working at Alibaba for 3 years.",
        output=utilis.format_profile_data(utilis.UserProfiles(facts=[
            utilis.UserProfile(
                domain="basic_info",
                attribute="name",
                description="Li Ming"
            ),
            utilis.UserProfile(
                domain="basic_info",
                attribute="age",
                description="28 years old"
            ),
            utilis.UserProfile(
                domain="work",
                attribute="profession",
                description="software engineer"
            ),
            utilis.UserProfile(
                domain="work",
                attribute="company",
                description="Alibaba"
            ),
            utilis.UserProfile(
                domain="work",
                attribute="experience",
                description="working for 3 years"
            )
        ]))
    ),
    Example(
        input="I like playing basketball and watching movies. I'm currently learning English and hope to travel to the United States next year.",
        output=utilis.format_profile_data(utilis.UserProfiles(facts=[
            utilis.UserProfile(
                domain="interest",
                attribute="hobby",
                description="likes playing basketball and watching movies"
            ),
            utilis.UserProfile(
                domain="education",
                attribute="learning",
                description="currently learning English"
            ),
            utilis.UserProfile(
                domain="plan",
                attribute="travel",
                description="hopes to travel to the United States next year"
            )
        ]))
    ),
    Example(
        input="I plan to move to Shanghai next year. I've already found a new job with a monthly salary of 25,000.",
        output=utilis.format_profile_data(utilis.UserProfiles(facts=[
            utilis.UserProfile(
                domain="plan",
                attribute="relocation",
                description="plans to move to Shanghai"
            ),
            utilis.UserProfile(
                domain="work",
                attribute="new_job",
                description="already found a new job"
            ),
            utilis.UserProfile(
                domain="finance",
                attribute="salary",
                description="monthly salary of 25,000"
            )
        ]))
    ),
    Example(
        input="I graduated from Peking University with a master's degree in Computer Science. I previously interned at Tencent for six months.",
        output=utilis.format_profile_data(utilis.UserProfiles(facts=[
            utilis.UserProfile(
                domain="education",
                attribute="university",
                description="graduated from Peking University"
            ),
            utilis.UserProfile(
                domain="education",
                attribute="major",
                description="Computer Science"
            ),
            utilis.UserProfile(
                domain="education",
                attribute="degree",
                description="master's degree"
            ),
            utilis.UserProfile(
                domain="work",
                attribute="internship",
                description="interned at Tencent for six months"
            )
        ]))
    )
]
extraction_rules=f"""
Return the facts and preferences in a markdown list format as shown above.


Remember the following:
Time Precision
- Time Precision:Infer exact dates (e.g., 2025/03/15) from context. Relative terms (e.g., "tomorrow") are prohibited.
- Implicit Context: You should infer what's implied from the conversation, not just what's explicitly stated (e.g., infer marital status from "our anniversary").
- Format Compliance:Make sure to return the response in the format mentioned in the formatting & examples section.
- Language Alignment: Match description language to user input (CN/EN), with domains/attributes in English.
- Null Handling: If you do not find anything relevant facts, user memories, and preferences in the below conversation, just return "NONE" or "NO FACTS".
- Domain Scope: Below is the list of domain and attribute that you should focus on collecting and extracting:
{format_all_domains()}

Don't record the domains and attributes that are not mentioned in the following conversation.
"""



class Extract_Profile_Prompt(BasePromptTemplate):
    """Basic chat prompt template"""

    def __init__(self):
        super().__init__()

        self.prefix = role+formatting_specifications

        self.examples = Examples

        self.suffix = extraction_rules

        self.user_prompt = """
${input}
"""


if __name__ == "__main__":
    prompt = Extract_Profile_Prompt()
    print(prompt.get_format_system_prompt())

