\# NEVIS\_HISTORY.md



\# NEVIS DEVELOPMENT HISTORY



This document records critical lessons learned during development.



Purpose:



\* Prevent old bugs from returning.

\* Preserve engineering knowledge.

\* Explain why certain rules exist.

\* Help future developers understand hidden constraints.



\---



LESSON #1

PIPES ARE NOT DRAWING OBJECTS

\-----------------------------



Early versions treated pipes and fittings as graphic objects.



Result:



Changing one fitting often caused unrelated objects to change.



Conclusion:



NEVIS must be treated as a network graph.



Every fitting and pipe belongs to a connected system.



Never process objects independently.



\---



LESSON #2

FITTING OWNERSHIP IS CRITICAL

\-----------------------------



Major bug discovered in Version 2.02.



Scenario:



Main pipe:

65



Branches:



65x50

65x50

65x50

65x50



Changing Branch #2:



65x50 → 65x65



caused:



Branch #3 → 65

Branch #4 → 65



even though they were unrelated.



Root Cause:



Size propagation crossed fitting ownership boundaries.



Solution:



Each fitting owns its own branch size.



A fitting may affect:



\* itself

\* downstream pipe



A fitting may never affect:



\* sibling fittings

\* unrelated branches



Permanent Rule:



Never propagate across ownership boundaries.



\---



LESSON #3

DOWNSTREAM PROPAGATION ONLY

\---------------------------



Several bugs were caused by propagation in both directions.



Correct behavior:



Reducer:



65x50



Before reducer:



65



After reducer:



50



Changing downstream must not change upstream.



Permanent Rule:



Propagation follows flow direction only.



\---



LESSON #4

DOUBLE CLICK AND APPLY MUST USE SAME ENGINE

\-------------------------------------------



Historical bug:



Apply button produced correct result.



Double-right-click replacement produced different result.



Reason:



Two different update algorithms existed.



Solution:



Unified update engine.



Permanent Rule:



All fitting modifications must use the same update engine.



\---



LESSON #5

IN REDUCER ORIENTATION

\----------------------



Historical bug:



IN 65x50 occasionally reversed.



Result:



Wrong material table.



Wrong network sizes.



Wrong JWW output.



Permanent Rule:



Large side = upstream.



Small side = downstream.



Never reverse automatically.



\---



LESSON #6

PREVIEW MUST MATCH REAL OUTPUT

\------------------------------



Several bugs occurred because:



Preview:



A



Output:



B



Users lost trust.



Permanent Rule:



Preview and actual drawing must use the same geometry data.



No duplicate calculation paths.



\---



LESSON #7

PIPE TRIMMING IS HARDER THAN DRAWING

\------------------------------------



Many trimming algorithms were tested.



Problems:



\* Pipe visible inside fitting.

\* Over-trimming.

\* Under-trimming.



Final conclusion:



Trim must use library connection points.



P1

P2

P3



Never trim using arbitrary distance values.



\---



LESSON #8

SPECIAL EQUIPMENT INSERTION

\---------------------------



Early implementation:



Inserted object visually only.



Result:



Network corruption.



Material table mismatch.



Final process:



1\. Split host pipe.

2\. Insert equipment.

3\. Trim pipe.

4\. Reconnect graph.

5\. Update material table.



All five steps are required.



\---



LESSON #9

FIRE PROTECTION BOUNDARY

\------------------------



Historical bug:



Pipe converted to fire-resistant material too early.



Cause:



Boundary calculated from centerline.



Correct approach:



Use actual outside diameter.



Permanent Rule:



Fire boundary must be calculated from physical pipe edge.



\---



LESSON #10

MATERIAL TABLE IS A FIRST-CLASS FEATURE

\---------------------------------------



Many CAD systems treat BOM as secondary.



NEVIS does not.



Material table is equally important as drawing output.



Permanent Rule:



Every geometry change must immediately update BOM.



\---



LESSON #11

LIBRARY IS THE SOURCE OF TRUTH

\------------------------------



Historical issue:



System generated sizes that did not exist.



Result:



Impossible fittings.



Permanent Rule:



If library does not contain the size:



Do not display it.



Do not generate it.



Do not export it.



\---



LESSON #12

JWW OUTPUT MUST MATCH SCREEN

\----------------------------



Historical issue:



Screen and JWW differed.



Users trusted neither.



Permanent Rule:



Screen

BOM

JWW



must always match.



If one differs, it is considered a bug.



\---



LESSON #13

DRAINAGE WORKFLOW IS PRIORITY

\-----------------------------



NEVIS originally aimed to support:



\* Drainage

\* Water Supply

\* Fire Fighting

\* Ventilation



Reality:



Drainage became the most mature system.



Permanent Rule:



Never sacrifice drainage stability to accelerate other systems.



Drainage is the core product.



\---



LESSON #14

PERFORMANCE OPTIMIZATION CAN CREATE HIDDEN BUGS

\-----------------------------------------------



Many bugs appeared after optimization attempts.



Examples:



\* partial refresh missing updates

\* cached library showing wrong fitting

\* delayed BOM updates



Permanent Rule:



Correctness first.



Performance second.



\---



LESSON #15

REAL JAPANESE WORKFLOW IS MORE IMPORTANT THAN SOFTWARE THEORY

\-------------------------------------------------------------



Several "clean" programming solutions were rejected.



Reason:



They violated actual Japanese plumbing practice.



Permanent Rule:



If engineering practice and software theory conflict:



Follow engineering practice.



NEVIS is an engineering tool first.



\---



\## VERSION 2.02 STATUS



Stable areas:



\* Drainage network

\* LT

\* Y

\* DT

\* DL

\* LL

\* IN

\* Collection fittings

\* Fire protection zones

\* Material table

\* JWW export



Known future focus:



\* Performance optimization

\* Library caching

\* Local redraw

\* Advanced fitting intelligence

\* AI-assisted routing



\---



\## FINAL RULE



When uncertain:



Preserve existing behavior.



A slower correct result is better than a fast wrong result.



