# KNOWN_RULES.md

# NEVIS BUSINESS RULES

This document contains business rules that MUST NOT be broken.

These rules have been accumulated through actual Japanese drainage design workflows.

Any new development must preserve these behaviors.

# Language Independence Rule

Business logic must not depend on display text.

Do not use Japanese or Vietnamese UI labels as logic keys.

Use stable internal identifiers for engineering objects.

Example:

Internal ID:

COLLECTION_FITTING

Display text:

Japanese:
集合管

Vietnamese:
Ống gom

---

Internal ID:

START_BRANCH

Display text:

Japanese:
頭側

Vietnamese:
Đầu nhánh

---

Internal ID:

END_BRANCH

Display text:

Japanese:
末端側

Vietnamese:
Cuối nhánh

All UI text should eventually come from a centralized language resource.

Avoid hardcoded UI text inside calculation logic, fitting logic, BOM logic, JWW export logic, or graph propagation logic.

The engineering model must remain language-independent.

---

# 1. BASIC CONCEPT

NEVIS is not a CAD drawing tool.

NEVIS is a pipe network system.

Every pipe segment belongs to a logical network.

All fitting decisions must be based on network rules.

Never update geometry only.

Always update:

* geometry
* fitting
* size
* material table

together.

---

# 2. PIPE NETWORK RULES

Network consists of:

Node:

* fitting
* endpoint
* equipment

Edge:

* pipe

Graph based structure.

Never treat drawing objects as isolated entities.

---

# 3. DRAINAGE SYSTEM RULES

Current stable target:

排水設備

Supported materials:

* DV
* VP
* VU
* HTVP
* 耐火VP
* TMP

---

# 4. DIRECTION RULES

Allowed directions only:

0°
45°
90°
135°
180°
225°
270°
315°

No arbitrary angle.

All fitting calculations must snap to nearest valid direction.

---

# 5. PIPE SIZE RULES

Pipe size propagation follows flow direction.

Upstream and downstream are important.

Never propagate sizes backward unless explicitly requested.

---

# 6. REDUCER (IN) RULES

Reducer is called:

IN

Example:

65x50

Meaning:

Upstream side:
65

Downstream side:
50

Rule:

Everything after reducer becomes 50.

Everything before reducer remains 65.

Reducer never changes upstream size.

---

# 7. BUSHING RULES

ブッシング

Used when reducer is inserted directly at fitting mouth.

Behavior:

* fitting remains original size
* downstream pipe becomes smaller
* no visible pipe piece between fitting and bushing

Material table must include:

65x50 ブッシング

---

# 8. FITTING OWNERSHIP RULE

Critical rule.

Each fitting owns its own branch size.

Example:

LT 65x50

Branch side:

50

Main side:

65

Changing one fitting must never modify branch sizes owned by another fitting.

---

# 9. PROPAGATION RULE

Changes only propagate downstream.

Never affect unrelated branches.

Example:

Main 65

Branch1 50
Branch2 50
Branch3 50
Branch4 50

Changing Branch2 to 65

Must not affect:

Branch3
Branch4

---

# 10. LT RULE

LT = Long Tee

Main flow:

P1 ↔ P3

Branch:

P2

Branch size follows LT settings only.

---

# 11. Y RULE

Y fitting

Main flow:

P1 ↔ P3

Branch:

P2

45 degree branch.

Must preserve flow direction.

---

# 12. DT RULE

DT fitting

Main:

P1 ↔ P3

Branch:

P2

Must use library orientation.

Never mirror randomly.

---

# 13. 45 DEGREE FITTING

45 fitting must:

* follow pipe direction
* preserve flow direction

When inserted:

trim connected pipes automatically.

---

# 14. SPECIAL EQUIPMENT RULE

Special equipment:

特

Can be inserted inside existing pipe.

Required actions:

1. Split host pipe
2. Insert equipment
3. Trim pipe
4. Reconnect network
5. Update BOM

All five actions are mandatory.

---

# 15. PIPE TRIMMING RULE

Pipe trimming must use fitting geometry.

Use fitting connection points:

P1
P2
P3

Never use arbitrary offsets.

No visible pipe may remain inside fitting body.

---

# 16. FIRE PROTECTION RULE

Default fire zone:

1200mm

Materials:

VP
HTVP
耐火VP
TMP

Fire boundary determined by outside diameter.

Not centerline.

Not fitting center.

---

# 17. MATERIAL TABLE RULE

Material table output:

Size
Name
Quantity
Unit

Example:

65 DV DL継手

---

# 18. MATERIAL MERGE RULE

These names are identical:

DL
DL_U
DL_D
DL_UP
DL_DOWN

All merged into:

DL継手

Same for:

LL
LL_U
LL_D

---

# 19. PIPE DISPLAY RULE

Pipe display names:

VP
VU
HTVP
耐火VP

Do not display DV on pipe.

DV belongs to fittings only.

---

# 20. COLLECTION FITTING RULE

集合管

Supported:

1-port

S_*

2-port straight

S_*_*

2-port right-angle

SV_*_*

3-port V type

SV_*_*_*

Display names must clearly distinguish these types.

Never merge all into one display name.

---

# 21. START OF BRANCH RULE

Allowed:

集合管

DL_D

LL_D

Special equipment

Only.

---

# 22. END OF BRANCH RULE

Allowed:

DL_U

LL_U

Pipe end

IN

Only.

---

# 23. DOUBLE CLICK RULE

Double-right-click on fitting:

Open replacement dialog.

Double-right-click on pipe:

Open special equipment insertion dialog.

---

# 24. REPLACEMENT RULE

Current fitting type determines available replacements.

Example:

Current = Y

Show:

Y variants only

plus:

Special Equipment folder

Do not show LT or DT.

---

# 25. LIBRARY RULE

Never invent sizes.

Only use sizes that physically exist inside library.

If library does not contain size:

Do not display it.

Do not generate it.

---

# 26. DETAIL VIEW RULE

Detailed view must display:

* actual fitting geometry
* actual trimming result
* actual library orientation

Preview and final output must be identical.

---

# 27. JWW EXPORT RULE

JWW output must match:

Screen display
Material table
Network model

All three must be consistent.

---

# 28. PERFORMANCE RULE

Future optimization must never sacrifice correctness.

Priority:

1. Correct fitting
2. Correct size
3. Correct BOM
4. Performance

Never reverse this order.

---

# 29. BACKWARD COMPATIBILITY

New versions must preserve:

Existing projects

Existing libraries

Existing BOM output

Existing JWW output

Backward compatibility is mandatory.

---

# 30. GOLDEN RULE

If a feature improves UI but changes engineering behavior:

Reject it.

Engineering correctness is always higher priority than UI convenience.
