"""Case Assignment Orchestration Service

This module provides intelligent case assignment orchestration for distributing
active visa applications to case workers (human agents and AI agents).

The orchestration system considers:
- Agent expertise with specific application types and locations
- Workload balancing between agents
- Agent processing capacity (different agents can handle different volumes)
- Human agents vs AI agents (human agents verify AI agent work)
- Urgent cases prioritization
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from enum import Enum


class AgentType(Enum):
    """Agent type classification"""
    HUMAN = "human"
    AI = "ai"


class ExpertiseLevel(Enum):
    """Expertise level for specific case types or locations"""
    EXPERT = 3      # Can handle complex cases efficiently
    PROFICIENT = 2  # Can handle most cases competently
    BASIC = 1       # Can handle simple cases


class CaseWorkerAgent:
    """Represents a case worker agent (human or AI)"""
    
    def __init__(
        self, 
        agent_id: str,
        name: str,
        agent_type: AgentType,
        max_capacity: int,
        case_type_expertise: Dict[str, ExpertiseLevel] = None,
        location_expertise: Dict[str, ExpertiseLevel] = None,
        current_workload: int = 0,
        is_available: bool = True
    ):
        self.agent_id = agent_id
        self.name = name
        self.agent_type = agent_type
        self.max_capacity = max_capacity
        self.case_type_expertise = case_type_expertise or {}
        self.location_expertise = location_expertise or {}
        self.current_workload = current_workload
        self.is_available = is_available
        self.assigned_cases = []
        
    def get_expertise_score(self, case_type: str, location: str) -> float:
        """Calculate expertise score for a specific case"""
        case_score = self.case_type_expertise.get(case_type, ExpertiseLevel.BASIC).value
        location_score = self.location_expertise.get(location, ExpertiseLevel.BASIC).value
        
        # Combined score (weighted average)
        return (case_score * 0.6 + location_score * 0.4)
    
    def get_capacity_ratio(self) -> float:
        """Get current capacity utilization (0.0 to 1.0)"""
        if self.max_capacity == 0:
            return 1.0
        return self.current_workload / self.max_capacity
    
    def can_accept_case(self) -> bool:
        """Check if agent can accept more cases"""
        return self.is_available and self.current_workload < self.max_capacity
    
    def assign_case(self, case: Dict):
        """Assign a case to this agent"""
        if not self.can_accept_case():
            raise ValueError(f"Agent {self.name} is at capacity or unavailable")
        
        self.current_workload += 1
        self.assigned_cases.append(case)
    
    def to_dict(self) -> Dict:
        """Convert agent to dictionary representation"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'agent_type': self.agent_type.value,
            'max_capacity': self.max_capacity,
            'current_workload': self.current_workload,
            'capacity_ratio': f"{self.get_capacity_ratio():.1%}",
            'is_available': self.is_available,
            'assigned_cases_count': len(self.assigned_cases)
        }


class CaseAssignmentOrchestrator:
    """Orchestrates intelligent case assignment to case workers"""
    
    def __init__(self):
        self.agents: List[CaseWorkerAgent] = []
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Initialize default agent pool with diverse expertise"""
        
        # Human Agents - Senior case officers
        self.agents.append(CaseWorkerAgent(
            agent_id="H001",
            name="Sarah Mitchell - Senior Case Officer",
            agent_type=AgentType.HUMAN,
            max_capacity=15,  # Human agents have lower capacity
            case_type_expertise={
                "Schengen Short Stay": ExpertiseLevel.EXPERT,
                "Work Visa": ExpertiseLevel.PROFICIENT,
                "Student Visa": ExpertiseLevel.PROFICIENT
            },
            location_expertise={
                "Sydney FO": ExpertiseLevel.EXPERT,
                "Melbourne FO": ExpertiseLevel.PROFICIENT,
                "Brisbane FO": ExpertiseLevel.BASIC
            }
        ))
        
        self.agents.append(CaseWorkerAgent(
            agent_id="H002",
            name="Michael Chen - Case Officer",
            agent_type=AgentType.HUMAN,
            max_capacity=12,
            case_type_expertise={
                "Work Visa": ExpertiseLevel.EXPERT,
                "Student Visa": ExpertiseLevel.EXPERT,
                "Schengen Short Stay": ExpertiseLevel.BASIC
            },
            location_expertise={
                "Melbourne FO": ExpertiseLevel.EXPERT,
                "Sydney FO": ExpertiseLevel.PROFICIENT,
                "Brisbane FO": ExpertiseLevel.PROFICIENT
            }
        ))
        
        self.agents.append(CaseWorkerAgent(
            agent_id="H003",
            name="Emma Rodriguez - Junior Case Officer",
            agent_type=AgentType.HUMAN,
            max_capacity=10,
            case_type_expertise={
                "Student Visa": ExpertiseLevel.PROFICIENT,
                "Schengen Short Stay": ExpertiseLevel.PROFICIENT,
                "Work Visa": ExpertiseLevel.BASIC
            },
            location_expertise={
                "Brisbane FO": ExpertiseLevel.EXPERT,
                "Sydney FO": ExpertiseLevel.BASIC,
                "Melbourne FO": ExpertiseLevel.BASIC
            }
        ))
        
        # AI Agents - Higher capacity, need human verification
        self.agents.append(CaseWorkerAgent(
            agent_id="AI001",
            name="AI Agent Alpha - Document Specialist",
            agent_type=AgentType.AI,
            max_capacity=50,  # AI can handle more cases
            case_type_expertise={
                "Schengen Short Stay": ExpertiseLevel.EXPERT,
                "Work Visa": ExpertiseLevel.EXPERT,
                "Student Visa": ExpertiseLevel.PROFICIENT
            },
            location_expertise={
                "Sydney FO": ExpertiseLevel.EXPERT,
                "Melbourne FO": ExpertiseLevel.EXPERT,
                "Brisbane FO": ExpertiseLevel.EXPERT
            }
        ))
        
        self.agents.append(CaseWorkerAgent(
            agent_id="AI002",
            name="AI Agent Beta - Biometrics Specialist",
            agent_type=AgentType.AI,
            max_capacity=45,
            case_type_expertise={
                "Work Visa": ExpertiseLevel.EXPERT,
                "Student Visa": ExpertiseLevel.EXPERT,
                "Schengen Short Stay": ExpertiseLevel.PROFICIENT
            },
            location_expertise={
                "Melbourne FO": ExpertiseLevel.EXPERT,
                "Brisbane FO": ExpertiseLevel.EXPERT,
                "Sydney FO": ExpertiseLevel.PROFICIENT
            }
        ))
        
        self.agents.append(CaseWorkerAgent(
            agent_id="AI003",
            name="AI Agent Gamma - General Processor",
            agent_type=AgentType.AI,
            max_capacity=40,
            case_type_expertise={
                "Schengen Short Stay": ExpertiseLevel.PROFICIENT,
                "Work Visa": ExpertiseLevel.PROFICIENT,
                "Student Visa": ExpertiseLevel.PROFICIENT
            },
            location_expertise={
                "Sydney FO": ExpertiseLevel.PROFICIENT,
                "Melbourne FO": ExpertiseLevel.PROFICIENT,
                "Brisbane FO": ExpertiseLevel.PROFICIENT
            }
        ))
    
    def get_agent_by_id(self, agent_id: str) -> Optional[CaseWorkerAgent]:
        """Get agent by ID"""
        for agent in self.agents:
            if agent.agent_id == agent_id:
                return agent
        return None
    
    def get_available_agents(self, agent_type: Optional[AgentType] = None) -> List[CaseWorkerAgent]:
        """Get all available agents, optionally filtered by type"""
        available = [agent for agent in self.agents if agent.can_accept_case()]
        
        if agent_type:
            available = [agent for agent in available if agent.agent_type == agent_type]
        
        return available
    
    def calculate_assignment_score(
        self, 
        agent: CaseWorkerAgent, 
        case: Dict,
        urgency_multiplier: float = 1.0
    ) -> float:
        """
        Calculate assignment score for an agent-case pair
        Higher score = better match
        
        Factors:
        - Expertise match (40%)
        - Capacity availability (30%)
        - Agent type (20% - prefer AI for routine, human for complex)
        - Urgency handling (10%)
        """
        # Expertise score (0-3 normalized to 0-1)
        expertise_score = agent.get_expertise_score(
            case.get('case_type', ''),
            case.get('intake_location', '')
        ) / 3.0
        
        # Capacity score (inverted ratio - lower workload = higher score)
        capacity_score = 1.0 - agent.get_capacity_ratio()
        
        # Agent type score
        is_urgent = case.get('urgent', False)
        if is_urgent:
            # Prefer human agents for urgent cases
            agent_type_score = 0.8 if agent.agent_type == AgentType.HUMAN else 0.4
        else:
            # AI agents are good for routine cases
            agent_type_score = 0.7 if agent.agent_type == AgentType.AI else 0.9
        
        # Urgency handling score
        urgency_score = urgency_multiplier if is_urgent else 1.0
        
        # Weighted combination
        total_score = (
            expertise_score * 0.40 +
            capacity_score * 0.30 +
            agent_type_score * 0.20 +
            urgency_score * 0.10
        )
        
        return total_score
    
    def assign_case_to_best_agent(
        self, 
        case: Dict,
        prefer_agent_type: Optional[AgentType] = None
    ) -> Tuple[Optional[CaseWorkerAgent], float]:
        """
        Assign a case to the best available agent
        
        Returns: (assigned_agent, assignment_score)
        """
        available_agents = self.get_available_agents(prefer_agent_type)
        
        if not available_agents:
            return None, 0.0
        
        # Calculate scores for all available agents
        agent_scores = [
            (agent, self.calculate_assignment_score(agent, case))
            for agent in available_agents
        ]
        
        # Sort by score (descending)
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Assign to best agent
        best_agent, best_score = agent_scores[0]
        best_agent.assign_case(case)
        
        return best_agent, best_score
    
    def assign_cases_batch(
        self, 
        cases: List[Dict],
        prioritize_urgent: bool = True
    ) -> Dict[str, List[Dict]]:
        """
        Assign multiple cases in batch
        
        Returns: Dictionary mapping agent_id to list of assigned cases
        """
        # Sort cases by urgency if prioritization is enabled
        if prioritize_urgent:
            cases = sorted(cases, key=lambda c: c.get('urgent', False), reverse=True)
        
        assignments = {}
        unassigned_cases = []
        
        for case in cases:
            agent, score = self.assign_case_to_best_agent(case)
            
            if agent:
                if agent.agent_id not in assignments:
                    assignments[agent.agent_id] = {
                        'agent': agent,
                        'cases': []
                    }
                assignments[agent.agent_id]['cases'].append({
                    'case': case,
                    'score': score
                })
            else:
                unassigned_cases.append(case)
        
        # Add unassigned cases info
        if unassigned_cases:
            assignments['unassigned'] = {
                'agent': None,
                'cases': [{'case': c, 'score': 0.0} for c in unassigned_cases]
            }
        
        return assignments
    
    def get_workload_summary(self) -> Dict:
        """Get summary of current workload across all agents"""
        summary = {
            'total_agents': len(self.agents),
            'human_agents': len([a for a in self.agents if a.agent_type == AgentType.HUMAN]),
            'ai_agents': len([a for a in self.agents if a.agent_type == AgentType.AI]),
            'available_agents': len(self.get_available_agents()),
            'total_capacity': sum(a.max_capacity for a in self.agents),
            'total_workload': sum(a.current_workload for a in self.agents),
            'agents': [agent.to_dict() for agent in self.agents]
        }
        
        # Calculate overall utilization
        if summary['total_capacity'] > 0:
            summary['overall_utilization'] = f"{(summary['total_workload'] / summary['total_capacity']):.1%}"
        else:
            summary['overall_utilization'] = "N/A"
        
        return summary
    
    def reset_workloads(self):
        """Reset all agent workloads (for testing/simulation)"""
        for agent in self.agents:
            agent.current_workload = 0
            agent.assigned_cases = []
    
    def recommend_assignment(self, case: Dict) -> List[Dict]:
        """
        Get top 3 agent recommendations for a case without actually assigning
        
        Returns: List of {agent, score, reasoning} dictionaries
        """
        available_agents = self.get_available_agents()
        
        if not available_agents:
            return []
        
        recommendations = []
        for agent in available_agents:
            score = self.calculate_assignment_score(agent, case)
            
            # Generate reasoning
            expertise = agent.get_expertise_score(
                case.get('case_type', ''),
                case.get('intake_location', '')
            )
            capacity_ratio = agent.get_capacity_ratio()
            
            reasoning = []
            if expertise >= 2.5:
                reasoning.append("High expertise match")
            elif expertise >= 1.5:
                reasoning.append("Good expertise match")
            else:
                reasoning.append("Basic expertise")
            
            if capacity_ratio < 0.3:
                reasoning.append("Low workload")
            elif capacity_ratio < 0.7:
                reasoning.append("Moderate workload")
            else:
                reasoning.append("High workload")
            
            if agent.agent_type == AgentType.HUMAN:
                reasoning.append("Human verification available")
            else:
                reasoning.append("AI processing - faster turnaround")
            
            recommendations.append({
                'agent': agent,
                'score': score,
                'reasoning': reasoning
            })
        
        # Sort by score and return top 3
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:3]


# Global orchestrator instance
_orchestrator_instance = None


def get_orchestrator() -> CaseAssignmentOrchestrator:
    """Get or create global orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = CaseAssignmentOrchestrator()
    return _orchestrator_instance
