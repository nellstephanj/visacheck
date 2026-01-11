# Decision Agent - Visual Quick Guide

## 🎯 Quick Access

### From Active Applications Page:

```
┌─────────────────────────────────────────────────────────────┐
│ Active Applications                                         │
├─────────────────────────────────────────────────────────────┤
│ Application # | Status | Days | ... | Actions              │
│ APP-2024-001  | Active |  15  | ... | [🤖 Agent] [🎯 Decide]│
│                                         ↑          ↑         │
│                                         │          └─ Click! │
│                                   Sexy Agent                 │
└─────────────────────────────────────────────────────────────┘
```

### From Sidebar Navigation:

```
🔐 Login
📄 VisaCheck
📊 Active Applications
🎯 Case Assignment
🤖 Visa AI
⚖️ Application Decision  ← Click here!
📋 Visa Intake
🔍 EU-VIS Matching
```

---

## 📊 Decision Dashboard Layout

```
╔══════════════════════════════════════════════════════════════╗
║  🎯 Application Decision - APP-2024-001                      ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  📋 Application Summary (collapsible)                        ║
║  ├─ Application #: APP-2024-001                             ║
║  ├─ Case Type: Standard                                     ║
║  ├─ Visa Type: Schengen Tourist                            ║
║  └─ Days in Process: 15                                     ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  🤖 AI Decision Recommendation                               ║
║                                                              ║
║  [🔄 Generate AI Recommendation]  ← Click to analyze        ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║         ┌─────────────────────────────────┐                 ║
║         │  ⚠️  MANUAL_REVIEW              │                 ║
║         │  Overall Score: 78/100          │                 ║
║         └─────────────────────────────────┘                 ║
║                                                              ║
║  📊 Score Breakdown                                          ║
║                                                              ║
║  💰 Funds Sufficiency                           30/40       ║
║  ████████████████████████░░░░░░░░░░   75%                  ║
║  └─ Funds cover 85% of requirement; large inflow detected  ║
║                                                              ║
║  ✈️ Travel Proof Completeness                   18/20       ║
║  ██████████████████████████████████░   90%                  ║
║  └─ Round-trip confirmed; hotel covers 90% of days         ║
║                                                              ║
║  🔍 Background Check                             20/20       ║
║  ████████████████████████████████████  100%                 ║
║  └─ No negative hits found.                                ║
║                                                              ║
║  📋 Document Consistency                         10/20       ║
║  ████████████████░░░░░░░░░░░░░░░░░░   50%                  ║
║  └─ Minor name punctuation mismatch between docs           ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🚫 Blocking Issues        │  ⚠️ Soft Concerns              ║
║  ├─ None detected          │  ├─ Recent large deposit      ║
║  └─ ✅ Clear              │  └─ requires explanation        ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  📜 Policy References: POL-FUNDS-1.3, POL-TRAVEL-2.0        ║
╠══════════════════════════════════════════════════════════════╣
║  📝 AI Justification:                                        ║
║  Application shows moderate concerns. Manual review          ║
║  recommended to assess risk factors.                         ║
╠══════════════════════════════════════════════════════════════╣
║  💬 AI Expert Analysis                                       ║
║                                                              ║
║  [🧠 Generate Detailed AI Analysis]  ← Optional             ║
║                                                              ║
║  (3-4 paragraph expert analysis appears here)               ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  👤 Human Officer Decision                                   ║
║                                                              ║
║  ⚠️ The AI recommendation is advisory only.                 ║
║     Final decision rests with the human officer.            ║
║                                                              ║
║  Final Decision: [--- Select Decision ---]  ▼               ║
║                  ├─ APPROVE                                  ║
║                  ├─ REJECT                                   ║
║                  └─ REQUEST MORE INFO                        ║
║                                                              ║
║  Officer Name:   [John Smith            ]                   ║
║                                                              ║
║  Officer Notes:  ┌─────────────────────────────────┐        ║
║                  │ After reviewing AI analysis,    │        ║
║                  │ I recommend manual review of    │        ║
║                  │ the recent deposit before...    │        ║
║                  └─────────────────────────────────┘        ║
║                                                              ║
║  [✅ Submit Decision] [📋 Save Draft] [🔙 Back]             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 🎨 Color Coding System

### Status Badge Colors

```
┌────────────┬───────────┬──────────────┐
│ Status     │ Color     │ Icon         │
├────────────┼───────────┼──────────────┤
│ APPROVE    │ 🟢 Green  │ ✅           │
│ REJECT     │ 🔴 Red    │ ❌           │
│ MANUAL_REV │ 🟠 Orange │ ⚠️           │
│ ERROR      │ ⚫ Gray   │ 🔴           │
└────────────┴───────────┴──────────────┘
```

### Score Gauge Colors

```
█████████████████████████████████ 100%  🟢 Green  (≥80%)
████████████████████░░░░░░░░░░░░  60%   🟠 Orange (60-79%)
█████████░░░░░░░░░░░░░░░░░░░░░░░  30%   🔴 Red    (<60%)
```

### Days in Process Circles (Active Apps)

```
  ┌────┐        ┌────┐        ┌────┐
  │ 8  │ 🟢     │ 18 │ 🟠     │ 35 │ 🔴
  └────┘        └────┘        └────┘
  ≤15 days     16-30 days     >30 days
```

---

## 🔄 Workflow Diagram

```
                    START
                      │
                      ▼
        ┌─────────────────────────┐
        │  Active Applications    │
        │  Page                   │
        └────────┬────────────────┘
                 │
         Click "🎯 Decide"
                 │
                 ▼
        ┌─────────────────────────┐
        │  Application Decision   │
        │  Page Loads             │
        └────────┬────────────────┘
                 │
         Click "Generate AI Rec"
                 │
                 ▼
        ┌─────────────────────────┐
        │  Load Person Data       │
        │  from res/people/*.json │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  Generate Mock App Data │
        │  (temp - will be real)  │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  DecisionAgentService   │
        │  Calculates 4 Scores:   │
        │  ├─ Funds (40 pts)      │
        │  ├─ Travel (20 pts)     │
        │  ├─ Background (20 pts) │
        │  └─ Consistency (20 pts)│
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  Aggregate Total Score  │
        │  Apply Decision Logic   │
        │  ├─ Score ≥85 → APPROVE │
        │  ├─ 60-84 → MANUAL_REV  │
        │  ├─ <60 → REJECT        │
        │  └─ Block → MANUAL_REV  │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │  Display Visual         │
        │  Dashboard              │
        │  ├─ Status Badge        │
        │  ├─ Score Gauges        │
        │  ├─ Issues/Concerns     │
        │  └─ Justification       │
        └────────┬────────────────┘
                 │
         Optional: Generate AI Analysis
                 │
                 ▼
        ┌─────────────────────────┐
        │  Human Officer Reviews  │
        │  ├─ Reads AI rec        │
        │  ├─ Applies judgment    │
        │  └─ Makes final decision│
        └────────┬────────────────┘
                 │
         Select Decision + Notes
                 │
                 ▼
        ┌─────────────────────────┐
        │  Submit Decision        │
        │  ├─ Store record        │
        │  ├─ Update status       │
        │  └─ Move to next queue  │
        └────────┬────────────────┘
                 │
                 ▼
                 END
```

---

## 📝 Score Calculation Details

### Funds Sufficiency (40 pts max)

```
Required Funds = (Daily Rate × Duration) + Accommodation Cost
With Buffer    = Required Funds × 1.20

Coverage % = (Bank Balance / Required with Buffer) × 100

┌─────────────┬────────┬──────────────────┐
│ Coverage %  │ Score  │ Description      │
├─────────────┼────────┼──────────────────┤
│ ≥120%       │ 40 pts │ Excellent        │
│ 100-119%    │ 35 pts │ Adequate         │
│ 85-99%      │ 30 pts │ Marginal         │
│ 70-84%      │ 20 pts │ Insufficient     │
│ <70%        │ 10 pts │ Severely Insuff  │
└─────────────┴────────┴──────────────────┘

Penalty: -10 pts if large deposit ≤14 days ago
```

### Travel Proof (20 pts max)

```
Flight Tickets (10 pts):
├─ Has return + dates + names match     → 10 pts
├─ Has return + dates (name mismatch)   → 8 pts
├─ Has return (dates inconsistent)      → 5 pts
└─ No return flight                     → 0 pts

Hotel Reservations (10 pts):
├─ ≥95% coverage   → 10 pts
├─ 80-94% coverage → 8 pts
├─ 60-79% coverage → 5 pts
└─ <60% coverage   → 2 pts
```

### Background Check (20 pts max)

```
Police Report (10 pts):
├─ Clear   → 10 pts
├─ Issues  → 3 pts
└─ Missing → 0 pts

Schengen DB (10 pts):
├─ No alerts           → 10 pts
├─ Inconclusive        → 7 pts
├─ Prior violations    → 3 pts
└─ Active entry ban    → 0 pts (MANUAL_REVIEW)
```

### Document Consistency (20 pts max)

```
Start: 20 pts

Deductions:
├─ Name inconsistent      → -5 pts
├─ Dates inconsistent     → -5 pts
├─ MRZ invalid            → -7 pts
├─ Doc integrity <90%     → -3 pts
└─ Photo match <85%       → -5 pts

Minimum: 0 pts
```

---

## 🎯 Decision Thresholds

```
                SCORE SCALE
    0  10  20  30  40  50  60  70  80  85 90  100
    ├───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
    │                              │           │
    │         REJECT               │  MANUAL   │ APPROVE
    │        (score <60)           │  REVIEW   │ (≥85)
    │                              │ (60-84)   │
    └──────────────────────────────┴───────────┴────
    
    * Blocking issues → MANUAL_REVIEW (override score)
```

---

## 📊 Sample Recommendations

### Example 1: High Score → APPROVE

```
┌────────────────────────────────────────┐
│  ✅ APPROVE                            │
│  Overall Score: 88/100                 │
├────────────────────────────────────────┤
│  💰 Funds:         38/40  (95%)        │
│  ✈️ Travel:        20/20  (100%)       │
│  🔍 Background:    20/20  (100%)       │
│  📋 Consistency:   10/20  (50%)        │
├────────────────────────────────────────┤
│  🚫 No blocking issues                 │
│  ⚠️ Minor name variation in ticket     │
└────────────────────────────────────────┘
```

### Example 2: Medium Score → MANUAL_REVIEW

```
┌────────────────────────────────────────┐
│  ⚠️ MANUAL_REVIEW                      │
│  Overall Score: 72/100                 │
├────────────────────────────────────────┤
│  💰 Funds:         30/40  (75%)        │
│  ✈️ Travel:        15/20  (75%)        │
│  🔍 Background:    17/20  (85%)        │
│  📋 Consistency:   10/20  (50%)        │
├────────────────────────────────────────┤
│  🚫 No blocking issues                 │
│  ⚠️ 3 soft concerns detected           │
└────────────────────────────────────────┘
```

### Example 3: Low Score → REJECT

```
┌────────────────────────────────────────┐
│  ❌ REJECT                             │
│  Overall Score: 48/100                 │
├────────────────────────────────────────┤
│  💰 Funds:         10/40  (25%)        │
│  ✈️ Travel:         8/20  (40%)        │
│  🔍 Background:    20/20  (100%)       │
│  📋 Consistency:   10/20  (50%)        │
├────────────────────────────────────────┤
│  🚫 No blocking issues                 │
│  ⚠️ Severely insufficient funds        │
│  ⚠️ Incomplete travel documentation    │
└────────────────────────────────────────┘
```

### Example 4: Blocking Issue → MANUAL_REVIEW

```
┌────────────────────────────────────────┐
│  ⚠️ MANUAL_REVIEW                      │
│  Overall Score: 65/100                 │
├────────────────────────────────────────┤
│  💰 Funds:         35/40  (88%)        │
│  ✈️ Travel:        18/20  (90%)        │
│  🔍 Background:     0/20  (0%)         │
│  📋 Consistency:   12/20  (60%)        │
├────────────────────────────────────────┤
│  🚫 CRITICAL: Active entry ban         │
│  ⚠️ Schengen database alert            │
└────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Issue: Button not appearing

```
Problem: "🎯 Decide" button missing
Solution: Check Active Applications page is loaded
         Verify authentication (logged in)
         Refresh page
```

### Issue: Recommendation not generating

```
Problem: Error when clicking "Generate"
Solution: 1. Check person data exists in res/people/
         2. Verify OpenAI API credentials
         3. Check browser console for errors
         4. Try different application
```

### Issue: Score looks wrong

```
Problem: Score doesn't match expectation
Solution: 1. Review score breakdown details
         2. Check mock data generation
         3. Verify calculation logic
         4. See DECISION_AGENT_README.md
```

### Issue: Can't submit decision

```
Problem: Submit button doesn't work
Solution: 1. Select a decision from dropdown
         2. Fill in officer notes (required)
         3. Verify officer name is filled
         4. Check for error messages
```

---

## ✨ Tips for Human Officers

1. **Always read the AI justification** - It summarizes key concerns

2. **Check blocking issues first** - These require immediate attention

3. **Review soft concerns** - These may need additional documentation

4. **Use the AI analysis feature** - Provides valuable context

5. **Document your reasoning** - Especially if overriding AI recommendation

6. **Consider policy references** - Link to official guidelines

7. **Check days in process** - Urgent cases may need priority

8. **Look at consistency score** - Low scores may indicate fraud

---

## 📱 Quick Reference Card

```
╔════════════════════════════════════════╗
║   DECISION AGENT QUICK REFERENCE       ║
╠════════════════════════════════════════╣
║ 🎯 Access: Active Apps → "🎯 Decide"  ║
║ 🤖 Generate: Click "Generate AI Rec"   ║
║ 📊 Scores: 4 criteria, 100 pts total  ║
║ ⚖️ Thresholds:                         ║
║    • ≥85 → APPROVE                     ║
║    • 60-84 → MANUAL_REVIEW             ║
║    • <60 → REJECT                      ║
║ 🚫 Block → Always MANUAL_REVIEW        ║
║ 👤 Human decides, AI advises           ║
║ 📝 Notes required for submission       ║
╚════════════════════════════════════════╝
```

---

**Need Help?**  
📚 See: DECISION_AGENT_README.md (full documentation)  
✉️ Email: support@visacheck.com  
🔗 Link: Workflow Guidelines (in-app)

