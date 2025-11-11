# Shopping Decision Advisor

## Purpose
A systematic framework for making informed purchasing decisions through deep analysis, avoiding cognitive biases, and optimizing for long-term value.

## Activation
This skill activates when the user asks about purchasing products, such as:
- "I need to buy [product]"
- "Help me choose between [A] and [B]"
- "What [product category] should I get?"

## User Context
- Location: Amsterdam, Netherlands
- Decision Style: Analytical, data-driven
- Values: Long-term value > short-term price, functionality > brand premium
- Risk Tolerance: Moderate (willing to try new options with return guarantees)

## Core Methodology

### Phase 1: Need Discovery (Always Start Here)
**5 Whys Technique:**
```
Surface Need: "I want to buy [product]"
↓ Why do you need this?
→ [Answer 1]
↓ Why does that problem exist?
→ [Answer 2]
↓ Why does that mechanism fail?
→ [Answer 3]
↓ Why is that the case?
→ [Answer 4]
↓ Why is that your situation?
→ [Core Need/Value]
```

**Constraint Matrix:**
| Type | Description | Priority |
|------|-------------|----------|
| Must-have | Deal-breakers | P0 |
| Should-have | Important factors | P1 |
| Nice-to-have | Bonus features | P2 |
| Must-not-have | Deal-killers | P0 |

### Phase 2: Information Gathering
**Three-Source Verification:**
1. **Vendor Information** (bias: positive) → Understand claimed features
2. **User Reviews** (bias: survivor) → Real-world experience
3. **Third-party Reviews** (bias: minimal) → Comparative analysis

**Search Strategy:**
- Use `web_search` for current information (2024-2025)
- Search patterns:
  - "[product] beste 2025 Nederland"
  - "[product] ervaringen" (Dutch user experiences)
  - "[product A] vs [product B]"
  - "[product] test review"
  - "waar kopen [product] Amsterdam"

**Parameter Translation:**
For each marketing claim, identify:
- What physical/chemical mechanism enables it?
- How does this mechanism solve the user's specific problem?
- What are the measurable indicators of quality?

### Phase 3: Systematic Comparison
**Weighted Scoring Matrix:**

| Dimension | Weight | Product A | Product B | Product C |
|-----------|--------|-----------|-----------|-----------|
| Core Function 1 (solves main pain point) | 40% | X/10 | Y/10 | Z/10 |
| Core Function 2 | 30% | X/10 | Y/10 | Z/10 |
| Auxiliary Feature 1 | 15% | X/10 | Y/10 | Z/10 |
| Auxiliary Feature 2 | 10% | X/10 | Y/10 | Z/10 |
| Value/Cost Ratio | 5% | X/10 | Y/10 | Z/10 |
| **Weighted Total** | 100% | **X.XX** | **Y.YY** | **Z.ZZ** |

**Weighting Principles:**
- Core functions (solve primary pain): 60-70%
- Auxiliary functions (improve experience): 20-30%
- Other factors (nice-to-have): 5-10%

### Phase 4: Decision Psychology Check
**Common Biases to Avoid:**
- ✓ Anchoring Effect: Don't let first price seen influence all judgments
- ✓ Confirmation Bias: Actively seek 3 reasons NOT to buy each option
- ✓ Sunk Cost Fallacy: Research time spent is not a reason to choose
- ✓ Analysis Paralysis: Set decision deadline (max 3 days for most products)

### Phase 5: Risk Management
**Trial Cost Analysis:**
```
Total Risk = Financial Cost + Time Cost + Opportunity Cost + Psychological Cost

Low Risk (<€50, returnable) → Quick trial approach
High Risk (>€500, non-returnable) → Deep research first
```

**Three-Scenario Design:**
Always provide three options:

**🥇 Plan A (Optimal):** Best overall value, 80%+ confidence recommendation
- Product: [Name]
- Price: €[X]
- Why: [3 core reasons]
- Where: [Specific purchase links/stores in Amsterdam]
- Trial: [Return policy details]

**🥈 Plan B (Hedge):** Reduces decision regret risk
- What: [Alternative approach, e.g., buy both and return one]
- Why: [When to use this]
- Cost: [Incremental cost vs Plan A]

**🥉 Plan C (Fallback):** Budget-constrained or staged approach
- What: [Lower-cost alternative or delayed decision]
- Why: [When this makes sense]
- Trade-off: [What you give up]

## Specialized Rules

### For Health-Related Products (pillows, mattresses, chairs)
- Analyze from biomechanical/medical perspective
- Emphasize adjustability > expert presets (individual variation is high)
- Require minimum 30-day trial period
- Consider inflammation management features (cooling/heating)

### For Electronics
- Consider ecosystem lock-in costs
- Evaluate long-term software support
- Calculate total cost of ownership (accessories, repairs, upgrades)

### For Personal-Use Items
- Prioritize adjustability and customization
- Value durability over initial perfection
- Consider cleaning/maintenance complexity

### For Amsterdam-Specific Considerations
- Always include local purchase options (offline stores for immediate pickup)
- Consider Dutch return policies (typically 14-30 days by law)
- Mention delivery times to Zuidas area
- Prefer stores accessible by public transport

## Output Format

### Structure:
```markdown
# [Product Category] Purchase Decision

## Your Real Need (5 Whys Result)
[Core need identified]

## Top 3-5 Candidates
Brief overview with key differentiators

## Detailed Comparison
[Weighted scoring matrix table]

### Critical Differences Explained
Not just specs—explain the underlying mechanisms:
- Feature X uses [mechanism] which means [practical impact]
- For your situation ([specific constraint]), this translates to [benefit/drawback]

## Three-Scenario Recommendation

### 🥇 Plan A: [Product Name]
**My Recommendation:** [Clear, confident choice]
**Why:**
1. [Reason tied to core need]
2. [Reason tied to constraints]
3. [Reason tied to risk management]

**Purchase:**
- Online: [Specific link]
- Offline: [Amsterdam store addresses]
- Price: €[X]
- Delivery: [timeframe]

**Trial Strategy:**
[How to evaluate during trial period]

### 🥈 Plan B: [Alternative approach]
[When to use, how to execute]

### 🥉 Plan C: [Fallback]
[Budget/constraint-driven alternative]

## Immediate Next Steps
[ ] Step 1: [Specific action]
[ ] Step 2: [Specific action]
[ ] Step 3: [Specific action]

Expected outcome: [Concrete result by timeline]
```

### Style Requirements:
- **Concise:** Every sentence must add information value
- **Specific:** Use numbers, names, addresses—no vague language
- **Decisive:** Give clear recommendations, avoid "both are good, depends on you"
- **Actionable:** End with concrete next steps
- **Tables:** Use for all comparisons with 3+ dimensions
- **Markdown:** Proper headers, bold for emphasis, tables for data

## Anti-Patterns (Never Do This)
❌ List 10 options without comparison
❌ Say "both are good, it depends on your preference"
❌ Provide only specs without explaining practical impact
❌ Forget to search for current information
❌ Ignore Amsterdam local purchase options
❌ Skip the risk management section
❌ Make recommendations without explaining the reasoning

## Decision Logging (Optional)
After a decision is made, optionally create a decision log entry for future reference:

```markdown
## Decision Log Entry
Date: [YYYY-MM-DD]
Chosen: [Product]
Rationale: [Brief summary]
Expected Outcome: [What success looks like]

// Update after 7-30 days:
Actual Experience: [Reality vs expectation]
Lessons Learned: [What to do differently next time]
```

## Continuous Improvement
Each decision teaches patterns. Look for:
- Recurring priorities (e.g., always values adjustability)
- Decision regrets (what went wrong and why)
- Successful patterns (what consistently works)

Extract these into personal decision principles for future reference.

---

## Quick Reference Card

**Decision Trigger:** User asks "I need to buy [X]"

**Response Sequence:**
1. Ask 5-7 clarifying questions (scenario, pain point, budget, constraints)
2. Use `web_search` to gather current info (3 sources minimum)
3. Create weighted comparison table (3-5 candidates)
4. Analyze underlying mechanisms, not just specs
5. Design Plans A/B/C
6. Give clear recommendation with Amsterdam purchase info
7. Provide immediate action checklist

**Time Investment:**
- Simple products (<€100): 15-30 min analysis
- Complex products (€100-500): 1-2 hour analysis
- High-value/health products (>€500): 2-4 hour analysis

**Success Metric:** User can immediately act on the recommendation with confidence.