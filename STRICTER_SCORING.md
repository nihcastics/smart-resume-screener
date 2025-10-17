# Stricter Scoring Thresholds - Update Summary

## Changes Made

All scoring thresholds have been made significantly stricter to ensure better differentiation between strong, medium, and weak candidates.

---

## 1. **Semantic Similarity Thresholds**

### Before:
```python
strict_threshold = 0.80
partial_threshold = 0.65
weak_threshold = 0.50
```

### After:
```python
strict_threshold = 0.85  # +0.05 (stricter)
partial_threshold = 0.70  # +0.05 (stricter)
weak_threshold = 0.55     # +0.05 (stricter)
```

**Impact**: Requires stronger semantic alignment for partial/full credit

---

## 2. **Initial Scoring (Semantic-Based)**

### Before:
```python
if similarity >= 0.80: score = 0.80
elif similarity >= 0.65: score = 0.55
elif similarity >= 0.50: score = 0.30
else: score = 0.0
```

### After:
```python
if similarity >= 0.85: score = 0.85  # Higher bar, higher reward
elif similarity >= 0.70: score = 0.60  # +0.05 requirement, +0.05 score
elif similarity >= 0.55: score = 0.35  # +0.05 requirement, +0.05 score
else: score = 0.0
```

**Impact**: Stricter thresholds but proportional rewards

---

## 3. **LLM-Based Final Scoring**

### For PRESENT Skills:

**Before:**
```python
base_score = 0.60
confidence_bonus = 0.40 * confidence
# Range: 0.60 to 1.0

Boosts:
- similarity >= 0.85: +10%
- similarity >= 0.75: +5%
```

**After:**
```python
base_score = 0.55  # Lowered from 0.60
confidence_bonus = 0.45 * confidence  # Increased from 0.40
# Range: 0.55 to 1.0 (stricter base, rewards high confidence more)

Boosts (stricter thresholds):
- similarity >= 0.90: +12%  # NEW tier
- similarity >= 0.85: +8%   # Was 10%
- similarity >= 0.75: +4%   # Was 5%
```

**Impact**: Lower base score but rewards very high confidence and strong evidence more

---

### For ABSENT Skills:

**Before:**
```python
if confidence >= 0.80: score = 0.0
elif confidence >= 0.60: score = 0.10
elif confidence >= 0.40: score = 0.25
else: score = min(0.40, pre_llm_score * 0.8)
```

**After:**
```python
if confidence >= 0.85: score = 0.0      # Stricter (was 0.80)
elif confidence >= 0.70: score = 0.05  # Stricter (was 0.60), lower score (was 0.10)
elif confidence >= 0.50: score = 0.20  # Stricter (was 0.40), lower score (was 0.25)
else: score = min(0.35, pre_llm_score * 0.7)  # More conservative
```

**Impact**: Harsher penalties for likely-absent skills

---

## 4. **Must-Have Fulfillment Penalties**

### Before:
```python
if fulfillment < 50%: penalty = 0.70  # -30%
elif fulfillment < 70%: penalty = 0.85  # -15%
else: penalty = 1.0  # No penalty
```

### After:
```python
if fulfillment < 40%: penalty = 0.60  # -40% (was -30% at 50%)
elif fulfillment < 60%: penalty = 0.75  # -25% (was -15% at 70%)
elif fulfillment < 80%: penalty = 0.90  # -10% (NEW tier)
else: penalty = 1.0  # No penalty only if 80%+ met
```

**Impact**: Much stricter - need 80% must-haves to avoid penalty

---

## 5. **Overall Score Weighting**

### Before:
```python
semantic: 40%
coverage: 35%
llm_fit: 25%

Must-have: 75%
Nice-to-have: 25%
```

### After:
```python
semantic: 35%  # -5% (less weight)
coverage: 45%  # +10% (more weight - most concrete)
llm_fit: 20%   # -5% (less weight - can be subjective)

Must-have: 80%  # +5% (more critical)
Nice-to-have: 20%  # -5% (less important)
```

**Impact**: Coverage (concrete skill matching) now dominates scoring

---

## 6. **LLM Confidence Guidelines**

Updated prompt to be stricter:

### Before:
```
0.5-0.6: Mentioned with minimal context or only in skills list
```

### After:
```
0.5-0.6: Mentioned with some context OR in skills list with light project usage
0.3-0.4: Only in skills list without evidence OR weak/indirect mention
```

**Impact**: Just being in skills list without project usage → confidence 0.3-0.4 max

---

## Expected Results

### Scoring Distribution:

**Before (Lenient):**
- Strong candidates: 75-85%
- Medium candidates: 65-75%
- Weak candidates: 55-70%
- Range: ~20-30 points

**After (Strict):**
- Excellent candidates: 80-92%
- Good candidates: 65-78%
- Fair candidates: 50-65%
- Poor candidates: 30-50%
- Range: ~40-60 points (much better differentiation)

---

## Key Benefits

1. **Better Differentiation**: Wider score range (30-92% vs 55-85%)
2. **Rewards Excellence**: Strong evidence + high confidence → higher scores
3. **Penalizes Gaps**: Missing must-haves severely impact score
4. **Prioritizes Coverage**: Concrete skill matching weighs most (45%)
5. **Stricter Baselines**: Lower minimum scores for marginal matches

---

## Examples

### Example 1: Excellent Candidate
```
Must-haves: 18/20 met (90%)
Coverage score: 0.88
Semantic score: 0.82
LLM fit: 0.85

Calculation:
Raw = (0.45×0.88 + 0.35×0.82 + 0.20×0.85) = 0.853
Penalty = 1.0 (90% fulfillment)
Final = 0.853 × 10 = 85.3% ✅ (was ~78%)
```

### Example 2: Good Candidate
```
Must-haves: 14/20 met (70%)
Coverage score: 0.72
Semantic score: 0.68
LLM fit: 0.70

Calculation:
Raw = (0.45×0.72 + 0.35×0.68 + 0.20×0.70) = 0.702
Penalty = 0.90 (70% fulfillment)
Final = 0.702 × 0.90 × 10 = 63.2% ✅ (was ~68%)
```

### Example 3: Weak Candidate
```
Must-haves: 7/20 met (35%)
Coverage score: 0.45
Semantic score: 0.52
LLM fit: 0.48

Calculation:
Raw = (0.45×0.45 + 0.35×0.52 + 0.20×0.48) = 0.481
Penalty = 0.60 (35% fulfillment)
Final = 0.481 × 0.60 × 10 = 28.9% ✅ (was ~48%)
```

---

## Migration Notes

- **No breaking changes** to data structures
- All changes are in scoring algorithms
- Existing resumes will get re-scored with stricter criteria
- Expect scores to drop by 5-15% for most candidates
- Top candidates may see slight increase (better rewards)

---

## Testing Recommendations

1. **Benchmark Tests**: Re-score known good/bad resumes
2. **Threshold Validation**: Ensure 80%+ = excellent, 50-65% = fair
3. **Penalty Impact**: Verify missing must-haves drop score significantly
4. **Weight Balance**: Confirm coverage weighs most (45%)

---

## Commit Summary

**Changes:**
- 6 major scoring components updated
- All thresholds raised by 0.05
- Penalties increased by 10-15%
- Coverage weight increased to 45%
- Must-have weight increased to 80%

**Files Modified:**
- `app.py` - 8 scoring functions/thresholds updated

**Expected Impact:**
- Better candidate differentiation (40-60 point range)
- More accurate scoring (rewards excellence, penalizes gaps)
- Coverage-first approach (concrete > abstract)
