"""
Test script for DataManager with new schema
Run this to verify Phase 1 implementation
"""
import json
import os
from src.data.data_manager import DataManager

def test_data_manager():
    print("Testing DataManager Phase 1 Implementation\n")
    print("=" * 60)
    
    # Create a test data file
    test_file = "data/test_tally_data.json"
    
    # Clean up any existing test file
    if os.path.exists(test_file):
        os.remove(test_file)
    
    # Initialize DataManager
    dm = DataManager(test_file)
    print("✓ DataManager initialized")
    
    # Test 1: Create empty structures
    print("\n1. Testing empty structure creation:")
    empty_section = dm.create_empty_section_structure()
    print(f"   Empty section has {len(empty_section)} top-level keys")
    assert "call_connects" in empty_section
    assert "call_nonconnects" in empty_section
    assert "call_inbetweens" in empty_section
    assert "other" in empty_section
    assert empty_section["call_connects"]["paid_lead"] == 0
    print("   ✓ Empty section structure correct")
    
    empty_entry = dm.create_empty_entry_structure()
    assert "current_leads" in empty_entry
    assert "prospects" in empty_entry
    print("   ✓ Empty entry structure correct")
    
    # Test 2: Add a user
    print("\n2. Testing user management:")
    dm.add_user("TestUser")
    users = dm.get_users()
    assert "TestUser" in users
    print(f"   ✓ User added: {users}")
    
    # Test 3: Save a complete entry
    print("\n3. Testing save_entry with new schema:")
    entry = {
        "user": "TestUser",
        "date": "2025-10-23",
        "current_leads": {
            "call_connects": {
                "paid_lead": 5,
                "organic_lead": 3,
                "agents": 2,
                "total": 10
            },
            "call_nonconnects": {
                "paid_lead": 8,
                "organic_lead": 4,
                "agents": 1,
                "total": 13
            },
            "call_inbetweens": {
                "paid_lead": 2,
                "organic_lead": 1,
                "agents": 0,
                "total": 3
            },
            "other": {
                "sms": 5,
                "email": 10,
                "total": 15
            },
            "grand_total": 41,
            "enrolment_packs": 3,
            "quotes": 5,
            "cpd_booked": 2,
            "grand_total_2": 10
        },
        "prospects": {
            "call_connects": {
                "paid_lead": 1,
                "organic_lead": 2,
                "agents": 0,
                "total": 3
            },
            "call_nonconnects": {
                "paid_lead": 3,
                "organic_lead": 1,
                "agents": 1,
                "total": 5
            },
            "call_inbetweens": {
                "paid_lead": 0,
                "organic_lead": 0,
                "agents": 0,
                "total": 0
            },
            "other": {
                "sms": 2,
                "email": 3,
                "total": 5
            },
            "grand_total": 13,
            "enrolment_packs": 1,
            "quotes": 2,
            "cpd_booked": 0,
            "grand_total_2": 3
        },
        "comments": "Test entry with new schema"
    }
    
    dm.save_entry(entry)
    print("   ✓ Entry saved")
    
    # Test 4: Load entry back
    print("\n4. Testing get_entry_for_user_and_date:")
    loaded_entry = dm.get_entry_for_user_and_date("TestUser", "2025-10-23")
    assert loaded_entry is not None
    assert loaded_entry["user"] == "TestUser"
    assert loaded_entry["current_leads"]["call_connects"]["paid_lead"] == 5
    assert loaded_entry["prospects"]["grand_total"] == 13
    print("   ✓ Entry loaded correctly")
    print(f"   Current Leads Grand Total: {loaded_entry['current_leads']['grand_total']}")
    print(f"   Prospects Grand Total: {loaded_entry['prospects']['grand_total']}")
    
    # Test 5: Test validation with missing fields
    print("\n5. Testing validation with incomplete data:")
    incomplete_entry = {
        "user": "TestUser",
        "date": "2025-10-24",
        "current_leads": {
            "call_connects": {
                "paid_lead": 3
                # Missing other fields
            }
        },
        "comments": "Incomplete entry"
    }
    
    dm.save_entry(incomplete_entry)
    loaded_incomplete = dm.get_entry_for_user_and_date("TestUser", "2025-10-24")
    assert loaded_incomplete is not None
    # Should have all fields filled with defaults
    assert loaded_incomplete["current_leads"]["call_connects"]["organic_lead"] == 0
    assert loaded_incomplete["current_leads"]["call_nonconnects"]["paid_lead"] == 0
    assert loaded_incomplete["prospects"]["grand_total"] == 0
    print("   ✓ Missing fields filled with defaults")
    
    # Test 6: Test update existing entry
    print("\n6. Testing update existing entry:")
    updated_entry = {
        "user": "TestUser",
        "date": "2025-10-23",
        "current_leads": {
            "call_connects": {
                "paid_lead": 10,  # Changed from 5
                "organic_lead": 3,
                "agents": 2,
                "total": 15
            },
            "call_nonconnects": {
                "paid_lead": 8,
                "organic_lead": 4,
                "agents": 1,
                "total": 13
            },
            "call_inbetweens": {
                "paid_lead": 2,
                "organic_lead": 1,
                "agents": 0,
                "total": 3
            },
            "other": {
                "sms": 5,
                "email": 10,
                "total": 15
            },
            "grand_total": 46,  # Updated
            "enrolment_packs": 3,
            "quotes": 5,
            "cpd_booked": 2,
            "grand_total_2": 10
        },
        "prospects": dm.create_empty_section_structure(),
        "comments": "Updated entry"
    }
    
    dm.save_entry(updated_entry)
    loaded_updated = dm.get_entry_for_user_and_date("TestUser", "2025-10-23")
    assert loaded_updated["current_leads"]["call_connects"]["paid_lead"] == 10
    assert loaded_updated["comments"] == "Updated entry"
    print("   ✓ Entry updated successfully")
    
    # Test 7: Test date range query
    print("\n7. Testing get_data_for_date_range:")
    range_data = dm.get_data_for_date_range("2025-10-23", "2025-10-24")
    assert len(range_data) == 2
    print(f"   ✓ Found {len(range_data)} entries in range")
    
    # Display saved file structure
    print("\n8. Checking saved file structure:")
    with open(test_file, 'r') as f:
        saved_data = json.load(f)
    print(f"   Users: {saved_data['users']}")
    print(f"   Entries: {len(saved_data['entries'])}")
    print(f"   Sample entry structure keys: {list(saved_data['entries'][0].keys())}")
    
    # Clean up test file
    os.remove(test_file)
    print("\n" + "=" * 60)
    print("✓ All Phase 1 tests passed!")
    print("DataManager is ready for Phase 2 integration")

if __name__ == "__main__":
    test_data_manager()
