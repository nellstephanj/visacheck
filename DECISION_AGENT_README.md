# Application Decision Agent - Documentation

## Overview

The Application Decision Agent is an AI-powered advisory system that provides visa application decision recommendations to human officers. It analyzes multiple criteria including financial sufficiency, travel documentation, background checks, and document consistency to generate a comprehensive recommendation with transparent reasoning.

**⚠️ Important:** The Decision Agent provides **advisory recommendations only**. All final legal decisions must be made by qualified human officers. The agent's role is to support, not replace, human judgment.

## Purpose

The Decision Agent serves to:
- Provide consistent, objective preliminary assessments
- Highlight critical issues requiring human attention
- Standardize evaluation criteria across cases
- Accelerate case processing while maintaining quality
- Ensure transparent, traceable decision rationale

## Features

### 1. Multi-Dimensional Scoring System (100 points total)

#### 💰 Funds Sufficiency (40 points)
- Evaluates bank balance against required funds
- Considers destination-specific daily cost thresholds
- Accounts for accommodation costs and safety buffers
- Flags suspicious recent large deposits (≤14 days)
- Calculates coverage percentage against requirements

**Scoring:**
- 40 pts: ≥120% coverage (Excellent)
- 35 pts: 100-119% coverage (Adequate)
- 30 pts: 85-99% coverage (Marginal)
- 20 pts: 70-84% coverage (Insufficient)
- 10 pts: <70% coverage (Severely insufficient)

**Penalties:**
- -10 pts for recent large deposits within 14 days

#### ✈️ Travel Proof Completeness (20 points)

**Flight Tickets (10 points):**
- Return flight confirmation
- Date consistency with travel plan
- Name matching across documents

**Hotel Reservations (10 points):**
- Coverage percentage across stay duration
- Refundable vs non-refundable status
- Gap tolerance (configurable, default ≤1 day)

**Scoring:**
- 10 pts: ≥95% coverage (Excellent)
- 8 pts: 80-94% coverage (Good)
- 5 pts: 60-79% coverage (Partial)
- 2 pts: <60% coverage (Inadequate)

#### 🔍 Background Check (20 points)

**Police Report Status (10 points):**
- Clear: 10 points
- Issues detected: 3 points
- Missing/Invalid: 0 points

**Schengen Database Check (10 points):**
- No alerts: 10 points
- Prior violations: 3 points
- Active entry ban: 0 points (automatic MANUAL_REVIEW)
- Inconclusive: 7 points

#### 📋 Document Consistency & Authenticity (20 points)

Evaluates:
- Name consistency across all documents (-5 pts penalty)
- Date consistency verification (-5 pts penalty)
- Passport MRZ validation (-7 pts penalty)
- Document integrity analysis (-3 pts if <90%)
- Photo matching confidence (-5 pts if <85%)

**Scoring:**
- 18-20 pts: Excellent consistency
- 15-17 pts: Good with minor discrepancies
- 10-14 pts: Moderate issues requiring attention
- 0-9 pts: Significant authenticity concerns

### 2. Decision Thresholds

The system uses the following decision logic:

```
if blocking_issues_present:
    → MANUAL_REVIEW
elif total_score >= 85:
    → APPROVE
elif 60 <= total_score < 85:
    → MANUAL_REVIEW
elif total_score < 60:
    → REJECT
```

**Blocking Issues** (trigger immediate MANUAL_REVIEW):
- Active Schengen entry ban
- MRZ validation failure
- Critical security flags

### 3. Transparent Output Structure

```json
{
  "decision_recommendation": {
    "status": "APPROVE | REJECT | MANUAL_REVIEW",
    "score": 78,
    "score_breakdown": {
      "funds": {
        "score": 30,
        "max_score": 40,
        "reason": "Funds cover 85% of requirement; large inflow detected 7 days ago.",
        "details": {
          "bank_balance": 5000.00,
          "required_funds": 5500.00,
          "coverage_percentage": 85.0,
          "daily_rate": 80
        }
      },
      "travel_proof": {
        "score": 18,
        "max_score": 20,
        "reason": "Round-trip confirmed; hotel covers 90% of days.",
        "details": { /* ... */ }
      },
      "background": {
        "score": 20,
        "max_score": 20,
        "reason": "No negative hits found.",
        "details": { /* ... */ }
      },
      "consistency": {
        "score": 10,
        "max_score": 20,
        "reason": "Minor name punctuation mismatch between ticket and passport.",
        "details": { /* ... */ }
      }
    },
    "blocking_issues": [],
    "soft_concerns": [
      "Recent large deposit may require explanation."
    ],
    "policy_refs": [
      "POL-FUNDS-1.3",
      "POL-TRAVEL-2.0",
      "POL-SEC-1.1"
    ],
    "justification": "Application shows moderate concerns. Manual review recommended to assess risk factors.",
    "generated_at": "2025-10-27T10:30:00Z"
  }
}
```

## User Interface

### 1. Application Decision Page

**Location:** `pages/decision.py`

**Access:** 
- From Active Applications page, click "🎯 Decide" button for any application
- Also available in sidebar navigation: ⚖️ Application Decision

**Layout:**

1. **Application Summary** (collapsible)
   - Application number, case type, visa type
   - Applicant nationality and intake location
   - Submission date and processing duration
   - Urgency status

2. **AI Recommendation Generation**
   - Generate recommendation button
   - Visual score breakdown with gauges
   - Overall status badge (color-coded)
   - Score: X/100 display

3. **Score Breakdown Section**
   - Four visual progress bars for each criterion
   - Detailed reasoning for each score
   - Real-time percentage calculations

4. **Issues & Concerns Display**
   - Blocking Issues (red alerts)
   - Soft Concerns (orange warnings)
   - Side-by-side comparison

5. **AI Expert Analysis** (optional)
   - Natural language explanation
   - Generated via OpenAI GPT
   - 3-4 paragraph professional analysis
   - Highlights key decision factors

6. **Human Officer Decision Interface**
   - Decision selector (APPROVE/REJECT/REQUEST MORE INFO)
   - Officer name field (auto-filled from session)
   - Justification text area (required)
   - Submit/Save Draft/Back buttons

### 2. Visual Elements

**Status Badge Colors:**
- 🟢 Green: APPROVE
- 🔴 Red: REJECT
- 🟠 Orange: MANUAL_REVIEW
- ⚫ Gray: ERROR

**Score Gauges:**
- Green: ≥80% of max score
- Orange: 60-79% of max score
- Red: <60% of max score

## Technical Implementation

### Service Layer: `decision_agent_service.py`

**Class:** `DecisionAgentService`

**Key Methods:**

1. `calculate_funds_score(application_data)` → Dict
2. `calculate_travel_proof_score(application_data)` → Dict
3. `calculate_background_score(application_data)` → Dict
4. `calculate_consistency_score(application_data)` → Dict
5. `generate_decision_recommendation(application_data)` → Dict
6. `get_ai_recommendation_explanation(recommendation, application_data)` → str (async)

**Dependencies:**
- `azure_handler`: Azure Table Storage operations
- `openai_handler`: OpenAI GPT API integration

### Data Flow

```
1. User selects application → Active Applications page
2. Click "🎯 Decide" → Navigate to Decision page
3. Click "Generate Recommendation" → Call DecisionAgentService
4. Load person data from res/people/*.json
5. Generate mock application data (temp - will be from doc processing)
6. Calculate 4 dimension scores
7. Aggregate scores → total recommendation
8. Display visual dashboard
9. Optional: Generate AI explanation via GPT
10. Human officer reviews and makes final decision
11. Submit decision → Store record (DB integration pending)
```

## Configuration

### Daily Rate Thresholds (configurable in service)

```python
daily_rates = {
    'Germany': 80,
    'France': 90,
    'Italy': 75,
    'Spain': 70,
    'Netherlands': 85,
    'default': 80
}
```

### Buffer Percentage
- Default: 20% (1.20x multiplier on required funds)

### Gap Tolerance
- Hotel coverage: ≤1 day gap acceptable

### Recent Deposit Window
- Flagged if deposit within 14 days of application

## Policy References

The system references internal policy codes for traceability:

- `POL-FUNDS-1.3`: Financial sufficiency requirements
- `POL-TRAVEL-2.0`: Travel documentation standards
- `POL-SEC-1.1`: Security and background check protocols
- `POL-AUTH-3.2`: Document authenticity verification

## Integration Points

### Current Integrations

1. **Active Applications Page**
   - Added "🎯 Decide" button alongside "🤖 Agent" button
   - Stores application data in session state
   - Navigates to decision page

2. **Main Navigation**
   - Registered as "⚖️ Application Decision" in sidebar
   - Available to all authenticated users
   - Positioned after Sexy Visa Agent

3. **Session Management**
   - Uses SessionManager for authentication checks
   - Stores recommendation in session state
   - Maintains application context across pages

### Future Integrations (Pending)

1. **Document Verification Agent** → Extract actual document data
2. **Biometrics Agent** → Photo matching confidence scores
3. **EU-VIS Matching** → Real Schengen database queries
4. **Azure Table Storage** → Persist decision records
5. **Audit Logging** → Track all recommendations and decisions
6. **Email Notifications** → Alert supervisors of critical cases

## Usage Workflow

### For Human Officers

1. **Navigate to Active Applications**
   - Review queue of pending applications
   - Filter by urgency, days in process, nationality, etc.

2. **Select Application for Decision**
   - Click "🎯 Decide" button on target application
   - System loads complete application context

3. **Generate AI Recommendation**
   - Click "🔄 Generate AI Recommendation"
   - System analyzes all criteria (2-3 seconds)
   - Visual dashboard displays results

4. **Review Score Breakdown**
   - Examine each of 4 criterion scores
   - Read detailed reasoning for each score
   - Note any blocking issues or soft concerns

5. **Request AI Analysis (Optional)**
   - Click "🧠 Generate Detailed AI Analysis"
   - Read comprehensive natural language explanation
   - Understand AI reasoning and focus areas

6. **Make Human Decision**
   - Consider AI recommendation as advisory input
   - Apply professional judgment and experience
   - Select final decision: APPROVE/REJECT/REQUEST MORE INFO
   - Provide detailed justification in notes field

7. **Submit Decision**
   - Click "✅ Submit Decision"
   - System records final decision with timestamp
   - Application moves to appropriate queue

## Mock Data Generation

**Current State:** Decision agent uses mock data for demonstration.

**Mock Data Generator:** `generate_mock_application_data()`

**Mocked Fields:**
- Bank balance, duration, accommodation costs
- Flight and hotel booking status
- Police report and watchlist status
- Document consistency indicators

**Transition Plan:**
- Phase 1: Mock data (current)
- Phase 2: Integrate with Document Verification Agent
- Phase 3: Real-time document extraction
- Phase 4: Live database queries

## Security & Compliance

### Data Privacy
- All application data handled per GDPR requirements
- No personally identifiable information in logs
- Secure session state management

### Bias Mitigation
- Criteria are objective and transparent
- No nationality-based scoring adjustments
- Regular audits of recommendation patterns
- Human oversight on all final decisions

### Auditability
- All recommendations timestamped
- Policy references included in output
- Score breakdown fully traceable
- Human decisions recorded with justification

## Error Handling

The system gracefully handles:
- Missing person data → Uses application data only
- OpenAI API failures → Displays error, continues workflow
- Invalid data formats → Returns 0 scores with error messages
- Session state issues → Redirects to Active Applications

## Performance Considerations

- **Recommendation Generation:** ~2-3 seconds
- **AI Explanation (optional):** ~5-10 seconds
- **Page Load:** <1 second
- **Session State:** Minimal memory footprint

## Future Enhancements

### Planned Features

1. **Machine Learning Enhancement**
   - Learn from human override patterns
   - Adjust scoring weights based on historical accuracy
   - Anomaly detection in application patterns

2. **Advanced Analytics Dashboard**
   - Success rate by recommendation type
   - Human override frequency and reasons
   - Processing time metrics
   - Officer performance comparisons

3. **Automated Notifications**
   - Alert supervisors of high-risk cases
   - Notify officers of pending decisions
   - Send applicant updates on status changes

4. **Document Upload Integration**
   - Direct upload of verification documents
   - Automatic OCR and data extraction
   - Real-time validation feedback

5. **Multi-Language Support**
   - Interface localization
   - Document translation
   - Multilingual AI explanations

6. **Mobile Application**
   - Tablet-optimized interface
   - Offline decision capability
   - Biometric authentication

## Testing & Validation

### Test Cases

1. **High Score (≥85)** → Should recommend APPROVE
2. **Medium Score (60-84)** → Should recommend MANUAL_REVIEW
3. **Low Score (<60)** → Should recommend REJECT
4. **Blocking Issue Present** → Should recommend MANUAL_REVIEW regardless of score
5. **Missing Data** → Should handle gracefully with error messages

### Validation Criteria

- ✅ Scores sum correctly to 100 max points
- ✅ All flags properly categorized (blocking vs soft)
- ✅ Policy references accurate and relevant
- ✅ UI displays all score components
- ✅ Human decision overrides stored correctly
- ✅ Session state maintained across navigation

## Support & Documentation

### Getting Help

**In-App:**
- ℹ️ Decision Criteria Information (expandable section)
- 📚 Workflow Guidelines button (links to docs)
- ✉️ Mail Support button (support@visacheck.com)

**Documentation:**
- This README file
- ARCHITECTURE.md (system design)
- CASE_ASSIGNMENT_README.md (related feature)
- VISA_INTAKE_README.md (data entry)

### Troubleshooting

**Issue:** Recommendation not generating
- **Solution:** Check OpenAI API credentials, verify person data exists

**Issue:** Score seems incorrect
- **Solution:** Review mock data generation, check calculation logic

**Issue:** Page navigation fails
- **Solution:** Verify session state has 'decision_app_data', check authentication

**Issue:** AI explanation times out
- **Solution:** OpenAI API may be slow, try again or skip explanation

## Conclusion

The Application Decision Agent is a powerful advisory tool that enhances visa processing efficiency while maintaining human oversight. By providing transparent, consistent recommendations with detailed reasoning, it enables officers to make informed decisions quickly while ensuring all applications receive thorough evaluation.

Remember: **The AI recommends, the human decides.**

---

**Version:** 1.0  
**Last Updated:** October 27, 2025  
**Author:** VisaCheck Development Team  
**Contact:** support@visacheck.com
