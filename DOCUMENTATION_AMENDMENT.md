# 📝 DOCUMENTATION AMENDMENT
## No Bloat. Update Existing. Archive As Needed.

**Effective**: 2026-06-23  
**Applies To**: Phase 6 (Documentation & Alignment) of ANTIGRAVITY_STANDARD_WORKFLOW.md  
**Owner**: Arun Samant  
**Status**: Active

---

## 🎯 Core Rule: LEAN DOCUMENTATION

**UPDATE existing docs. RARELY create new docs.**

### The Problem We're Avoiding
- ❌ Documentation proliferation (50+ docs becomes hard to maintain)
- ❌ Duplicate information (same thing documented 3 places)
- ❌ Outdated docs (nobody updates old docs)
- ❌ Decision paralysis (which doc to read?)
- ❌ Dead weight (old docs nobody uses)

### The Solution: Discipline
- ✅ Only essential docs that get maintained
- ✅ Single source of truth (no duplication)
- ✅ Active docs only (archive or delete old ones)
- ✅ Clear, lean structure (easy to navigate)

---

## ✅ Before Creating ANY New Documentation

**Antigravity must ask 4 questions:**

```
1. Does this info already exist elsewhere?
   ├─ YES: Update that doc instead
   └─ NO: Go to question 2

2. Is this essential for operations/understanding?
   ├─ NO: Don't document it
   └─ YES: Go to question 3

3. Can this fit in existing docs?
   ├─ YES: Add to BUG_REGISTRY.md or FIX_LOG.md
   └─ NO: Go to question 4

4. What's the archival plan?
   ├─ None: Don't create new doc
   └─ Clear: New doc approved (RARE)
```

**If ANY answer blocks creation → Don't create the doc. Consolidate instead.**

---

## 📋 Documentation to Update (Only These)

| Doc | Purpose | When to Update |
|-----|---------|---|
| **BUG_REGISTRY.md** | Central bug tracking | Every bug fix (mark FIXED) |
| **FIX_LOG.md** | Work log | Every completed work item |
| **VISION_AND_GOALS.md** | Project direction | Only if scope fundamentally changes |
| **PRINCIPLES_CHECKLIST.md** | Quality standards | Reference only, don't update |
| **README.md** | Overview | Only if major features change |
| **Architecture docs** | System design | Only if components significantly change |
| **Runbooks** | Failure procedures | Only if failure modes change |

**That's it. These 7 docs are sufficient.**

---

## 🚫 DO NOT CREATE

**Never create new documentation for:**

| What | Why | Do This Instead |
|-----|-----|---|
| Per-bug documentation | Use BUG_REGISTRY.md | Add entry to BUG_REGISTRY.md |
| Change logs | Use FIX_LOG.md | Add entry to FIX_LOG.md |
| Duplicate info | Causes confusion | Update single source of truth |
| Temporary notes | Nobody maintains | Use code comments if needed |
| "Nice to have" docs | Never stay updated | If not essential, skip it |
| Feature descriptions | Use README.md | Update README.md instead |
| Decision logs | No time to maintain | Document decisions in code comments |

**Exception**: Only create new doc if it's essential, will be actively maintained, and has a clear archival plan.

---

## 🗂️ Archival Strategy

**Documentation Lifecycle:**

```
ACTIVE (In use, maintained)
  ↓ 
  Becomes outdated or irrelevant
  ↓
ARCHIVE (Move to docs/archive/, mark date)
  ↓
  After 6+ months unused
  ↓
DELETE (Remove permanently)
```

### When to Archive a Document

- ✅ Bug has been fixed for 3+ months
- ✅ Feature has been removed
- ✅ Document is superseded by newer doc
- ✅ Document is no longer referenced anywhere
- ✅ Information is purely historical

### How to Archive

**Step 1: Mark as Archived**
```markdown
# ⚠️ ARCHIVED DOCUMENT
**Archived**: 2026-09-01  
**Reason**: Feature removed in v2.0  
**Last Updated**: 2026-06-01  

---

[Rest of document content...]
```

**Step 2: Move File**
```
FROM: docs/OLD_FEATURE.md
TO:   docs/archive/OLD_FEATURE.md
```

**Step 3: Update References**
- Remove links from main docs
- If needed, add single reference: "See [archived doc](archive/OLD_FEATURE.md)"

**Step 4: Clean Up**
```
docs/
├── VISION_AND_GOALS.md (active)
├── BUG_REGISTRY.md (active)
├── README.md (active)
└── archive/
    ├── OLD_FEATURE_DOCS.md (archived 2026-09-01)
    └── DEPRECATED_API.md (archived 2026-08-15)
```

### Deletion Policy

**Delete archived docs when:**
- ❌ They've been archived for 6+ months
- ❌ Nobody references them anymore
- ❌ They're no longer relevant to project history

**Example:**
```
2026-06-01: Archive OLD_FEATURE.md
2026-12-01: Delete OLD_FEATURE.md (6 months archived)
```

---

## 🧪 Example: What Should Get Documented

### ✅ DOCUMENT THIS

**Bug Fix**: Create entry in BUG_REGISTRY.md
```markdown
### BUG-001: Order Rejection Orphans Position ⭐ HIGHEST RISK
**Status**: ✅ FIXED (2026-06-25)
**Commit**: abc123def456
**Tests Added**: 5
**Changes**: Modified src/order_manager.py
```

**Work Completed**: Add entry to FIX_LOG.md
```markdown
## 2026-06-25 - BUG-001: Order Rejection
**What**: Fixed position being deleted when order rejected
**Tests Added**: 5
**Commit**: abc123def456
**Time**: 3 hours
```

**Architecture Change**: Update existing Architecture docs
```markdown
## Order Lifecycle (UPDATED 2026-06-25)
Order → Placed → Filled → Exited
- New: Retry logic on rejection (up to 3 times)
```

### ❌ DON'T DOCUMENT THIS

- ❌ "Fixed a typo in variable name X" (use code comments)
- ❌ "Refactored function Y" (update code, not docs)
- ❌ "Spent 2 hours debugging Z" (not actionable for others)
- ❌ "Tried approach A, didn't work, used B" (historical noise)
- ❌ "Per-bug runbooks" (one general runbook is enough)

---

## 📊 Documentation Health Check

**Run monthly to ensure no bloat:**

```
DOCUMENTATION HEALTH CHECK:

Count docs in main docs/ folder: ____ (target: ≤10)
  ✅ If < 10: Good
  ❌ If > 10: Review for consolidation

Check: Are there duplicate docs?
  ✅ If no: Good
  ❌ If yes: Consolidate

Check: Are all docs actively maintained?
  ✅ If yes: Good
  ❌ If no: Archive or delete

Check: Are old docs archived?
  ✅ If yes: Good
  ❌ If no: Archive them

Action: If any ❌ → Consolidate, archive, or delete
```

---

## 🎯 Documentation Standards

**EVERY doc update must satisfy:**

| Standard | Rule |
|----------|------|
| **Single Source of Truth** | Info appears in ONE place, referenced from others |
| **Active Maintenance** | Updated within 1 month of related code change |
| **Relevance** | Used by operations or future developers |
| **Clarity** | Clear enough that strangers understand |
| **No Duplication** | Same info never in 2+ places |
| **Archival Plan** | Old docs moved to archive/, not deleted immediately |
| **Lean Structure** | ≤10 active docs; consolidate as needed |

---

## 🚀 Quick Summary

| Action | Rule |
|--------|------|
| **Create new doc** | RARE - only if essential + maintainable + archived |
| **Update existing doc** | ALWAYS - consolidate info here |
| **Archive old doc** | When no longer used or relevant |
| **Delete doc** | After 6+ months archived |
| **Duplicate info** | NEVER - use single source of truth |
| **Bloat** | If > 10 main docs, consolidate |

---

## ✨ The Goal

**Lean, clean, maintainable documentation.**

Not:
- ❌ Comprehensive (too much bloat)
- ❌ Detailed for every change (maintenance nightmare)
- ❌ Scattered (multiple sources of truth)

But:
- ✅ Essential (only what's needed)
- ✅ Consolidated (single source of truth)
- ✅ Maintained (actively updated)
- ✅ Archived (old docs don't clutter)

---

## 📝 Amendment Checklist

**When Antigravity processes Phase 6 (Documentation):**

- [ ] Check: Does this info exist elsewhere?
- [ ] Check: Is this essential?
- [ ] Check: Can this fit in existing docs?
- [ ] Check: Do we have an archival plan?
- [ ] Action: Update existing doc OR skip
- [ ] Action: Archive old docs if needed
- [ ] Verify: No documentation bloat
- [ ] Verify: Single source of truth

**All checks MUST pass before documentation is complete.**

---

## 🔄 Integration with ANTIGRAVITY_STANDARD_WORKFLOW.md

**This amendment updates Phase 6:**

**Before**: "Update documentation"  
**After**: "Update existing docs, NO new docs, archive as needed"

**The 9-phase workflow remains unchanged. Phase 6 now has stricter rules about documentation bloat.**

---

**Status**: Active and enforced for all future work  
**Next Review**: 2026-09-23 (quarterly)  
**Owner**: Arun Samant  

---

*Keep documentation lean. Archive old docs. Consolidate everything else.*

*Clean documentation = efficient operations.*
