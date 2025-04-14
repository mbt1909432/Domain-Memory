from typing import Optional, List, Dict
from sqlalchemy import select, delete, update
from database.connector import get_db
from models.user_profile_facts_database import UserProfileFacts
from schemas.agents.profile.profile_schema import UserProfile, UserProfiles
import uuid
from utils.config import LOG

#TODO: 统一错误处理控制
class UserProfileService:
    """Service class for handling user profile facts operations"""
    
    @staticmethod
    async def add_profile_fact(user_profile: UserProfile) -> UserProfileFacts:
        """
        Add a new profile fact record.
        
        Args:
            user_profile: UserProfile object containing domain, attribute and description
            
        Returns:
            The created UserProfileFacts object
        """
        try:
            LOG.info(f"Adding profile fact: {user_profile.domain}.{user_profile.attribute}")
            with next(get_db()) as session:
                # Create new profile fact
                profile_fact = UserProfileFacts(
                    domain=user_profile.domain,
                    attribute=user_profile.attribute,
                    description=user_profile.description
                )
                
                # Add to session and commit
                session.add(profile_fact)
                session.commit()
                session.refresh(profile_fact)
                
                LOG.info(f"Successfully added profile fact: {profile_fact.id} - {profile_fact.domain}.{profile_fact.attribute}")
                return profile_fact
        except Exception as e:
            LOG.error(f"Error adding profile fact: {e}")
            raise
    
    @staticmethod
    async def add_multiple_profile_facts(profiles: UserProfiles) -> List[UserProfileFacts]:
        """
        Add multiple profile fact records in a single transaction.
        
        Args:
            profiles: UserProfiles object containing a list of UserProfile objects
            
        Returns:
            List of created UserProfileFacts objects
        """
        try:
            LOG.info(f"Adding {len(profiles.facts)} profile facts in bulk")
            with next(get_db()) as session:
                # Create profile fact objects
                profile_facts = []
                for profile in profiles.facts:
                    profile_fact = UserProfileFacts(
                        domain=profile.domain,
                        attribute=profile.attribute,
                        description=profile.description
                    )
                    profile_facts.append(profile_fact)
                
                # Add all to session and commit
                session.add_all(profile_facts)
                session.commit()
                
                # Refresh all objects to get their IDs
                for fact in profile_facts:
                    session.refresh(fact)
                
                LOG.info(f"Successfully added {len(profile_facts)} profile facts in bulk")
                return profile_facts
        except Exception as e:
            LOG.error(f"Error adding multiple profile facts: {e}")
            raise
    
    @staticmethod
    async def update_profile_fact(
        fact_id: uuid.UUID,
        user_profile: UserProfile
    ) -> Optional[UserProfileFacts]:
        """
        Update an existing profile fact record.
        
        Args:
            fact_id: The UUID of the fact to update
            user_profile: UserProfile object with updated information
            
        Returns:
            Updated UserProfileFacts object or None if not found
        """
        try:
            LOG.info(f"Updating profile fact with ID: {fact_id}")
            with next(get_db()) as session:
                # Get the fact by ID
                fact = session.query(UserProfileFacts).filter(UserProfileFacts.id == fact_id).first()
                if not fact:
                    LOG.warning(f"Profile fact with ID {fact_id} not found for update")
                    return None
                    
                LOG.info(f"Updating fact from {fact.domain}.{fact.attribute}: '{fact.description}' to {user_profile.domain}.{user_profile.attribute}: '{user_profile.description}'")
                
                # Update fields
                fact.domain = user_profile.domain
                fact.attribute = user_profile.attribute
                fact.description = user_profile.description
                    
                # Commit changes
                session.commit()
                session.refresh(fact)
                
                LOG.info(f"Successfully updated profile fact: {fact.id}")
                return fact
        except Exception as e:
            LOG.error(f"Error updating profile fact {fact_id}: {e}")
            raise
    
    @staticmethod
    async def delete_profile_fact(fact_id: uuid.UUID) -> bool:
        """
        Delete a profile fact record.
        
        Args:
            fact_id: The UUID of the fact to delete
            
        Returns:
            True if deletion was successful, False if record not found
        """
        try:
            LOG.info(f"Deleting profile fact with ID: {fact_id}")
            with next(get_db()) as session:
                # Get the fact by ID
                fact = session.query(UserProfileFacts).filter(UserProfileFacts.id == fact_id).first()
                if not fact:
                    LOG.warning(f"Profile fact with ID {fact_id} not found for deletion")
                    return False
                
                LOG.info(f"Deleting fact: {fact.domain}.{fact.attribute}: '{fact.description}'")
                
                # Delete the record
                session.delete(fact)
                session.commit()
                
                LOG.info(f"Successfully deleted profile fact with ID: {fact_id}")
                return True
        except Exception as e:
            LOG.error(f"Error deleting profile fact {fact_id}: {e}")
            raise
    
    @staticmethod
    async def get_profile_fact(fact_id: uuid.UUID) -> Optional[UserProfile]:
        """
        Get a profile fact by ID.
        
        Args:
            fact_id: The UUID of the fact to retrieve
            
        Returns:
            UserProfile object or None if not found
        """
        try:
            LOG.info(f"Getting profile fact with ID: {fact_id}")
            with next(get_db()) as session:
                fact = session.query(UserProfileFacts).filter(UserProfileFacts.id == fact_id).first()
                if not fact:
                    LOG.warning(f"Profile fact with ID {fact_id} not found")
                    return None
                
                LOG.info(f"Found profile fact: {fact.domain}.{fact.attribute}")
                return UserProfile(
                    domain=fact.domain,
                    attribute=fact.attribute,
                    description=fact.description
                )
        except Exception as e:
            LOG.error(f"Error getting profile fact {fact_id}: {e}")
            raise
    
    @staticmethod
    async def get_profile_facts_by_domain(domain: str) -> UserProfiles:
        """
        Get all profile facts for a specific domain.
        
        Args:
            domain: The domain to filter by
            
        Returns:
            UserProfiles object containing matching facts
        """
        try:
            LOG.info(f"Getting profile facts for domain: {domain}")
            with next(get_db()) as session:
                facts = session.query(UserProfileFacts).filter(UserProfileFacts.domain == domain).all()
                
                user_profiles = UserProfiles(
                    facts=[
                        UserProfile(
                            domain=fact.domain,
                            attribute=fact.attribute,
                            description=fact.description
                        )
                        for fact in facts
                    ]
                )
                
                LOG.info(f"Found {len(user_profiles.facts)} profile facts for domain: {domain}")
                return user_profiles
        except Exception as e:
            LOG.error(f"Error getting profile facts for domain {domain}: {e}")
            raise


    @staticmethod
    async def get_all_profile_facts() -> UserProfiles:
        """
        Get all profile facts from the database.
        
        Returns:
            UserProfiles object containing all facts
        """
        try:
            LOG.info("Getting all profile facts")
            with next(get_db()) as session:
                facts = session.query(UserProfileFacts).all()
                
                user_profiles = UserProfiles(
                    facts=[
                        UserProfile(
                            domain=fact.domain,
                            attribute=fact.attribute,
                            description=fact.description
                        )
                        for fact in facts
                    ]
                )
                
                LOG.info(f"Found {len(user_profiles.facts)} total profile facts")
                return user_profiles
        except Exception as e:
            LOG.error(f"Error getting all profile facts: {e}")
            raise
    
    @staticmethod
    async def get_all_profile_facts_by_domain() -> List[UserProfiles]:
        """
        Get all profile facts organized by domain.
        
        Returns:
            List of UserProfiles objects, each containing facts for a specific domain
        """
        try:
            LOG.info("Getting all profile facts organized by domain")
            with next(get_db()) as session:
                # Get all facts
                facts = session.query(UserProfileFacts).all()
                
                # Group facts by domain
                domain_facts = {}
                for fact in facts:
                    if fact.domain not in domain_facts:
                        domain_facts[fact.domain] = []
                    domain_facts[fact.domain].append(
                        UserProfile(
                            domain=fact.domain,
                            attribute=fact.attribute,
                            description=fact.description
                        )
                    )
                
                # Create a UserProfiles object for each domain
                result = []
                for domain, facts_list in domain_facts.items():
                    user_profiles = UserProfiles(facts=facts_list)
                    result.append(user_profiles)
                
                LOG.info(f"Found facts for {len(result)} domains")
                return result
        except Exception as e:
            LOG.error(f"Error getting profile facts by domain: {e}")
            raise
    
    @staticmethod
    async def get_profile_fact_by_domain_and_attribute(domain: str, attribute: str) -> Optional[UserProfile]:
        """
        Get a profile fact by domain and attribute.
        
        Args:
            domain: The domain to filter by
            attribute: The attribute to filter by
            
        Returns:
            UserProfile object or None if not found
        """
        try:
            LOG.info(f"Getting profile fact for {domain}.{attribute}")
            with next(get_db()) as session:
                fact = session.query(UserProfileFacts).filter(
                    UserProfileFacts.domain == domain,
                    UserProfileFacts.attribute == attribute
                ).first()
                
                if not fact:
                    LOG.warning(f"Profile fact for {domain}.{attribute} not found")
                    return None
                
                LOG.info(f"Found profile fact for {domain}.{attribute}: '{fact.description}'")
                return UserProfile(
                    domain=fact.domain,
                    attribute=fact.attribute,
                    description=fact.description
                )
        except Exception as e:
            LOG.error(f"Error getting profile fact for {domain}.{attribute}: {e}")
            raise
    
    @staticmethod
    async def update_profile_description_by_domain_attribute(
        domain: str,
        attribute: str,
        new_description: str
    ) -> Optional[UserProfileFacts]:
        """
        Update the description of a profile fact by domain and attribute.
        If the fact doesn't exist, returns None. If it exists, updates the description.
        
        Args:
            domain: The domain of the fact to update
            attribute: The attribute of the fact to update
            new_description: The new description value
            
        Returns:
            Updated UserProfileFacts object or None if not found
        """
        try:
            LOG.info(f"Updating description for {domain}.{attribute}")
            with next(get_db()) as session:
                # Find the fact by domain and attribute
                fact = session.query(UserProfileFacts).filter(
                    UserProfileFacts.domain == domain,
                    UserProfileFacts.attribute == attribute
                ).first()
                
                if not fact:
                    LOG.warning(f"Profile fact with domain={domain}, attribute={attribute} not found for update")
                    return None
                
                LOG.info(f"Updating description from '{fact.description}' to '{new_description}'")
                
                # Update only the description
                fact.description = new_description
                
                # Commit changes
                session.commit()
                session.refresh(fact)
                
                LOG.info(f"Successfully updated profile fact description: {fact.id}")
                return fact
        except Exception as e:
            LOG.error(f"Error updating profile description for {domain}.{attribute}: {e}")
            raise


async def main():
    """Example usage of UserProfileService"""
    try:
        # Create a single profile fact
        print("Adding a new profile fact...")
        user_profile = UserProfile(
            domain="basic_info",
            attribute="age",
            description="User is 30 years old"
        )
        fact1 = await UserProfileService.add_profile_fact(user_profile)
        print(f"Added fact: {fact1.id} - {fact1.domain}.{fact1.attribute}: {fact1.description}")
        
        # Test bulk insert with UserProfiles
        print("\nAdding multiple facts at once...")
        profiles = UserProfiles(facts=[
            UserProfile(
                domain="interests", 
                attribute="hobbies", 
                description="Enjoys reading and hiking"
            ),
            UserProfile(
                domain="basic_info", 
                attribute="name", 
                description="John Doe"
            ),
            UserProfile(
                domain="education", 
                attribute="degree", 
                description="Bachelor in Computer Science"
            )
        ])
        
        bulk_facts = await UserProfileService.add_multiple_profile_facts(profiles)
        
        print(f"Added {len(bulk_facts)} facts at once:")
        for i, fact in enumerate(bulk_facts, 1):
            print(f"Bulk fact {i}: {fact.id} - {fact.domain}.{fact.attribute}: {fact.description}")
        
        # Update description by domain and attribute
        print("\nUpdating description by domain and attribute...")
        updated_fact = await UserProfileService.update_profile_description_by_domain_attribute(
            domain="basic_info",
            attribute="age",
            new_description="User is 32 years old"
        )
        if updated_fact:
            print(f"Updated fact: {updated_fact.id} - {updated_fact.domain}.{updated_fact.attribute}: {updated_fact.description}")
        else:
            print("Fact not found for update")
            
        # Get all facts
        print("\nGetting all profile facts...")
        all_profiles = await UserProfileService.get_all_profile_facts()
        print(f"Total facts found: {len(all_profiles.facts)}")
        for i, profile in enumerate(all_profiles.facts, 1):
            print(f"Fact {i}: {profile.domain}.{profile.attribute} = {profile.description}")
        
        # Get facts by domain
        print("\nGetting all basic_info facts...")
        basic_info_profiles = await UserProfileService.get_profile_facts_by_domain("basic_info")
        for i, profile in enumerate(basic_info_profiles.facts, 1):
            print(f"Basic info fact {i}: {profile.domain}.{profile.attribute} = {profile.description}")
        
        # Update a fact
        print("\nUpdating first fact...")
        updated_profile = UserProfile(
            domain="basic_info",
            attribute="age",
            description="User is 31 years old"
        )
        updated_fact = await UserProfileService.update_profile_fact(
            fact_id=fact1.id,
            user_profile=updated_profile
        )
        if updated_fact:
            print(f"Updated fact: {updated_fact.id} - {updated_fact.domain}.{updated_fact.attribute}: {updated_fact.description}")
        else:
            print("Fact not found for update")
        
        # Delete a fact
        print("\nDeleting a fact...")
        deleted = await UserProfileService.delete_profile_fact(fact_id=bulk_facts[0].id)
        print(f"Deletion {'successful' if deleted else 'failed'}")
        
    except Exception as e:
        LOG.error(f"Error in example: {e}")
        print(f"An error occurred: {e}")

async def main2():
    result=await UserProfileService.get_all_profile_facts_by_domain()
    print(result)

if __name__ == "__main__":
    import asyncio
    #asyncio.run(main())
    asyncio.run(main2())