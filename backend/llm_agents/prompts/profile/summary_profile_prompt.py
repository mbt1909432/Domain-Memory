from openai.types.responses.response_reasoning_item import Summary

from llm_agents.prompts_base import BasePromptTemplate, Example
from llm_agents.prompts.profile import utilis



role = """
Summarize the given user profile concisely, adhering to the following guidelines:

Keep the summary to 3 sentences or fewer.

Remove redundant or repetitive information, retaining only key details.

Maintain the original language of the input text.
"""

formatting_specifications = f""""""

Examples = []

organization_rules = """"""

class Summary_Profile_Prompt(BasePromptTemplate):
    """Profile organization prompt template for consolidating user profile information"""

    def __init__(self):
        super().__init__()
        self.prefix = role + formatting_specifications
        self.examples = []#Examples
        self.suffix = organization_rules
        self.user_prompt = """
${input}
"""

if __name__ == "__main__":
    prompt = Summary_Profile_Prompt()
    print(prompt.get_format_system_prompt()) 