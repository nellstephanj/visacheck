"""Test script for Case Assignment Orchestration Service

This script tests the core functionality of the case assignment system
including agent management, scoring algorithms, and batch assignments.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

from services.case_assignment_service import (
    get_orchestrator,
    AgentType,
    ExpertiseLevel,
    CaseWorkerAgent
)


def test_agent_creation():
    """Test creating and configuring agents"""
    print("=" * 60)
    print("TEST 1: Agent Creation")
    print("=" * 60)
    
    agent = CaseWorkerAgent(
        agent_id="TEST001",
        name="Test Agent",
        agent_type=AgentType.HUMAN,
        max_capacity=10,
        case_type_expertise={
            "Schengen Short Stay": ExpertiseLevel.EXPERT
        },
        location_expertise={
            "Sydney FO": ExpertiseLevel.PROFICIENT
        }
    )
    
    print(f"✓ Created agent: {agent.name}")
    print(f"  - ID: {agent.agent_id}")
    print(f"  - Type: {agent.agent_type.value}")
    print(f"  - Capacity: {agent.max_capacity}")
    print(f"  - Can accept cases: {agent.can_accept_case()}")
    print()


def test_expertise_scoring():
    """Test expertise score calculation"""
    print("=" * 60)
    print("TEST 2: Expertise Scoring")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    agent = orchestrator.get_agent_by_id("H001")  # Sarah Mitchell
    
    if agent:
        # Test different case types
        test_cases = [
            ("Schengen Short Stay", "Sydney FO"),
            ("Work Visa", "Melbourne FO"),
            ("Student Visa", "Brisbane FO")
        ]
        
        print(f"Agent: {agent.name}")
        print("Expertise scores:")
        
        for case_type, location in test_cases:
            score = agent.get_expertise_score(case_type, location)
            print(f"  - {case_type} @ {location}: {score:.2f} / 3.0")
    
    print()


def test_workload_tracking():
    """Test workload and capacity tracking"""
    print("=" * 60)
    print("TEST 3: Workload Tracking")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    orchestrator.reset_workloads()  # Start fresh
    
    agent = orchestrator.get_agent_by_id("AI001")
    
    if agent:
        print(f"Agent: {agent.name}")
        print(f"Initial capacity: {agent.get_capacity_ratio():.1%}")
        
        # Simulate assigning cases
        test_case = {
            'application_number': 'TEST-001',
            'case_type': 'Schengen Short Stay',
            'intake_location': 'Sydney FO',
            'urgent': False
        }
        
        for i in range(5):
            agent.assign_case(test_case.copy())
        
        print(f"After 5 assignments: {agent.get_capacity_ratio():.1%}")
        print(f"Current workload: {agent.current_workload} / {agent.max_capacity}")
        print(f"Can accept more: {agent.can_accept_case()}")
    
    print()


def test_assignment_scoring():
    """Test the assignment scoring algorithm"""
    print("=" * 60)
    print("TEST 4: Assignment Scoring")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    orchestrator.reset_workloads()
    
    test_case = {
        'application_number': 'TEST-URGENT-001',
        'case_type': 'Schengen Short Stay',
        'intake_location': 'Sydney FO',
        'urgent': True,
        'nationality': 'Australian',
        'days_in_process': 5
    }
    
    print(f"Case: {test_case['case_type']} @ {test_case['intake_location']}")
    print(f"Urgent: {test_case['urgent']}")
    print()
    
    print("Agent Scores:")
    for agent in orchestrator.agents[:3]:  # Test first 3 agents
        score = orchestrator.calculate_assignment_score(agent, test_case)
        print(f"  {agent.name}: {score:.3f} ({score*100:.1f}%)")
    
    print()


def test_single_assignment():
    """Test assigning a single case"""
    print("=" * 60)
    print("TEST 5: Single Case Assignment")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    orchestrator.reset_workloads()
    
    test_case = {
        'application_number': 'TEST-SINGLE-001',
        'case_type': 'Work Visa',
        'intake_location': 'Melbourne FO',
        'urgent': False,
        'nationality': 'Indian',
        'days_in_process': 10
    }
    
    print(f"Assigning case: {test_case['application_number']}")
    print(f"Type: {test_case['case_type']} @ {test_case['intake_location']}")
    
    agent, score = orchestrator.assign_case_to_best_agent(test_case)
    
    if agent:
        print(f"✓ Assigned to: {agent.name}")
        print(f"  - Agent ID: {agent.agent_id}")
        print(f"  - Agent Type: {agent.agent_type.value}")
        print(f"  - Assignment Score: {score:.3f} ({score*100:.1f}%)")
        print(f"  - Agent Workload: {agent.current_workload} / {agent.max_capacity}")
    else:
        print("✗ No available agent found")
    
    print()


def test_batch_assignment():
    """Test batch assignment of multiple cases"""
    print("=" * 60)
    print("TEST 6: Batch Case Assignment")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    orchestrator.reset_workloads()
    
    # Create test cases
    test_cases = [
        {
            'application_number': f'BATCH-{i:03d}',
            'case_type': ['Schengen Short Stay', 'Work Visa', 'Student Visa'][i % 3],
            'intake_location': ['Sydney FO', 'Melbourne FO', 'Brisbane FO'][i % 3],
            'urgent': i < 3,  # First 3 are urgent
            'nationality': 'Test',
            'days_in_process': i + 1
        }
        for i in range(10)
    ]
    
    print(f"Assigning {len(test_cases)} cases...")
    print(f"Urgent cases: {sum(1 for c in test_cases if c['urgent'])}")
    
    assignments = orchestrator.assign_cases_batch(test_cases, prioritize_urgent=True)
    
    total_assigned = sum(
        len(data['cases']) 
        for agent_id, data in assignments.items() 
        if agent_id != 'unassigned'
    )
    total_unassigned = len(assignments.get('unassigned', {}).get('cases', []))
    
    print(f"\nResults:")
    print(f"  Total Assigned: {total_assigned}")
    print(f"  Total Unassigned: {total_unassigned}")
    print(f"  Success Rate: {(total_assigned / len(test_cases) * 100):.1f}%")
    
    print(f"\nAssignments by Agent:")
    for agent_id, data in assignments.items():
        if agent_id == 'unassigned':
            continue
        
        agent = data['agent']
        cases = data['cases']
        print(f"  {agent.name}: {len(cases)} cases")
        
        # Show first 3 cases
        for case_data in cases[:3]:
            case = case_data['case']
            score = case_data['score']
            urgent = "🔴" if case['urgent'] else "  "
            print(f"    {urgent} {case['application_number']} (score: {score:.2f})")
        
        if len(cases) > 3:
            print(f"    ... and {len(cases) - 3} more")
    
    print()


def test_recommendations():
    """Test recommendation generation"""
    print("=" * 60)
    print("TEST 7: Assignment Recommendations")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    orchestrator.reset_workloads()
    
    test_case = {
        'application_number': 'RECOMMEND-001',
        'case_type': 'Student Visa',
        'intake_location': 'Brisbane FO',
        'urgent': False,
        'nationality': 'Chinese',
        'days_in_process': 7
    }
    
    print(f"Getting recommendations for:")
    print(f"  {test_case['case_type']} @ {test_case['intake_location']}")
    
    recommendations = orchestrator.recommend_assignment(test_case)
    
    print(f"\nTop {len(recommendations)} Recommendations:")
    for idx, rec in enumerate(recommendations, 1):
        agent = rec['agent']
        score = rec['score']
        reasoning = rec['reasoning']
        
        print(f"\n#{idx} - {agent.name}")
        print(f"  Score: {score:.3f} ({score*100:.1f}%)")
        print(f"  Type: {agent.agent_type.value}")
        print(f"  Workload: {agent.current_workload}/{agent.max_capacity}")
        print(f"  Reasoning:")
        for reason in reasoning:
            print(f"    • {reason}")
    
    print()


def test_workload_summary():
    """Test workload summary generation"""
    print("=" * 60)
    print("TEST 8: Workload Summary")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    orchestrator.reset_workloads()
    
    # Assign some test cases
    for i in range(20):
        test_case = {
            'application_number': f'SUMMARY-{i:03d}',
            'case_type': ['Schengen Short Stay', 'Work Visa'][i % 2],
            'intake_location': 'Sydney FO',
            'urgent': False
        }
        orchestrator.assign_case_to_best_agent(test_case)
    
    summary = orchestrator.get_workload_summary()
    
    print("Workload Summary:")
    print(f"  Total Agents: {summary['total_agents']}")
    print(f"  Human Agents: {summary['human_agents']}")
    print(f"  AI Agents: {summary['ai_agents']}")
    print(f"  Available Agents: {summary['available_agents']}")
    print(f"  Total Capacity: {summary['total_capacity']}")
    print(f"  Total Workload: {summary['total_workload']}")
    print(f"  Overall Utilization: {summary['overall_utilization']}")
    
    print("\nAgent Details:")
    for agent_info in summary['agents']:
        print(f"  {agent_info['name']}")
        print(f"    Type: {agent_info['agent_type']}")
        print(f"    Workload: {agent_info['current_workload']}/{agent_info['max_capacity']}")
        print(f"    Capacity: {agent_info['capacity_ratio']}")
    
    print()


def test_urgent_prioritization():
    """Test urgent case prioritization"""
    print("=" * 60)
    print("TEST 9: Urgent Case Prioritization")
    print("=" * 60)
    
    orchestrator = get_orchestrator()
    orchestrator.reset_workloads()
    
    # Mix of urgent and non-urgent cases
    test_cases = [
        {'application_number': 'NORMAL-001', 'case_type': 'Work Visa', 
         'intake_location': 'Sydney FO', 'urgent': False, 'days_in_process': 10},
        {'application_number': 'URGENT-001', 'case_type': 'Work Visa', 
         'intake_location': 'Sydney FO', 'urgent': True, 'days_in_process': 5},
        {'application_number': 'NORMAL-002', 'case_type': 'Student Visa', 
         'intake_location': 'Melbourne FO', 'urgent': False, 'days_in_process': 8},
        {'application_number': 'URGENT-002', 'case_type': 'Student Visa', 
         'intake_location': 'Melbourne FO', 'urgent': True, 'days_in_process': 3},
    ]
    
    print("Cases to assign:")
    for case in test_cases:
        urgent_flag = "🔴 URGENT" if case['urgent'] else "NORMAL  "
        print(f"  {urgent_flag} - {case['application_number']}")
    
    print("\nAssigning with prioritization...")
    assignments = orchestrator.assign_cases_batch(test_cases, prioritize_urgent=True)
    
    print("\nAssignment order (urgent cases should be first):")
    for agent_id, data in assignments.items():
        if agent_id == 'unassigned':
            continue
        
        agent = data['agent']
        print(f"\n{agent.name} ({agent.agent_type.value}):")
        for case_data in data['cases']:
            case = case_data['case']
            urgent_flag = "🔴" if case['urgent'] else "  "
            print(f"  {urgent_flag} {case['application_number']}")
    
    print()


def run_all_tests():
    """Run all test cases"""
    print("\n" + "=" * 60)
    print("CASE ASSIGNMENT ORCHESTRATION - TEST SUITE")
    print("=" * 60 + "\n")
    
    tests = [
        test_agent_creation,
        test_expertise_scoring,
        test_workload_tracking,
        test_assignment_scoring,
        test_single_assignment,
        test_batch_assignment,
        test_recommendations,
        test_workload_summary,
        test_urgent_prioritization
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"✓ {test_func.__name__} PASSED\n")
        except Exception as e:
            failed += 1
            print(f"✗ {test_func.__name__} FAILED: {str(e)}\n")
    
    print("=" * 60)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
