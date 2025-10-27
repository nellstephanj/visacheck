# Case Assignment Orchestration System

## Overview

The **Case Assignment Orchestration Agent** is an intelligent system designed to automatically assign active visa applications to case workers (both human agents and AI agents) based on multiple factors including expertise, workload, capacity, and urgency.

## Key Features

### 1. **Intelligent Agent Matching**
The orchestrator evaluates each case against available agents using a sophisticated scoring algorithm that considers:
- **Expertise Match (40%)**: Agent's experience with specific case types and intake locations
- **Capacity Availability (30%)**: Current workload vs. maximum capacity
- **Agent Type (20%)**: Human vs. AI agent suitability for the case
- **Urgency Handling (10%)**: Priority given to urgent cases

### 2. **Agent Types**

#### Human Agents
- **Lower capacity** (10-15 cases typical)
- **Higher expertise** for complex cases
- **Verification role** for AI agent work
- **Manual review** capabilities

#### AI Agents
- **Higher capacity** (40-50 cases typical)
- **Faster processing** for routine cases
- **24/7 availability**
- **Requires human verification** for final decisions

### 3. **Expertise Levels**

Each agent has expertise ratings in two dimensions:

**Case Type Expertise:**
- ⭐⭐⭐ **Expert** (Level 3): Can handle complex cases efficiently
- ⭐⭐ **Proficient** (Level 2): Can handle most cases competently
- ⭐ **Basic** (Level 1): Can handle simple cases

**Location Expertise:**
- ⭐⭐⭐ **Expert** (Level 3): Deep knowledge of location-specific requirements
- ⭐⭐ **Proficient** (Level 2): Good understanding of location processes
- ⭐ **Basic** (Level 1): Basic familiarity with location

### 4. **Workload Balancing**

The system automatically balances workload across agents:
- Prevents agent overload by respecting capacity limits
- Distributes cases evenly when expertise levels are similar
- Prioritizes agents with lower utilization rates
- Tracks real-time workload and available capacity

### 5. **Urgent Case Handling**

Urgent cases receive special treatment:
- Automatically prioritized in batch assignments
- Preferentially assigned to human agents for faster decision-making
- Higher weight in assignment scoring algorithm
- Visual indicators (🔴) throughout the system

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Case Assignment Orchestration System           │
└─────────────────────────────────────────────────────────────┘
                             │
                             ├─── Agent Pool Management
                             │    • Human Agents (3 default)
                             │    • AI Agents (3 default)
                             │    • Capacity tracking
                             │    • Expertise profiles
                             │
                             ├─── Scoring Algorithm
                             │    • Expertise scoring
                             │    • Capacity calculation
                             │    • Agent type matching
                             │    • Urgency weighting
                             │
                             ├─── Assignment Engine
                             │    • Single case assignment
                             │    • Batch assignment
                             │    • Recommendation generation
                             │    • Conflict resolution
                             │
                             └─── Reporting & Analytics
                                  • Workload dashboard
                                  • Agent utilization
                                  • Assignment history
                                  • Performance metrics
```

## Default Agent Pool

### Human Agents

#### 1. Sarah Mitchell - Senior Case Officer (H001)
- **Type**: Human
- **Capacity**: 15 cases
- **Expertise**:
  - ⭐⭐⭐ Schengen Short Stay
  - ⭐⭐ Work Visa
  - ⭐⭐ Student Visa
- **Location Strength**: Sydney FO (Expert), Melbourne FO (Proficient)

#### 2. Michael Chen - Case Officer (H002)
- **Type**: Human
- **Capacity**: 12 cases
- **Expertise**:
  - ⭐⭐⭐ Work Visa
  - ⭐⭐⭐ Student Visa
  - ⭐ Schengen Short Stay
- **Location Strength**: Melbourne FO (Expert), Sydney FO (Proficient)

#### 3. Emma Rodriguez - Junior Case Officer (H003)
- **Type**: Human
- **Capacity**: 10 cases
- **Expertise**:
  - ⭐⭐ Student Visa
  - ⭐⭐ Schengen Short Stay
  - ⭐ Work Visa
- **Location Strength**: Brisbane FO (Expert)

### AI Agents

#### 1. AI Agent Alpha - Document Specialist (AI001)
- **Type**: AI
- **Capacity**: 50 cases
- **Expertise**:
  - ⭐⭐⭐ Schengen Short Stay
  - ⭐⭐⭐ Work Visa
  - ⭐⭐ Student Visa
- **Location Strength**: All locations (Expert)

#### 2. AI Agent Beta - Biometrics Specialist (AI002)
- **Type**: AI
- **Capacity**: 45 cases
- **Expertise**:
  - ⭐⭐⭐ Work Visa
  - ⭐⭐⭐ Student Visa
  - ⭐⭐ Schengen Short Stay
- **Location Strength**: Melbourne, Brisbane (Expert)

#### 3. AI Agent Gamma - General Processor (AI003)
- **Type**: AI
- **Capacity**: 40 cases
- **Expertise**:
  - ⭐⭐ All case types (Proficient)
- **Location Strength**: All locations (Proficient)

## User Interface

The Case Assignment page provides four main tabs:

### 📊 Dashboard Tab
- **Overview metrics**: Total agents, available capacity, current workload
- **Agent status cards**: Visual representation of each agent
- **Capacity visualization**: Color-coded progress bars
- **Split view**: Human agents vs. AI agents

### 👥 Agent Pool Tab
- **Detailed agent profiles**: Complete information for each agent
- **Filter options**: View by agent type (All/Human/AI)
- **Expertise breakdown**: Visual display of capabilities
- **Current assignments**: See what cases each agent is handling

### 📋 Assign Cases Tab
- **Load pending cases**: Import cases from the system
- **Batch assignment**: Assign multiple cases at once
- **Prioritization options**: Toggle urgent case priority
- **Assignment results**: Detailed breakdown of assignments
- **Success metrics**: Track assignment success rate
- **Unassigned handling**: Identify cases that couldn't be assigned

### 🔍 Recommendations Tab
- **Manual case input**: Enter specific case details
- **Top 3 recommendations**: Get best agent matches
- **Detailed reasoning**: Understand why agents were recommended
- **Score breakdown**: See expertise, capacity, and other factors
- **Best match highlight**: Clearly marked optimal assignment

## Scoring Algorithm Details

### Assignment Score Calculation

```python
total_score = (
    expertise_score * 0.40 +      # 40% weight
    capacity_score * 0.30 +       # 30% weight
    agent_type_score * 0.20 +     # 20% weight
    urgency_score * 0.10          # 10% weight
)
```

#### 1. Expertise Score (0-1)
```python
expertise_score = (
    case_type_expertise * 0.6 +
    location_expertise * 0.4
) / 3.0  # Normalize to 0-1
```

#### 2. Capacity Score (0-1)
```python
capacity_score = 1.0 - (current_workload / max_capacity)
```

#### 3. Agent Type Score (0-1)
- **Urgent cases**: Human agents preferred (0.8 vs 0.4)
- **Routine cases**: AI agents efficient (0.7 vs 0.9)

#### 4. Urgency Score
- Applied as multiplier when case is urgent
- Default value: 1.0

### Example Calculation

**Case**: Schengen Short Stay, Sydney FO, Urgent

**Agent**: Sarah Mitchell (H001)
- Case Type Expertise: 3 (Expert) → 3/3 = 1.0
- Location Expertise: 3 (Expert) → 3/3 = 1.0
- Combined Expertise: (1.0 * 0.6) + (1.0 * 0.4) = 1.0
- Current Workload: 5/15 = 0.33
- Capacity Score: 1.0 - 0.33 = 0.67
- Agent Type Score: 0.8 (human, urgent)
- Urgency Score: 1.0

**Final Score**:
```
(1.0 * 0.40) + (0.67 * 0.30) + (0.8 * 0.20) + (1.0 * 0.10)
= 0.40 + 0.201 + 0.16 + 0.10
= 0.861 (86.1%)
```

## API Reference

### Main Service Class: `CaseAssignmentOrchestrator`

#### Methods

##### `get_orchestrator()`
```python
orchestrator = get_orchestrator()
```
Returns the global singleton orchestrator instance.

##### `assign_case_to_best_agent(case, prefer_agent_type=None)`
```python
agent, score = orchestrator.assign_case_to_best_agent(
    case={
        'application_number': 'APP-001',
        'case_type': 'Work Visa',
        'intake_location': 'Sydney FO',
        'urgent': True
    }
)
```
Assigns a single case to the best available agent.

##### `assign_cases_batch(cases, prioritize_urgent=True)`
```python
assignments = orchestrator.assign_cases_batch(
    cases=[case1, case2, case3],
    prioritize_urgent=True
)
```
Assigns multiple cases in a batch operation.

##### `recommend_assignment(case)`
```python
recommendations = orchestrator.recommend_assignment(case)
# Returns top 3 agent recommendations with scores and reasoning
```
Gets recommendations without actually assigning the case.

##### `get_workload_summary()`
```python
summary = orchestrator.get_workload_summary()
# Returns complete workload statistics
```
Gets current workload overview for all agents.

##### `reset_workloads()`
```python
orchestrator.reset_workloads()
```
Resets all agent workloads (useful for testing/simulation).

## Integration with Existing System

The Case Assignment Orchestration integrates seamlessly with:

### 1. Active Applications Page
- View all pending cases
- Click "Use agent" to trigger workflow
- Cases can be bulk-imported to assignment system

### 2. Workflow Page (Sexy Visa Agent)
- Assigned agents can process cases through the workflow
- Human agents verify AI agent work
- Complete case review pipeline

### 3. Visa Intake
- New applications automatically enter the pending queue
- Ready for assignment through orchestration system

## Best Practices

### For Case Managers

1. **Regular Monitoring**
   - Check dashboard daily for capacity utilization
   - Ensure no agents are consistently at 100% capacity
   - Monitor unassigned cases queue

2. **Batch Assignment**
   - Process assignments in batches for efficiency
   - Prioritize urgent cases in batch operations
   - Review assignment results before finalizing

3. **Agent Expertise**
   - Match complex cases to expert agents
   - Use recommendations tab for difficult assignments
   - Consider location expertise for regional specifics

4. **Workload Balance**
   - Distribute cases evenly across available agents
   - Don't overload high-performing agents
   - Monitor AI vs. human agent distribution

### For System Administrators

1. **Agent Configuration**
   - Adjust capacity limits based on performance data
   - Update expertise profiles as agents gain experience
   - Add new agents to the pool as needed

2. **Performance Tuning**
   - Monitor assignment success rates
   - Adjust scoring algorithm weights if needed
   - Track processing times by agent type

3. **Human Verification**
   - Ensure human agents review AI decisions
   - Maintain appropriate human-to-AI agent ratios
   - Track verification outcomes

## Future Enhancements

### Planned Features

1. **Machine Learning Integration**
   - Learn optimal assignments from historical data
   - Predict case complexity automatically
   - Adaptive expertise scoring

2. **Real-time Monitoring**
   - Live agent status updates
   - Automatic workload rebalancing
   - Performance dashboards

3. **Advanced Analytics**
   - Processing time trends
   - Agent performance metrics
   - Case outcome correlation

4. **Integration Expansion**
   - Direct assignment from Active Applications page
   - Workflow automation triggers
   - Email notifications for assignments

5. **Customization**
   - Configure scoring algorithm weights
   - Define custom agent roles
   - Create specialized agent teams

## Troubleshooting

### Common Issues

#### No Available Agents
**Symptom**: Cases end up in "unassigned" queue
**Solution**: 
- Check agent capacity limits
- Increase max_capacity for existing agents
- Add more agents to the pool
- Reset workloads if in testing mode

#### Poor Assignment Quality
**Symptom**: Cases assigned to suboptimal agents
**Solution**:
- Review agent expertise profiles
- Verify case metadata is complete
- Check scoring algorithm weights
- Use recommendations tab to validate logic

#### Workload Imbalance
**Symptom**: Some agents always at capacity, others underutilized
**Solution**:
- Adjust capacity limits
- Review expertise configurations
- Consider agent availability settings
- Monitor batch assignment patterns

## Technical Details

### Dependencies
- Python 3.8+
- Streamlit
- Standard library (json, os, datetime, enum, typing)

### File Structure
```
visacheck/
└── src/
    ├── services/
    │   └── case_assignment_service.py    # Core orchestration logic
    ├── pages/
    │   └── case_assignment.py            # UI page
    └── main.py                           # Navigation integration
```

### Data Models

#### CaseWorkerAgent
```python
{
    'agent_id': str,
    'name': str,
    'agent_type': AgentType (HUMAN|AI),
    'max_capacity': int,
    'current_workload': int,
    'case_type_expertise': Dict[str, ExpertiseLevel],
    'location_expertise': Dict[str, ExpertiseLevel],
    'is_available': bool
}
```

#### Case
```python
{
    'application_number': str,
    'case_type': str,
    'intake_location': str,
    'urgent': bool,
    'days_in_process': int,
    'nationality': str,
    'submission_date': str
}
```

## Support

For questions or issues with the Case Assignment Orchestration system:

- 📧 Email: support@visacheck.com
- 📚 Documentation: [Internal Wiki Link]
- 🐛 Bug Reports: [Issue Tracker Link]

---

**Version**: 1.0.0  
**Last Updated**: October 27, 2025  
**Author**: VisaCheck Development Team
