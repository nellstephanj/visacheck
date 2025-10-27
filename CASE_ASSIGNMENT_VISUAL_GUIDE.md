# Case Assignment Orchestration - Visual Guide

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────┐
│                          VISA APPLICATION SYSTEM                           │
└────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ↓
┌────────────────────────────────────────────────────────────────────────────┐
│                          📋 VISA INTAKE FORM                               │
│  • New applications entered by staff                                       │
│  • Validates and stores application data                                   │
└────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ↓
┌────────────────────────────────────────────────────────────────────────────┐
│                      📊 ACTIVE APPLICATIONS PAGE                           │
│  • Displays all pending applications                                       │
│  • Shows submission date, urgency, days in process                         │
│  • Paginated view (25 per page)                                            │
└────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ↓
┌────────────────────────────────────────────────────────────────────────────┐
│                    🎯 CASE ASSIGNMENT ORCHESTRATION                        │
│                              *** NEW ***                                   │
│                                                                            │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │                        ORCHESTRATION ENGINE                          │ │
│  │                                                                      │ │
│  │  Input: Pending cases from Active Applications                      │ │
│  │                                                                      │ │
│  │  Process:                                                            │ │
│  │  1. Load case details (type, location, urgency, etc.)              │ │
│  │  2. Evaluate all available agents                                   │ │
│  │  3. Calculate assignment scores                                     │ │
│  │  4. Assign to best matching agent                                   │ │
│  │  5. Track workload and capacity                                     │ │
│  │                                                                      │ │
│  │  Output: Assigned cases ready for processing                        │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  ┌────────────────────────┐  ┌───────────────────────────────────────┐   │
│  │   AGENT POOL           │  │   SCORING ALGORITHM                   │   │
│  │                        │  │                                       │   │
│  │  👤 Human Agents (3)   │  │  Score = Σ Weighted Factors:         │   │
│  │  • Sarah Mitchell      │  │                                       │   │
│  │  • Michael Chen        │  │  • Expertise (40%)                    │   │
│  │  • Emma Rodriguez      │  │    - Case type match                  │   │
│  │                        │  │    - Location experience              │   │
│  │  🤖 AI Agents (3)      │  │                                       │   │
│  │  • Alpha (Docs)        │  │  • Capacity (30%)                     │   │
│  │  • Beta (Bio)          │  │    - Current workload                 │   │
│  │  • Gamma (General)     │  │    - Max capacity                     │   │
│  │                        │  │                                       │   │
│  │  Capacity: 172 total   │  │  • Agent Type (20%)                   │   │
│  │  Current: Variable     │  │    - Human vs AI fit                  │   │
│  │                        │  │                                       │   │
│  │                        │  │  • Urgency (10%)                      │   │
│  │                        │  │    - Priority handling                │   │
│  └────────────────────────┘  └───────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
        ┌───────────────────┐  ┌──────────────┐  ┌──────────────┐
        │  👤 Human Agent    │  │  🤖 AI Agent │  │  🤖 AI Agent │
        │  (Low Volume)      │  │ (High Volume)│  │ (High Volume)│
        │  • Expert Review   │  │ • Fast Proc. │  │ • Fast Proc. │
        │  • Complex Cases   │  │ • Routine    │  │ • Routine    │
        │  • Final Verify    │  │ • Needs ✓    │  │ • Needs ✓    │
        └───────────────────┘  └──────────────┘  └──────────────┘
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ↓
┌────────────────────────────────────────────────────────────────────────────┐
│                      🤖 SEXY VISA AGENT WORKFLOW                           │
│  • Document Verification Agent                                             │
│  • Biometrics Verification Agent                                           │
│  • EU-VIS Matching Agent                                                   │
│  • Final Review Agent                                                      │
└────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ↓
┌────────────────────────────────────────────────────────────────────────────┐
│                           ✅ CASE DECISION                                 │
│  • Approved / Refused / Additional Info Required                           │
│  • Human verification of AI work complete                                  │
└────────────────────────────────────────────────────────────────────────────┘
```

## User Interface Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🎯 Case Assignment Orchestration                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [📊 Dashboard] [👥 Agent Pool] [📋 Assign Cases] [🔍 Recommendations]    │
│  ───────────────────────────────────────────────────────────────────────    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        📊 DASHBOARD TAB                             │   │
│  │                                                                     │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────┐  │   │
│  │  │ Total Agents │ │  Available   │ │    Total     │ │ Current  │  │   │
│  │  │      6       │ │   Agents     │ │   Capacity   │ │ Workload │  │   │
│  │  │  👤3  🤖3    │ │      6       │ │     172      │ │    45    │  │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────┘  │   │
│  │                                                                     │   │
│  │  ┌─────────────────────┐          ┌─────────────────────┐          │   │
│  │  │ 👤 HUMAN AGENTS     │          │ 🤖 AI AGENTS        │          │   │
│  │  │                     │          │                     │          │   │
│  │  │ ┌─────────────────┐ │          │ ┌─────────────────┐ │          │   │
│  │  │ │ Sarah Mitchell  │ │          │ │ AI Alpha        │ │          │   │
│  │  │ │ ID: H001        │ │          │ │ ID: AI001       │ │          │   │
│  │  │ │ Workload: 5/15  │ │          │ │ Workload: 20/50 │ │          │   │
│  │  │ │ [████████░░░]  │ │          │ │ [████████░░░░] │ │          │   │
│  │  │ │ 33% 🟢         │ │          │ │ 40% 🟢         │ │          │   │
│  │  │ └─────────────────┘ │          │ └─────────────────┘ │          │   │
│  │  │                     │          │                     │          │   │
│  │  │ [More agents...]    │          │ [More agents...]    │          │   │
│  │  └─────────────────────┘          └─────────────────────┘          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Assignment Flow Diagram

```
┌─────────────────┐
│  Pending Cases  │
│  • URGENT-001   │ 🔴
│  • NORMAL-002   │
│  • URGENT-003   │ 🔴
│  • NORMAL-004   │
└────────┬────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Step 1: Prioritize                 │
│  • Sort by urgency                  │
│  • Urgent cases first               │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Step 2: For Each Case              │
│  ┌───────────────────────────────┐  │
│  │ Evaluate All Available Agents │  │
│  │                               │  │
│  │ For URGENT-001:               │  │
│  │ • Sarah: 96% 👤 ⭐⭐⭐        │  │
│  │ • Michael: 87% 👤 ⭐⭐        │  │
│  │ • AI Alpha: 74% 🤖 ⭐⭐⭐     │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Step 3: Assign to Best Match       │
│  URGENT-001 → Sarah Mitchell 👤     │
│  (Highest score, human for urgent)  │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Step 4: Update Workload            │
│  Sarah: 5/15 → 6/15 (40%)          │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Step 5: Repeat for All Cases       │
│  Continue until all assigned        │
└────────┬────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────┐
│  Final Result                       │
│  ┌───────────────────────────────┐  │
│  │ Assignments by Agent:         │  │
│  │                               │  │
│  │ 👤 Sarah Mitchell: 4 cases    │  │
│  │   • URGENT-001 🔴            │  │
│  │   • NORMAL-002               │  │
│  │   • NORMAL-007               │  │
│  │   • URGENT-012 🔴            │  │
│  │                               │  │
│  │ 🤖 AI Alpha: 8 cases          │  │
│  │   • NORMAL-003               │  │
│  │   • NORMAL-005               │  │
│  │   • [6 more...]              │  │
│  │                               │  │
│  │ Success Rate: 95%             │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Scoring Algorithm Visualization

```
┌──────────────────────────────────────────────────────────────────┐
│                    ASSIGNMENT SCORE CALCULATION                  │
└──────────────────────────────────────────────────────────────────┘

Example: Urgent Schengen Short Stay from Sydney FO

Agent: Sarah Mitchell (Senior Case Officer)

┌────────────────────────────────────────────────────────────────┐
│  EXPERTISE SCORE (40% weight)                                  │
│  ────────────────────────────                                  │
│  Case Type: Schengen Short Stay → ⭐⭐⭐ (Expert) = 3.0        │
│  Location: Sydney FO → ⭐⭐⭐ (Expert) = 3.0                    │
│                                                                │
│  Combined: (3.0 × 0.6) + (3.0 × 0.4) = 3.0                    │
│  Normalized: 3.0 / 3.0 = 1.0 (100%)                           │
│  Weighted: 1.0 × 0.40 = 0.40                                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  CAPACITY SCORE (30% weight)                                   │
│  ───────────────────────────                                   │
│  Current Workload: 5 cases                                     │
│  Max Capacity: 15 cases                                        │
│  Utilization: 5/15 = 33%                                       │
│                                                                │
│  Score: 1.0 - 0.33 = 0.67 (67%)                               │
│  Weighted: 0.67 × 0.30 = 0.20                                 │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  AGENT TYPE SCORE (20% weight)                                 │
│  ─────────────────────────────                                 │
│  Agent Type: HUMAN 👤                                          │
│  Case Urgency: YES 🔴                                          │
│                                                                │
│  Human + Urgent = 0.8 (prefer human for urgent)               │
│  Weighted: 0.8 × 0.20 = 0.16                                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  URGENCY SCORE (10% weight)                                    │
│  ──────────────────────────                                    │
│  Is Urgent: YES 🔴                                             │
│  Multiplier: 1.0                                               │
│                                                                │
│  Weighted: 1.0 × 0.10 = 0.10                                  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│  FINAL SCORE                                                   │
│  ───────────                                                   │
│  0.40 + 0.20 + 0.16 + 0.10 = 0.86                             │
│                                                                │
│  🎯 86% MATCH - EXCELLENT FIT                                 │
└────────────────────────────────────────────────────────────────┘
```

## Agent Expertise Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                          AGENT EXPERTISE MATRIX                        │
└────────────────────────────────────────────────────────────────────────┘

Case Types:      Schengen SS    Work Visa    Student Visa
Locations:       Sydney  Melb   Brisbane

┌─────────────────────────────────────────────────────────────────────┐
│ HUMAN AGENTS                                                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 👤 Sarah Mitchell (H001) - Capacity: 15                            │
│    Schengen SS: ⭐⭐⭐  Work: ⭐⭐  Student: ⭐⭐                    │
│    Sydney: ⭐⭐⭐  Melbourne: ⭐⭐  Brisbane: ⭐                      │
│                                                                     │
│ 👤 Michael Chen (H002) - Capacity: 12                              │
│    Schengen SS: ⭐  Work: ⭐⭐⭐  Student: ⭐⭐⭐                    │
│    Sydney: ⭐⭐  Melbourne: ⭐⭐⭐  Brisbane: ⭐⭐                    │
│                                                                     │
│ 👤 Emma Rodriguez (H003) - Capacity: 10                            │
│    Schengen SS: ⭐⭐  Work: ⭐  Student: ⭐⭐                        │
│    Sydney: ⭐  Melbourne: ⭐  Brisbane: ⭐⭐⭐                        │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│ AI AGENTS                                                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ 🤖 AI Alpha (AI001) - Capacity: 50                                 │
│    Schengen SS: ⭐⭐⭐  Work: ⭐⭐⭐  Student: ⭐⭐                  │
│    Sydney: ⭐⭐⭐  Melbourne: ⭐⭐⭐  Brisbane: ⭐⭐⭐                │
│                                                                     │
│ 🤖 AI Beta (AI002) - Capacity: 45                                  │
│    Schengen SS: ⭐⭐  Work: ⭐⭐⭐  Student: ⭐⭐⭐                  │
│    Sydney: ⭐⭐  Melbourne: ⭐⭐⭐  Brisbane: ⭐⭐⭐                  │
│                                                                     │
│ 🤖 AI Gamma (AI003) - Capacity: 40                                 │
│    Schengen SS: ⭐⭐  Work: ⭐⭐  Student: ⭐⭐                      │
│    Sydney: ⭐⭐  Melbourne: ⭐⭐  Brisbane: ⭐⭐                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Legend: ⭐⭐⭐ Expert  ⭐⭐ Proficient  ⭐ Basic
```

## Capacity Visualization

```
┌──────────────────────────────────────────────────────────────────┐
│                    AGENT CAPACITY OVERVIEW                       │
└──────────────────────────────────────────────────────────────────┘

Total System Capacity: 172 cases
Current Workload: Variable based on assignments

👤 HUMAN AGENTS (37 total capacity)
────────────────────────────────────

Sarah Mitchell (H001)
[████████████░░░░░░░] 40% (6/15 cases) 🟢 Available

Michael Chen (H002)
[████░░░░░░░░░░░░░░░] 17% (2/12 cases) 🟢 Available

Emma Rodriguez (H003)
[░░░░░░░░░░░░░░░░░░░] 0% (0/10 cases) 🟢 Available


🤖 AI AGENTS (135 total capacity)
────────────────────────────────────

AI Agent Alpha (AI001)
[████████░░░░░░░░░░░] 40% (20/50 cases) 🟢 Available

AI Agent Beta (AI002)
[████░░░░░░░░░░░░░░░] 22% (10/45 cases) 🟢 Available

AI Agent Gamma (AI003)
[██████░░░░░░░░░░░░░] 30% (12/40 cases) 🟢 Available


🎯 CAPACITY LEGEND
────────────────────────────────────
🟢 Green (0-50%):   Agent has plenty of capacity
🟠 Orange (50-80%): Agent is moderately busy
🔴 Red (80-100%):   Agent is near capacity
```

## Recommendation Interface

```
┌──────────────────────────────────────────────────────────────────────┐
│                    🔍 CASE ASSIGNMENT RECOMMENDATIONS                │
└──────────────────────────────────────────────────────────────────────┘

Case Details:
  Application: RECOMMEND-001
  Type: Student Visa
  Location: Brisbane FO
  Urgent: No
  Nationality: Chinese

Top 3 Recommendations:

┌────────────────────────────────────────────────────────────────────┐
│ #1 - AI Agent Beta - Biometrics Specialist                ⭐ BEST │
│ ─────────────────────────────────────────────────────────────────  │
│ Score: 0.940 (94.0%)                                              │
│ Type: 🤖 AI                                                        │
│ Workload: 10/45 (22%)                                             │
│                                                                    │
│ Why this agent?                                                    │
│ • High expertise match                                             │
│ • Low workload                                                     │
│ • AI processing - faster turnaround                                │
│                                                                    │
│ Expertise Score: 2.8 / 3.0                                        │
│ [Assign to This Agent]                                            │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ #2 - Michael Chen - Case Officer                                  │
│ ─────────────────────────────────────────────────────────────────  │
│ Score: 0.927 (92.7%)                                              │
│ Type: 👤 HUMAN                                                     │
│ Workload: 2/12 (17%)                                              │
│                                                                    │
│ Why this agent?                                                    │
│ • High expertise match                                             │
│ • Low workload                                                     │
│ • Human verification available                                     │
│                                                                    │
│ Expertise Score: 3.0 / 3.0                                        │
│ [Assign to This Agent]                                            │
└────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│ #3 - Emma Rodriguez - Junior Case Officer                         │
│ ─────────────────────────────────────────────────────────────────  │
│ Score: 0.900 (90.0%)                                              │
│ Type: 👤 HUMAN                                                     │
│ Workload: 0/10 (0%)                                               │
│                                                                    │
│ Why this agent?                                                    │
│ • Good expertise match                                             │
│ • Low workload                                                     │
│ • Human verification available                                     │
│                                                                    │
│ Expertise Score: 2.4 / 3.0                                        │
│ [Assign to This Agent]                                            │
└────────────────────────────────────────────────────────────────────┘
```

---

**This visual guide provides:**
- System architecture overview
- UI layout reference
- Assignment flow diagrams
- Scoring algorithm visualization
- Agent expertise matrix
- Capacity monitoring views
- Recommendation interface examples

**For complete details, refer to:**
- CASE_ASSIGNMENT_README.md (Technical Documentation)
- CASE_ASSIGNMENT_QUICKSTART.md (User Guide)
- CASE_ASSIGNMENT_IMPLEMENTATION.md (Implementation Summary)
