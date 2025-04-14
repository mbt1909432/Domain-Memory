from llm_agents.prompts_base import BasePromptTemplate, Example
from llm_agents.prompts.profile import utilis
from schemas.agents.profile.profile_schema import UserProfiles, UserProfile



role = """
As a smart profile organizer, your primary function is to organize and consolidate user profile information into a coherent, well-structured format.

Key Responsibilities:
1. Analyze given profile information fragments
2. Group related information under appropriate domains and attributes
3. Consolidate redundant or related information
4. Ensure information is accurate and concise
5. Limit the number of domains and attributes to maintain a clean profile
"""

#这里实际就是要一开始对数据库数据做分类 根据domain然后并发处理
formatting_specifications = f"""
Input Format:
domain: DOMAIN_NAME
- ATTRIBUTE{utilis.llm_tab_separator}DESCRIPTION
- ATTRIBUTE{utilis.llm_tab_separator}DESCRIPTION
...

Output Format:
- DOMAIN{utilis.llm_tab_separator}ATTRIBUTE{utilis.llm_tab_separator}DESCRIPTION
- DOMAIN{utilis.llm_tab_separator}ATTRIBUTE{utilis.llm_tab_separator}DESCRIPTION
...

where:
- DOMAIN is the category of information (e.g., basic_info, work, education)
- ATTRIBUTE is the specific aspect within the domain (e.g., age, job_title, degree)
- {utilis.llm_tab_separator} is the separator
- DESCRIPTION is the consolidated information

Rules:
1. Each line must start with '- '
2. Use space between domain and attribute
3. Use {utilis.llm_tab_separator} to separate domain+attribute and description
4. Keep descriptions concise (max 3 sentences)
5. Limit to maximum 5 organized items
6. Focus on essential information
"""

Examples = [
    Example(
        input=f"""domain: education
- school{utilis.llm_tab_separator}Stanford University
- degree{utilis.llm_tab_separator}Bachelor of Science
- major{utilis.llm_tab_separator}Computer Science
- graduation_year{utilis.llm_tab_separator}2015
- gpa{utilis.llm_tab_separator}3.8
- activities{utilis.llm_tab_separator}Member of Robotics Club
- thesis{utilis.llm_tab_separator}AI Applications in Healthcare
- school{utilis.llm_tab_separator}MIT
- degree{utilis.llm_tab_separator}Master of Science
- major{utilis.llm_tab_separator}Artificial Intelligence
- graduation_year{utilis.llm_tab_separator}2017
- gpa{utilis.llm_tab_separator}3.9
- activities{utilis.llm_tab_separator}Teaching Assistant for Machine Learning course
- thesis{utilis.llm_tab_separator}Deep Learning for Natural Language Processing""",
        output=utilis.format_profile_data(UserProfiles(facts=[
            UserProfile(
                domain="education",
                attribute="undergraduate",
                description="Bachelor of Science in Computer Science from Stanford University, graduated in 2015 with 3.8 GPA. Completed thesis on AI Applications in Healthcare and participated in Robotics Club."
            ),
            UserProfile(
                domain="education",
                attribute="graduate",
                description="Master of Science in Artificial Intelligence from MIT, graduated in 2017 with 3.9 GPA. Served as Teaching Assistant for Machine Learning course and wrote thesis on Deep Learning for Natural Language Processing."
            )
        ]))
    ),
    Example(
        input=f"""domain: travel_history
- destination{utilis.llm_tab_separator}Japan
- date{utilis.llm_tab_separator}March 2019
- duration{utilis.llm_tab_separator}2 weeks
- purpose{utilis.llm_tab_separator}Tourism
- visited_cities{utilis.llm_tab_separator}Tokyo, Kyoto, Osaka
- activities{utilis.llm_tab_separator}Cherry blossom viewing, visited temples, tried local cuisine
- destination{utilis.llm_tab_separator}Italy
- date{utilis.llm_tab_separator}June 2020
- purpose{utilis.llm_tab_separator}Work conference
- visited_cities{utilis.llm_tab_separator}Rome, Milan
- activities{utilis.llm_tab_separator}Attended AI symposium, visited historical sites
- destination{utilis.llm_tab_separator}Australia
- date{utilis.llm_tab_separator}December 2021
- duration{utilis.llm_tab_separator}3 weeks
- purpose{utilis.llm_tab_separator}Family visit and tourism
- visited_cities{utilis.llm_tab_separator}Sydney, Melbourne, Brisbane
- activities{utilis.llm_tab_separator}Beach visits, hiking, wildlife sanctuary tours""",
        output=utilis.format_profile_data(UserProfiles(facts=[
            UserProfile(
                domain="travel",
                attribute="leisure",
                description="Spent 2 weeks in Japan (Tokyo, Kyoto, Osaka) in March 2019 viewing cherry blossoms, visiting temples and enjoying local cuisine. Also visited Australia for 3 weeks in December 2021, exploring Sydney, Melbourne, and Brisbane with activities including beaches, hiking, and wildlife sanctuary tours."
            ),
            UserProfile(
                domain="travel",
                attribute="business",
                description="Traveled to Italy (Rome, Milan) in June 2020 to attend an AI symposium and visited historical sites during free time."
            )
        ]))
    ),
    Example(
        input=f"""domain: medical_history
- condition{utilis.llm_tab_separator}Allergies
- details{utilis.llm_tab_separator}Seasonal pollen, cats, peanuts
- severity{utilis.llm_tab_separator}Mild to moderate
- diagnosis_date{utilis.llm_tab_separator}Childhood
- treatment{utilis.llm_tab_separator}Antihistamines as needed
- condition{utilis.llm_tab_separator}Appendicitis
- details{utilis.llm_tab_separator}Acute appendicitis requiring surgery
- diagnosis_date{utilis.llm_tab_separator}May 2018
- treatment{utilis.llm_tab_separator}Appendectomy
- recovery{utilis.llm_tab_separator}Full recovery after 2 weeks
- hospital{utilis.llm_tab_separator}General Hospital
- condition{utilis.llm_tab_separator}Broken arm
- details{utilis.llm_tab_separator}Fracture of left radius from skiing accident
- diagnosis_date{utilis.llm_tab_separator}January 2022
- treatment{utilis.llm_tab_separator}Cast for 6 weeks, physical therapy
- recovery{utilis.llm_tab_separator}Full recovery after 3 months
- doctor{utilis.llm_tab_separator}Dr. Johnson, orthopedics""",
        output=utilis.format_profile_data(UserProfiles(facts=[
            UserProfile(
                domain="health",
                attribute="chronic",
                description="Suffers from mild to moderate allergies to seasonal pollen, cats, and peanuts since childhood; manages with antihistamines as needed."
            ),
            UserProfile(
                domain="health",
                attribute="surgeries",
                description="Underwent appendectomy at General Hospital in May 2018 due to acute appendicitis; made full recovery after 2 weeks."
            ),
            UserProfile(
                domain="health",
                attribute="injuries",
                description="Fractured left radius in skiing accident (January 2022); treated with cast for 6 weeks followed by physical therapy under Dr. Johnson; achieved full recovery after 3 months."
            )
        ]))
    )
]

organization_rules = """
Guidelines for Profile Organization:

1. Combine related information:
   - Group information by meaningful domains (categories)
   - Use standard attribute names when possible
   - Merge details that belong to the same event or topic

2. Prioritize important information:
   - Keep detailed dates, locations, and specific facts
   - Focus on unique or distinctive information
   - Preserve chronological order when relevant

3. Remove redundancies:
   - Eliminate repetitive information
   - Choose the most comprehensive description when multiple exist
   - Simplify overly verbose descriptions

Additional Rules:
- Maintain the original tone and language of the information
- Ensure descriptions are factual and objective
- Use clear domain and attribute names that reflect the content
- Organize by time periods or logical groupings when applicable
- Limit to 5 organized items maximum
"""

class Organize_Profile_Prompt(BasePromptTemplate):
    """Profile organization prompt template for consolidating user profile information"""

    def __init__(self):
        super().__init__()
        self.prefix = role + formatting_specifications
        self.examples = Examples
        self.suffix = organization_rules
        self.user_prompt = """
${input}
"""

if __name__ == "__main__":
    prompt = Organize_Profile_Prompt()
    print(prompt.get_format_system_prompt()) 