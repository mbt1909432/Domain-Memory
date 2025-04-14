from typing import List, Union, Dict, Any


class UserProfileDomain:
    """
    Class representing a user profile domain with attributes.
    """
    def __init__(self, domain: str, attributes: List[Union[str, Dict[str, str]]]):
        self.domain = domain
        self.attributes = attributes
    
    def __repr__(self):
        return f"UserProfileDomain(domain={self.domain}, attributes={self.attributes})"
    
    def format_as_string(self) -> str:
        """
        Format the domain and its attributes as a string for display in prompts.
        """
        lines = [f"- {self.domain}:"]
        
        for attribute in self.attributes:
            if isinstance(attribute, str):
                lines.append(f"  - {attribute}")
            elif isinstance(attribute, dict) and "name" in attribute:
                desc = f" ({attribute.get('description', '')})" if "description" in attribute else ""
                lines.append(f"  - {attribute['name']}{desc}")
        
        return "\n".join(lines)


CANDIDATE_PROFILE_DOMAINS: List[UserProfileDomain] = [
    UserProfileDomain(
        "basic_info",
        attributes=[
            "Name",
            {
                "name": "Age",
                "description": "integer",
            },
            "Gender",
            "birth_date",
            "nationality",
            "ethnicity",
            "language_spoken",
        ],
    ),
    UserProfileDomain(
        "contact_info",
        attributes=[
            "email",
            "phone",
            "city",
            "country",
        ],
    ),
    UserProfileDomain(
        "education",
        attributes=[
            "school",
            "degree",
            "major",
        ],
    ),
    UserProfileDomain(
        "demographics",
        attributes=[
            "marital_status",
            "number_of_children",
            "household_income",
        ],
    ),
    UserProfileDomain(
        "work",
        attributes=[
            "company",
            "title",
            "working_industry",
            "previous_projects",
            "work_skills",
        ],
    ),
    UserProfileDomain(
        "interest",
        attributes=[
            "books",
            "movies",
            "music",
            "foods",
            "sports",
        ],
    ),
    UserProfileDomain(
        "psychological",
        attributes=["personality", "values", "beliefs", "motivations", "goals"],
    ),
    UserProfileDomain(
        "life_event",
        attributes=["marriage", "relocation", "retirement"],
    ),
]


def format_all_domains() -> str:
    """
    Format all candidate profile domains as a string.
    
    Returns:
        str: Formatted string of all domains and attributes
    """
    return "\n".join(domain.format_as_string() for domain in CANDIDATE_PROFILE_DOMAINS)


if __name__ == "__main__":
    # Print all formatted domains for testing
    print(format_all_domains())
