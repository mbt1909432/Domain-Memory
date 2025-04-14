from llm_agents.prompts_base import BasePromptTemplate, Example
from llm_agents.prompts.profile import utilis
from llm_agents.prompts.profile.predefined_domain_attribute import format_all_domains
from pydantic import BaseModel, Field

class UpdateProfileResult(BaseModel):
    action: str = Field(..., description="Action to take: UPDATE, MERGE, or KEEP")
    description: str = Field(..., description="The final merged profile information")

def format_update_result(result):
    """
    Format an UpdateProfileResult into a string
    
    Args:
        result: An UpdateProfileResult model
        
    Returns:
        str: Formatted string with action and description
    """
    return f"- {result.action}{utilis.llm_tab_separator}{result.description}"

role = """
As a smart profile manager, your primary function is to manage and update user profile information by intelligently merging new information with existing data.

Key Responsibilities:
1. Analyze both old and new profile information
2. Determine the appropriate action (UPDATE/MERGE/KEEP)
3. Generate concise, accurate merged information
4. Maintain consistency in profile data
"""

formatting_specifications = f"""
Input Format:
## domain attribute
basic_info age (example)

## Old Description
existing profile information

## New Description
new profile information

Output Format:
- ACTION{utilis.llm_tab_separator}DESCRIPTION
where:
- ACTION can be UPDATE, MERGE, or KEEP
- {utilis.llm_tab_separator} is the separator
- DESCRIPTION is the final merged information

Rules:
1. Each line must start with '- '
2. Use {utilis.llm_tab_separator} to separate action and description
3. Keep descriptions concise (max 5 sentences)
4. Focus on essential information
"""

Examples = [
    Example(
        input="""## domain attribute
basic_info age

## Old Description
User is 39 years old
## New Description
User is 40 years old""",
        output=format_update_result(UpdateProfileResult(
            action="UPDATE",
            description="User is 40 years old"
        ))
    ),
    Example(
        input="""## domain attribute
interest food

## Old Description
Love cheese pizza
## New Description
Love chicken pizza""",
        output=format_update_result(UpdateProfileResult(
            action="MERGE",
            description="Love cheese and chicken pizza"
        ))
    ),
    Example(
        input="""## domain attribute
basic_info birthday

## Old Description
1999/04/30
## New Description
User didn't provide any birthday""",
        output=format_update_result(UpdateProfileResult(
            action="KEEP",
            description="1999/04/30"
        ))
    )
]

update_rules = """
Guidelines for Profile Updates:

1. Replace (UPDATE) when:
   - New information directly contradicts old information
   - New information is more recent/accurate
   - Old information is outdated

2. Merge when:
   - Both old and new information contain unique details
   - Information complements rather than contradicts
   - Different aspects of the same topic are covered

3. Keep when:
   - New information is empty or less detailed
   - New information doesn't add value
   - Old information is still accurate and complete

Additional Rules:
- Keep descriptions concise (max 5 sentences)
- Focus on essential information
- Maintain consistency in formatting
- Use clear, unambiguous language
- Preserve specific details (dates, numbers, etc.)
"""

class Update_Profile_Prompt(BasePromptTemplate):
    """Profile update prompt template for merging and updating user profile information"""

    def __init__(self):
        super().__init__()
        self.prefix = role + formatting_specifications
        self.examples = Examples
        self.suffix = update_rules
        self.user_prompt = """
${input}
"""

if __name__ == "__main__":
    prompt = Update_Profile_Prompt()
    print(prompt.get_format_system_prompt())

