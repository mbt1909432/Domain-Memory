from llm_agents.agent_group.profile import extract_agent, update_agent, organize_agent, utilis,summary_agent
from models.user_profile_facts_database import UserProfileFacts
from schemas.agents.profile.profile_schema import (
    UserProfile, UserProfiles, ChatBlob, OpenAICompatibleMessage,
    ProfileProcessResult, ProfileUpdateResult
)
from services.user_profile_service import UserProfileService
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from utils.config import LOG


async def process_user_chat_and_update_profile(chat: ChatBlob) -> ProfileProcessResult:
    """
    处理用户聊天并更新个人资料，将所有数据库操作放在最后执行
    
    Args:
        chat: 用户聊天历史
        
    Returns:
        ProfileProcessResult: 处理结果摘要，包含提取的新信息、更新的信息和组织后的资料
    """
    result_summary = ProfileProcessResult()
    
    try:
        # 步骤1: 从聊天中提取个人资料
        LOG.info("步骤1: 从聊天中提取新的个人资料信息")
        new_profiles = await extract_agent.extract_profile(chat)
        if not new_profiles or not hasattr(new_profiles, 'facts') or not new_profiles.facts:
            LOG.warning("未能从聊天中提取到任何个人资料信息")
            result_summary.status = "warning"
            result_summary.message = "未能从聊天中提取到任何个人资料信息"
            return result_summary
            
        # 将提取的信息添加到结果摘要，创建UserProfiles对象
        extracted_profiles = [
            UserProfile(
                domain=p.domain,
                attribute=p.attribute,
                description=p.description
            )
            for p in new_profiles.facts
        ]
        result_summary.extracted_profiles = UserProfiles(facts=extracted_profiles)
        LOG.info(f"提取了 {len(new_profiles.facts)} 项个人资料信息")
        
        # 步骤2: 从数据库获取现有的个人资料
        LOG.info("步骤2: 从数据库获取现有的个人资料")
        old_profiles = await UserProfileService.get_all_profile_facts()
        
        # 步骤3: 找出新数据中存在但旧数据中不存在的信息（差集）
        LOG.info("步骤3: 计算新旧数据的差异,后续直接将差异数据插入数据库中")
        different_profiles = utilis.extract_different_facts(old_profiles, new_profiles)
        LOG.info(f"发现 {len(different_profiles.facts) if hasattr(different_profiles, 'facts') else 0} 项全新的个人资料信息")
        
        # 步骤4: 对比新旧数据，找出需要更新的信息
        LOG.info("步骤4: 计算需要更新的个人资料项，需要和旧数据进行对比，做Update操作")
        update_requests = utilis.generate_profile_updates(old_profiles, new_profiles)
        LOG.info(f"发现 {len(update_requests)} 项需要更新的个人资料信息")
        
        # 步骤5: 处理所有需要更新的信息
        LOG.info("步骤5: 处理需要更新的项目")
        update_results = []
        if update_requests:
            # 定义处理单个更新的异步函数
            async def process_update(update):
                return await update_agent.update_profile(update)
            
            # 并发处理所有更新
            update_tasks = [process_update(update) for update in update_requests]
            update_results = await asyncio.gather(*update_tasks)
            
            # 将更新结果添加到摘要
            result_summary.updates = [
                ProfileUpdateResult(
                    domain=result.domain,
                    attribute=result.attribute,
                    action=result.action,
                    description=result.description
                )
                for result in update_results
            ]
        
        # 步骤6: 将要执行的数据库操作收集起来，准备最后执行
        LOG.info("步骤6: 收集所有需要执行的数据库操作")
        db_operations = []
        
        # 添加新数据的操作，临时存入列表后续在做操作
        if hasattr(different_profiles, 'facts') and different_profiles.facts:
            db_operations.append(("add_multiple", different_profiles))
        
        # 添加更新操作，临时存入列表后续在做操作
        for update in update_results:
            db_operations.append(("update", update))
        
        # 步骤7: 获取按领域分类的所有资料
        LOG.info("步骤7: 获取按领域分类的所有资料（模拟更新后的结果）")
        # 这里不直接从数据库获取，而是模拟更新后的结果
        updated_profiles = await simulate_updated_profiles(old_profiles, different_profiles, update_results)
        profile_list_by_domains = await group_profiles_by_domain(updated_profiles)
        
        # 步骤8: 组织各领域的资料（并发处理）
        LOG.info("步骤8: 组织各领域的资料")
        organize_tasks = [organize_agent.organize_profile(profile) for profile in profile_list_by_domains]
        user_profiles_list = await asyncio.gather(*organize_tasks)
        
        # 步骤9: 处理组织后的结果
        LOG.info("步骤9: 处理组织后的结果")
        organized_profiles = []
        for domain_profiles in user_profiles_list:
            if hasattr(domain_profiles, 'facts'):
                for profile in domain_profiles.facts:
                    organized_profiles.append(profile)
        
        # 将组织后的结果添加到摘要，创建UserProfiles对象
        organized_profile_list = [
            UserProfile(
                domain=p.domain,
                attribute=p.attribute,
                description=p.description
            )
            for p in organized_profiles
        ]
        result_summary.organized_profiles = UserProfiles(facts=organized_profile_list)

        # 步骤10: 对组织后的结果进行总结
        LOG.info("步骤10: 获取最后总结的数据")
        organized_user_profiles = UserProfiles(facts=organized_profiles)
        summary_result = await summary_agent.summarize_profile(organized_user_profiles)
        
        if summary_result and hasattr(summary_result, 'summary'):
            result_summary.profile_summary = summary_result.summary
            LOG.info(f"生成资料总结: {summary_result.summary}")
        else:
            LOG.warning("无法生成资料总结")
            result_summary.profile_summary = "无法生成资料总结"
        
        # 步骤11: 执行所有数据库操作
        LOG.info("步骤11: 执行所有数据库操作")
        await execute_db_operations(db_operations)
        
        return result_summary
        
    except Exception as e:
        LOG.error(f"处理聊天和更新个人资料时出错: {str(e)}")
        result_summary.status = "error"
        result_summary.message = f"处理过程中出错: {str(e)}"
        return result_summary


async def simulate_updated_profiles(
    old_profiles: UserProfiles, 
    different_profiles: UserProfiles,
    update_results: List[Any]
) -> UserProfiles:
    """
    模拟数据库操作后的个人资料状态
    
    Args:
        old_profiles: 原有的个人资料
        new_profiles: new_profile里的different profile
        update_results: 更新操作的结果
        
    Returns:
        模拟更新后的个人资料集合
    """
    # 复制原有的事实列表
    updated_facts = []
    if hasattr(old_profiles, 'facts'):
        updated_facts = [
            UserProfile(
                domain=fact.domain,
                attribute=fact.attribute,
                description=fact.description
            )
            for fact in old_profiles.facts
        ]
    
    # 添加新的事实
    if hasattr(different_profiles, 'facts'):
        for fact in different_profiles.facts:
            updated_facts.append(
                UserProfile(
                    domain=fact.domain,
                    attribute=fact.attribute,
                    description=fact.description
                )
            )
    
    # 应用更新
    for update in update_results:
        # 查找并更新对应的事实
        for i, fact in enumerate(updated_facts):
            if fact.domain == update.domain and fact.attribute == update.attribute:
                updated_facts[i] = UserProfile(
                    domain=update.domain,
                    attribute=update.attribute,
                    description=update.description
                )
                break
    
    return UserProfiles(facts=updated_facts)


async def group_profiles_by_domain(profiles: UserProfiles) -> List[UserProfiles]:
    """
    将个人资料按领域分组
    
    Args:
        profiles: 所有个人资料
        
    Returns:
        按领域分组的个人资料列表
    """
    domain_facts = {}
    if hasattr(profiles, 'facts'):
        for fact in profiles.facts:
            if fact.domain not in domain_facts:
                domain_facts[fact.domain] = []
            domain_facts[fact.domain].append(fact)
    
    return [UserProfiles(facts=facts) for facts in domain_facts.values()]


#TODO: 目前organize_profile操作没有入库但是先不要弄不然感觉会混乱
async def execute_db_operations(operations: List[Tuple[str, Any]]) -> None:
    """
    执行数据库操作
    
    Args:
        operations: 操作列表，每个操作是一个元组 (操作类型, 数据)
    """
    for op_type, data in operations:
        try:
            if op_type == "add_multiple" and hasattr(data, 'facts') and data.facts:
                LOG.info(f"添加 {len(data.facts)} 项新的个人资料信息到数据库")
                await UserProfileService.add_multiple_profile_facts(data)
            
            elif op_type == "update":
                LOG.info(f"更新数据库中的个人资料: {data.domain}.{data.attribute}")
                await UserProfileService.update_profile_description_by_domain_attribute(
                    data.domain, data.attribute, data.description
                )
        except Exception as e:
            LOG.error(f"执行数据库操作 {op_type} 时出错: {str(e)}")
            # 这里可以选择继续执行其他操作，或者抛出异常中断执行


async def main():
    """Main function to run examples."""
    # 示例：从聊天中提取信息并更新个人资料
    print("示例：从聊天中提取信息并更新个人资料")
    
    # 模拟客户端输入对话
    chat = ChatBlob(messages=[
        OpenAICompatibleMessage(role="user", content="Hi, my name is Emily."),
        OpenAICompatibleMessage(role="assistant", content="Hello Emily, how can I help you today?"),
        OpenAICompatibleMessage(role="user",
                              content="I'm 28 years old and work as a graphic designer. I've been considering a move to New York."),
        OpenAICompatibleMessage(role="assistant",
                              content="That sounds exciting! What's prompting you to consider moving to New York?"),
        OpenAICompatibleMessage(role="user",
                              content="I've been offered a job at a design agency there with a salary of $85,000.")
    ])
    
    # 处理聊天并更新个人资料
    result = await process_user_chat_and_update_profile(chat)
    
    # 打印处理结果
    print("\n" + "="*50)
    print("处理结果:")
    print("="*50)
    print(f"状态: {result.status}")
    
    if result.message:
        print(f"消息: {result.message}")
    
    print("\n" + "-"*30)
    print(f"提取的新信息 ({len(result.extracted_profiles)}):")
    print("-"*30)
    for profile in result.extracted_profiles.facts:
        print(f"- {profile.domain}.{profile.attribute}: {profile.description}")
    
    print("\n" + "-"*30)
    print(f"更新的信息 ({len(result.updates)}):")
    print("-"*30)
    for update in result.updates:
        print(f"- {update.domain}.{update.attribute} ({update.action}): {update.description}")
    
    print("\n" + "-"*30)
    print(f"组织后的信息 ({len(result.organized_profiles)}):")
    print("-"*30)
    for profile in result.organized_profiles.facts:
        print(f"- {profile.domain}.{profile.attribute}: {profile.description}")
    
    print("\n" + "-"*30)
    print("资料总结:")
    print("-"*30)
    print(result.profile_summary if result.profile_summary else "未生成资料总结")
    
    print("\n" + "="*50)


if __name__ == "__main__":
    asyncio.run(main())


