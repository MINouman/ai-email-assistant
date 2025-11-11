from app.services.ai.llm_service import llm_service
from app.services.ai.email_processor import email_processor

def test_summarization():
    print("\n"+"="*40)
    print("TEST 1: Email Summarization")
    print("-"*40)

    email = """
     Hi John,
    
    I hope this email finds you well. I wanted to follow up on our discussion
    from last week about the Q4 marketing campaign. We need to finalize the
    budget by Friday, November 15th.
    
    Could you please review the attached proposal and let me know your thoughts?
    We also need to schedule a meeting with the design team to discuss the
    creative assets.
    
    Best regards,
    Sarah
    """

    summary = llm_service.summarize_email(email, "Q4 Marketing Campaign Follow-up")
    print(f"\n Summary: \n{summary}\n")

def test_intent_detection():
    print("\n"+"="*40)
    print("TEST 2: Intent Detection")
    print("-"*40)

    email = """"
    URGENT: Server downtime scheduled for tonight at 11 PM.
    Please save all your work and log out before then.
    Expected duration: 2 hours.
    """

    result = llm_service.detect_intent(email, "URGENT: Server maintenance")
    print(f"Intent: {result.get('intent')}")
    print(f"Priority: {result.get('priority')}")
    print(f"Reasoning: {result.get('reasoning')}\n")

def test_entity_extraction():
    print("\n"+"="*40)
    print("TEST 3: Entity Extraction")
    print("-"*40)

    email = """"
    Hi team,
    
    Our meeting with Microsoft representatives is scheduled for December 5th
    at their Seattle office. John Smith and Sarah Johnson from their Azure team
    will be joining us. Please prepare the quarterly reports and bring your
    laptops for the product demo.
    """

    entities = llm_service.extract_entities(email)
    print(f"\nPeople: {entities.get('people')}")
    print(f"Organizations: {entities.get('organizations')}")
    print(f"Dates: {entities.get('dates')}")
    print(f"Locations: {entities.get('locations')}")
    print(f"Action Items: {entities.get('action_items')}\n")

def test_full_processing():
    print("\n" + "="*40)
    print("TEST 4: Full Email Processing")
    print("="*40)

    email_data = {
        "message_id": "test_123",
        "subject": "Project Deadline Extension Request",
        "body": """
        Hi Manager,
        
        I'm writing to request an extension for the project deadline.
        Due to unexpected technical challenges with the database migration,
        we need an additional week to ensure quality delivery.
        
        Current deadline: November 20th
        Requested new deadline: November 27th
        
        Please let me know if this is acceptable.
        
        Thanks,
        Developer
        """,
        "sender": "developer@company.com"
    }
    
    result = email_processor.process_email(email_data)
    
    print(f"\nSummary: {result.get('summary')}")
    print(f"Intent: {result.get('intent')}")
    print(f"Priority: {result.get('priority')}")
    print(f"Reasoning: {result.get('reasoning')}")
    
    print(f"\nReply Suggestions:")
    for i, reply in enumerate(result.get('reply_suggestions', []), 1):
        print(f"  {i}. [{reply.get('tone')}] {reply.get('text')}")
    
    print()


if __name__ == "__main__":
    print("\nAI Email Processing Test Suite")
    print("=" * 40)
    
    try:
        test_summarization()
        test_intent_detection()
        test_entity_extraction()
        test_full_processing()
        
        print("\nAll tests completed successfully!\n")
    
    except Exception as e:
        print(f"\nTest failed: {e}\n")