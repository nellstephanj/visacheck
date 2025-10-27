# Case Assignment Orchestration - Quick Start Guide

## What is Case Assignment Orchestration?

The Case Assignment Orchestration Agent is an intelligent system that automatically assigns visa application cases to case workers based on their expertise, current workload, and case complexity. It supports both **Human Agents** (case officers) and **AI Agents** (automated processors).

## Key Benefits

✅ **Intelligent Matching** - Cases are automatically matched to agents with the right expertise  
✅ **Workload Balancing** - Prevents agent overload by distributing cases evenly  
✅ **Urgent Prioritization** - Urgent cases are automatically prioritized  
✅ **Mixed Workforce** - AI agents handle high volume, human agents provide oversight  
✅ **Transparent Scoring** - See exactly why cases are assigned to specific agents

## Quick Start (5 Minutes)

### Step 1: Access the Page
1. Log into VisaCheck
2. Click **"🎯 Case Assignment"** in the sidebar
3. You'll see the Case Assignment Orchestration dashboard

### Step 2: View Current Workload
The **📊 Dashboard** tab shows:
- Total agents available
- Current workload distribution
- Agent capacity status
- Human vs. AI agent breakdown

### Step 3: Assign Cases

#### Option A: Batch Assignment (Recommended)
1. Go to **📋 Assign Cases** tab
2. Choose number of cases to load (5-100)
3. Click **🔄 Load Pending Cases**
4. Enable **"Prioritize Urgent Cases"** (recommended)
5. Click **🎯 Assign All Cases**
6. Review assignment results

#### Option B: Single Case Recommendation
1. Go to **🔍 Recommendations** tab
2. Enter case details:
   - Application number
   - Case type (Schengen/Work/Student visa)
   - Intake location (Sydney/Melbourne/Brisbane)
   - Urgent status
3. Click **Get Recommendations**
4. View top 3 agent matches with reasoning

## Understanding the Agents

### 👤 Human Agents (Case Officers)
- **Lower capacity** (10-15 cases)
- **Manual review** for complex cases
- **Verification role** for AI work
- **Expertise-based** assignments

**Current Human Agents:**
- Sarah Mitchell - Senior Case Officer (Schengen expert)
- Michael Chen - Case Officer (Work/Student visa expert)
- Emma Rodriguez - Junior Case Officer (Brisbane specialist)

### 🤖 AI Agents
- **Higher capacity** (40-50 cases)
- **Fast processing** for routine cases
- **24/7 availability**
- **Requires human verification**

**Current AI Agents:**
- AI Agent Alpha - Document Specialist
- AI Agent Beta - Biometrics Specialist  
- AI Agent Gamma - General Processor

## How Assignment Works

The system scores each agent for a case based on:

1. **Expertise (40%)** - Experience with case type and location
2. **Capacity (30%)** - Current workload availability
3. **Agent Type (20%)** - Human vs. AI suitability
4. **Urgency (10%)** - Priority for urgent cases

**Example:**
```
Case: Urgent Schengen visa from Sydney FO

Best Match: Sarah Mitchell (86.1% score)
Why?
✓ Expert in Schengen visas (⭐⭐⭐)
✓ Expert in Sydney FO (⭐⭐⭐)
✓ Only 5/15 cases (33% capacity)
✓ Human agent ideal for urgent case
```

## Common Workflows

### Workflow 1: Daily Case Assignment
**Use Case**: Assign new cases each morning

1. Open **📋 Assign Cases** tab
2. Load 25 pending cases
3. Enable urgent prioritization
4. Review the list of cases
5. Click **🎯 Assign All Cases**
6. Check assignment results
7. Monitor unassigned cases (if any)

**Time Required**: ~2 minutes

### Workflow 2: Urgent Case Handling
**Use Case**: Immediately assign an urgent case

1. Open **🔍 Recommendations** tab
2. Enter urgent case details
3. Mark as **"Urgent Case"**
4. Get recommendations
5. System prioritizes human agents
6. Review top recommendation
7. Manually assign if needed

**Time Required**: ~1 minute

### Workflow 3: Workload Monitoring
**Use Case**: Check agent utilization weekly

1. Open **📊 Dashboard** tab
2. Review "Overall Utilization" metric
3. Check agent status cards
4. Identify overloaded agents (>80% capacity)
5. Review **👥 Agent Pool** tab for details
6. Consider redistributing if needed

**Time Required**: ~3 minutes

### Workflow 4: Review Agent Expertise
**Use Case**: Understand agent capabilities

1. Open **👥 Agent Pool** tab
2. Filter by "Human" or "AI"
3. Expand agent profiles
4. Review expertise ratings (⭐⭐⭐)
5. Check assigned cases
6. Identify gaps or training needs

**Time Required**: ~5 minutes

## Reading the Dashboard

### Capacity Status Colors

🟢 **Green** (0-50%): Agent has plenty of capacity  
🟠 **Orange** (50-80%): Agent is moderately busy  
🔴 **Red** (80-100%): Agent is near capacity

### Agent Cards

```
┌─────────────────────────────────────┐
│ 👤 Sarah Mitchell - Senior Officer │ ← Icon + Name
├─────────────────────────────────────┤
│ ID: H001 | Type: HUMAN             │ ← Identifier
│ Workload: 5 / 15                   │ ← Current/Max
│ [████████░░░░░░░░░░] 33%           │ ← Visual bar
│ Capacity: 33.3%                    │ ← Utilization
└─────────────────────────────────────┘
```

### Assignment Results

After batch assignment, you'll see:

**Metrics:**
- Total Assigned: 23
- Unassigned: 2
- Success Rate: 92.0%

**Per-Agent Breakdown:**
Each agent shows:
- Number of cases assigned
- List of application numbers
- Assignment scores (0.0-1.0)

## Best Practices

### ✅ DO

- **Run batch assignments daily** to stay on top of new cases
- **Prioritize urgent cases** using the checkbox
- **Monitor capacity** to prevent agent overload
- **Review recommendations** before manual assignments
- **Check unassigned queue** regularly
- **Balance human and AI workloads**

### ❌ DON'T

- Ignore the unassigned cases queue
- Manually override without checking recommendations
- Let agents reach 100% capacity consistently
- Assign urgent cases to overloaded agents
- Ignore agent expertise levels
- Forget that AI agents need human verification

## Troubleshooting

### Problem: "No available agents found"
**Cause**: All agents are at capacity  
**Solution**: 
- Check agent workloads in Dashboard
- Increase capacity limits (admin)
- Add more agents to pool (admin)
- Process existing cases first

### Problem: "Many unassigned cases"
**Cause**: High volume or insufficient capacity  
**Solution**:
- Check assignment success rate
- Review agent capacity utilization
- Consider adding more agents
- Prioritize and assign manually

### Problem: "Poor agent match scores"
**Cause**: Limited expertise match  
**Solution**:
- Review case details for accuracy
- Check agent expertise profiles
- Use recommendations tab to understand scoring
- Consider agent training needs

## Tips & Tricks

💡 **Tip 1**: Use the recommendations tab to "preview" assignments before running a batch

💡 **Tip 2**: Check the reasoning section to understand why agents were recommended

💡 **Tip 3**: Sort cases by urgency and days in process before assigning

💡 **Tip 4**: Monitor the overall utilization metric - aim for 60-80% for optimal balance

💡 **Tip 5**: Human agents should verify AI agent work - check assignment distribution

## Integration with Other Pages

### 📊 Active Applications → 🎯 Case Assignment
Load cases from Active Applications into the assignment system for batch processing

### 🎯 Case Assignment → 🤖 Sexy Visa Agent  
Assigned cases flow to the Sexy Visa Agent workflow for processing

### 📋 Visa Intake → 📊 Active Applications → 🎯 Case Assignment
Complete pipeline from intake to assignment

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Navigate to Dashboard | Tab 1 |
| Navigate to Agent Pool | Tab 2 |
| Navigate to Assign Cases | Tab 3 |
| Navigate to Recommendations | Tab 4 |

## Getting Help

### In-App Help
- Each tab has contextual information
- Hover over metrics for tooltips
- Expand agent profiles for details
- Click "📚 Documentation" for full guide

### Support Contacts
- **Email**: support@visacheck.com
- **Documentation**: See CASE_ASSIGNMENT_README.md
- **Training**: Contact your supervisor

## Example Scenarios

### Scenario 1: Monday Morning Rush
**Situation**: 50 new cases over the weekend

**Action Plan:**
1. Open Case Assignment
2. Load 50 pending cases
3. Enable urgent prioritization
4. Review case list for critical items
5. Assign all cases
6. Check for unassigned (should be few)
7. Manually assign remaining

**Expected Result**: All cases assigned within 5 minutes

### Scenario 2: VIP Urgent Case
**Situation**: Embassy flagged case needs immediate attention

**Action Plan:**
1. Go to Recommendations tab
2. Enter case details, mark urgent
3. Review top recommendation (likely human agent)
4. Verify agent has capacity
5. Manually assign to recommended agent
6. Notify agent directly

**Expected Result**: Case assigned to best available expert

### Scenario 3: End of Week Review
**Situation**: Friday afternoon capacity check

**Action Plan:**
1. Review Dashboard overall utilization
2. Check Agent Pool for overloaded agents
3. Note agents with low utilization
4. Plan next week's capacity
5. Consider agent training needs
6. Review unassigned queue

**Expected Result**: Clear understanding of team capacity

## Next Steps

After mastering basic assignment:

1. **Explore Advanced Features**
   - Custom scoring adjustments
   - Agent expertise updates
   - Capacity planning tools

2. **Integrate with Workflow**
   - Track cases through processing
   - Monitor completion rates
   - Analyze performance data

3. **Optimize Operations**
   - Review assignment patterns
   - Identify bottlenecks
   - Improve team efficiency

---

**Ready to get started?** Open the Case Assignment page and try assigning your first batch of cases!

**Questions?** Check the full documentation in CASE_ASSIGNMENT_README.md
