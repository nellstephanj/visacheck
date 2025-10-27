# Decision Agent - Quick Start Guide

## 🚀 Getting Started in 3 Minutes

### Step 1: Access the Feature (30 seconds)

**Option A: From Active Applications**
1. Navigate to "📊 Active Applications" in the sidebar
2. Find any application in the list
3. Click the **"🎯 Decide"** button in the Action column

**Option B: Direct Navigation**
1. Look at the sidebar
2. Click "⚖️ Application Decision"
3. (Requires selecting an application first from Active Apps)

### Step 2: Generate AI Recommendation (30 seconds)

1. You'll see the Application Decision page
2. Review the application summary (optional - can collapse it)
3. Click the big blue button: **"🔄 Generate AI Recommendation"**
4. Wait 2-3 seconds for analysis

### Step 3: Review the Recommendation (1 minute)

You'll see a visual dashboard with:

1. **Status Badge** (top center)
   - Green ✅ = APPROVE
   - Orange ⚠️ = MANUAL_REVIEW
   - Red ❌ = REJECT

2. **Score Breakdown** (4 colored bars)
   - 💰 Funds (40 points max)
   - ✈️ Travel Proof (20 points max)
   - 🔍 Background (20 points max)
   - 📋 Consistency (20 points max)

3. **Issues Section** (two columns)
   - Left: 🚫 Blocking Issues (critical)
   - Right: ⚠️ Soft Concerns (warnings)

4. **AI Justification** (blue box)
   - One paragraph explanation

### Step 4: Make Your Decision (1 minute)

1. Scroll to "👤 Human Officer Decision" section
2. Select from dropdown:
   - APPROVE
   - REJECT
   - REQUEST MORE INFO
3. Type your justification in the text box (required)
4. Click **"✅ Submit Decision"**

Done! 🎉

---

## 📊 Understanding the Scores

### Quick Reference

| Score | Meaning | Recommendation |
|-------|---------|----------------|
| 85-100 | Excellent | ✅ APPROVE |
| 60-84 | Good/Fair | ⚠️ MANUAL_REVIEW |
| 0-59 | Poor | ❌ REJECT |

### What Each Criterion Means

**💰 Funds (40 pts)** - Does applicant have enough money?
- Checks bank balance
- Calculates required funds for trip
- Flags suspicious deposits

**✈️ Travel Proof (20 pts)** - Do they have tickets and hotels?
- Return flight confirmed?
- Hotel bookings cover the stay?
- Names match on all documents?

**🔍 Background (20 pts)** - Are they safe to admit?
- Police clearance clean?
- No Schengen violations?
- No entry bans?

**📋 Consistency (20 pts)** - Do documents match up?
- Same name everywhere?
- Dates line up?
- Passport looks authentic?

---

## ⚠️ Key Things to Know

### 1. The AI is Advisory Only
- You make the final decision
- AI provides recommendations
- You can disagree (with justification)

### 2. Blocking Issues Override Scores
- Even a high score → MANUAL_REVIEW if there's a critical issue
- Examples: Entry ban, invalid passport, security flag
- Always review these first

### 3. You Must Justify Your Decision
- Text box is required
- Explain your reasoning
- Note if you override AI recommendation

### 4. Optional AI Analysis
- Click "🧠 Generate Detailed AI Analysis" for more context
- Takes 5-10 seconds
- Provides 3-4 paragraph expert explanation
- Useful for complex cases

---

## 🎨 Color Guide

### Status Colors
- 🟢 **Green** = APPROVE (safe to proceed)
- 🟠 **Orange** = MANUAL_REVIEW (needs attention)
- 🔴 **Red** = REJECT (should decline)

### Score Bar Colors
- 🟢 **Green bar** = ≥80% (good score)
- 🟠 **Orange bar** = 60-79% (fair score)
- 🔴 **Red bar** = <60% (poor score)

---

## 💡 Pro Tips

### For Quick Reviews
1. Check the overall score first
2. Look at blocking issues (if any)
3. Scan the 4 score bars
4. Read AI justification
5. Make decision

### For Detailed Reviews
1. Click "🧠 Generate Detailed AI Analysis"
2. Read all score reasons
3. Review both blocking issues and soft concerns
4. Check policy references
5. Cross-reference with documents
6. Make informed decision

### When to Override AI
✅ **Good Reasons to Override:**
- You have additional context AI doesn't know
- Recent policy changes not in system
- Humanitarian considerations
- Supervisor guidance

❌ **Poor Reasons to Override:**
- "Just a feeling"
- Ignoring blocking issues
- Skipping justification
- Rushing without review

---

## 🔧 Common Scenarios

### Scenario 1: High Score, No Issues
```
Score: 92/100
Status: ✅ APPROVE
Blocking Issues: None
Soft Concerns: None

→ Recommendation: APPROVE
→ Your Action: Likely APPROVE (review briefly, submit)
```

### Scenario 2: Medium Score, Soft Concerns
```
Score: 72/100
Status: ⚠️ MANUAL_REVIEW
Blocking Issues: None
Soft Concerns: Recent large deposit, minor name variation

→ Recommendation: MANUAL_REVIEW
→ Your Action: Request additional documents or explanation
```

### Scenario 3: Low Score, Insufficient Funds
```
Score: 48/100
Status: ❌ REJECT
Blocking Issues: None
Soft Concerns: Severely insufficient funds, missing hotel bookings

→ Recommendation: REJECT
→ Your Action: Likely REJECT (insufficient resources for trip)
```

### Scenario 4: High Score BUT Blocking Issue
```
Score: 88/100
Status: ⚠️ MANUAL_REVIEW
Blocking Issues: Active Schengen entry ban
Soft Concerns: None

→ Recommendation: MANUAL_REVIEW (overrides high score)
→ Your Action: REJECT (entry ban is disqualifying)
```

---

## 🐛 Troubleshooting

### Problem: Can't find the "🎯 Decide" button
**Solution:** Go to Active Applications page, button is in the Actions column

### Problem: "Generate" button not working
**Solution:** Check internet connection, refresh page, try different application

### Problem: Score seems wrong
**Solution:** Click the collapsible details under each score to see calculations

### Problem: Can't submit decision
**Solution:** Make sure you've selected a decision AND filled in officer notes

### Problem: AI Analysis timing out
**Solution:** Skip it (it's optional), or try again in a moment

---

## 📱 Quick Reference Card

Print or save this:

```
╔════════════════════════════════════════╗
║     DECISION AGENT QUICK CARD          ║
╠════════════════════════════════════════╣
║ ACCESS: Active Apps → "🎯 Decide"     ║
╠════════════════════════════════════════╣
║ SCORES (100 total):                    ║
║  💰 Funds:        /40                  ║
║  ✈️ Travel:       /20                  ║
║  🔍 Background:   /20                  ║
║  📋 Consistency:  /20                  ║
╠════════════════════════════════════════╣
║ THRESHOLDS:                            ║
║  85+  → ✅ APPROVE                     ║
║  60-84 → ⚠️ MANUAL_REVIEW             ║
║  0-59  → ❌ REJECT                     ║
║  🚫 Block → ⚠️ MANUAL_REVIEW          ║
╠════════════════════════════════════════╣
║ REMEMBER:                              ║
║  • AI advises, you decide             ║
║  • Justify your decision               ║
║  • Check blocking issues first         ║
║  • Override if you have good reason    ║
╚════════════════════════════════════════╝
```

---

## 🎯 Your First Decision (Walkthrough)

Let's do one together:

1. **Go to Active Applications**
   - Look at the sidebar
   - Click "📊 Active Applications"

2. **Pick an application**
   - Any row works for testing
   - Find the "Action" column on the right
   - Click "🎯 Decide"

3. **Generate recommendation**
   - Click the blue "🔄 Generate AI Recommendation" button
   - Wait 2-3 seconds

4. **Read the result**
   - What's the overall score?
   - What color is the status badge?
   - Any blocking issues?

5. **Review details**
   - Look at the 4 score bars
   - Which is lowest?
   - Read the reasons under each bar

6. **Check concerns**
   - Left column: Blocking issues (critical)
   - Right column: Soft concerns (warnings)
   - Any red flags?

7. **Read AI justification**
   - Blue box at the bottom
   - What does the AI recommend?
   - Do you agree?

8. **Make your decision**
   - Scroll to "👤 Human Officer Decision"
   - Select: APPROVE, REJECT, or REQUEST MORE INFO
   - Type why you decided that way
   - Click "✅ Submit Decision"

Congratulations! You've completed your first AI-assisted decision! 🎉

---

## 📚 Need More Help?

- **Full Documentation:** `DECISION_AGENT_README.md`
- **Visual Guide:** `DECISION_AGENT_VISUAL_GUIDE.md`
- **Implementation Details:** `DECISION_AGENT_IMPLEMENTATION.md`
- **Support Email:** support@visacheck.com

---

## ✅ Checklist for Your First 10 Decisions

Use this to build confidence:

- [ ] 1. Complete first decision (any result)
- [ ] 2. APPROVE a high-score application
- [ ] 3. REJECT a low-score application
- [ ] 4. MANUAL_REVIEW a medium-score case
- [ ] 5. Handle an application with blocking issues
- [ ] 6. Override an AI recommendation (with justification)
- [ ] 7. Use the "Generate AI Analysis" feature
- [ ] 8. Process an urgent case (🔴 flag)
- [ ] 9. Review policy references
- [ ] 10. Handle a case with soft concerns only

After 10 decisions, you'll be an expert! 🏆

---

**Ready to start? Let's go! 🚀**

Navigate to **Active Applications** and click **"🎯 Decide"** on any application!

