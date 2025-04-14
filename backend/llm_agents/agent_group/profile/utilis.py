from typing import List
from schemas.agents.profile.profile_schema import UserProfiles, ProfileUpdateInput, UserProfile

def generate_profile_updates(old_profile: UserProfiles, new_profile: UserProfiles) -> List[ProfileUpdateInput]:
    """
    Compare two UserProfiles and generate a list of ProfileUpdateInput for matching domain and attribute pairs.
    
    Args:
        old_profile: Original UserProfiles object
        new_profile: New UserProfiles object to compare against
        
    Returns:
        List of ProfileUpdateInput objects for matching domain/attribute pairs
    """
    updates = []
    
    # Create a dictionary of (domain, attribute) -> description for old profile
    old_facts = {(fact.domain, fact.attribute): fact.description for fact in old_profile.facts}
    
    # Compare with new profile facts
    for new_fact in new_profile.facts:
        key = (new_fact.domain, new_fact.attribute)
        if key in old_facts:
            # Found matching domain and attribute
            updates.append(
                ProfileUpdateInput(
                    domain=new_fact.domain,
                    attribute=new_fact.attribute,
                    old_description=old_facts[key],
                    new_description=new_fact.description
                )
            )
    
    return updates


def merge_profiles_keep_different(old_profile: UserProfiles, new_profile: UserProfiles) -> UserProfiles:
    """
    Compare old and new profiles and create a merged profile.
    Keep all facts from the new profile where either domain or attribute is different from any in old profile.
    For facts with matching domain and attribute, keep the new profile's version.
    
    Args:
        old_profile: Original UserProfiles object
        new_profile: New UserProfiles object to merge with
        
    Returns:
        Merged UserProfiles object
    """
    # Create a dictionary of (domain, attribute) -> fact for old profile
    old_facts_dict = {(fact.domain, fact.attribute): fact for fact in old_profile.facts}
    
    # Start with all facts from new profile
    merged_facts = list(new_profile.facts)
    
    # Create a dictionary of (domain, attribute) -> fact for new profile
    new_facts_dict = {(fact.domain, fact.attribute): fact for fact in new_profile.facts}
    
    # Add facts from old profile that don't exist in new profile
    for key, old_fact in old_facts_dict.items():
        if key not in new_facts_dict:
            merged_facts.append(old_fact)
    
    # Return merged profile
    return UserProfiles(facts=merged_facts)


def extract_different_facts(old_profile: UserProfiles, new_profile: UserProfiles) -> UserProfiles:
    """
    Compare old and new profiles and extract facts from new profile where domain or attribute differs from any in old profile.
    
    Args:
        old_profile: Original UserProfiles object
        new_profile: New UserProfiles object to compare against
        
    Returns:
        UserProfiles object containing only the different facts from new profile
    """
    # Create a set of (domain, attribute) tuples from old profile
    old_keys = {(fact.domain, fact.attribute) for fact in old_profile.facts}
    
    # Extract facts from new profile that have different domain/attribute combinations
    different_facts = [
        fact for fact in new_profile.facts
        if (fact.domain, fact.attribute) not in old_keys
    ]
    
    return UserProfiles(facts=different_facts)


def main():
    """Example usage"""
    from schemas.agents.profile.profile_schema import UserProfiles, UserProfile
    
    # Create example old profile
    old_profile = UserProfiles(facts=[
        UserProfile(domain="basic_info", attribute="age", description="User is 39 years old"),
        UserProfile(domain="interest", attribute="food", description="Love cheese pizza"),
        UserProfile(domain="work", attribute="position", description="Software Engineer")
    ])
    
    # Create example new profile with some updates and new facts
    new_profile = UserProfiles(facts=[
        UserProfile(domain="basic_info", attribute="age", description="User is 40 years old"),
        UserProfile(domain="interest", attribute="food", description="Love chicken pizza"),
        UserProfile(domain="hobby", attribute="sports", description="Plays basketball"),  # New domain/attribute
        UserProfile(domain="education", attribute="degree", description="Bachelor in Computer Science")  # New domain/attribute
    ])
    
    # Test profile updates
    print("=== Testing generate_profile_updates ===")
    updates = generate_profile_updates(old_profile, new_profile)
    print(f"Found {len(updates)} profile updates:")
    for update in updates:
        print(f"Domain: {update.domain}, Attribute: {update.attribute}")
        print(f"Old: {update.old_description}")
        print(f"New: {update.new_description}\n")
    
    # Test extracting different facts
    print("=== Testing extract_different_facts ===")
    different_facts = extract_different_facts(old_profile, new_profile)
    print(f"Found {len(different_facts.facts)} facts with different domain/attribute:")
    for fact in different_facts.facts:
        print(f"Domain: {fact.domain}, Attribute: {fact.attribute}, Description: {fact.description}")
    
    # Test merging profiles
    print("\n=== Testing merge_profiles_keep_different ===")
    merged_profile = merge_profiles_keep_different(old_profile, new_profile)
    print(f"Merged profile has {len(merged_profile.facts)} facts:")
    for fact in merged_profile.facts:
        print(f"Domain: {fact.domain}, Attribute: {fact.attribute}, Description: {fact.description}")


if __name__ == "__main__":
    main()
