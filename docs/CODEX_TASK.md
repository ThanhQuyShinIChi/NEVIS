\# CODEX\_TASK.md



\# NEVIS 2.03 DEVELOPMENT TASK



\## Purpose



You are joining an existing software project called NEVIS.



NEVIS is a Japanese MEP CAD system focused primarily on plumbing and drainage design.



The project has evolved through many iterations and contains significant business knowledge accumulated from real engineering projects.



Your role is not to redesign the system.



Your role is to improve and extend the system while preserving existing behavior.



\---



\# Documents To Read First



Before reading source code, read:



1\. docs/PROJECT\_CONTEXT.md

2\. docs/KNOWN\_RULES.md

3\. docs/NEVIS\_HISTORY.md



These documents contain engineering knowledge that may not be obvious from the code.



Source code alone is not sufficient to understand the project.



\---



\# Current Situation



Current version:



NEVIS 2.02



Status:



Functional and stable.



Core drainage workflow is already working.



Main issue:



Performance degradation caused by project growth.



The system currently contains:



\* Large drawing scenes

\* Large fitting libraries

\* Repeated JSON parsing

\* Frequent full-scene redraws

\* Frequent BOM recalculation



The software is correct but slower than desired.



\---



\# Main Objective For Version 2.03



Improve performance while preserving behavior.



Expected outcome:



\* Faster UI

\* Faster fitting replacement

\* Faster library browsing

\* Faster drawing refresh

\* Faster BOM updates



without changing engineering behavior.



\---



\# What Must NOT Be Changed



Do not change:



\* Drainage business rules

\* Fitting selection rules

\* Size propagation rules

\* Material table rules

\* JWW export behavior

\* Existing library format



Backward compatibility is mandatory.



Existing projects must continue to work.



\---



\# Development Philosophy



Priority order:



1\. Engineering correctness

2\. Network correctness

3\. Material table correctness

4\. JWW export correctness

5\. Performance

6\. UI improvements



Never reverse this order.



\---



\# Phase 1 - Analysis Only



Before writing code:



Analyze:



\* application architecture

\* module structure

\* bottlenecks

\* technical debt

\* high-cost functions

\* repeated operations



Provide:



1\. Architecture Analysis

2\. Bottleneck Analysis

3\. Risk Analysis

4\. Optimization Roadmap



Do not modify code.



Wait for approval.



\---



\# Phase 2 - Performance Investigation



Identify:



\## Rendering Bottlenecks



Examples:



\* scene.clear()

\* full redraw

\* unnecessary repaint



Measure impact.



\---



\## Library Bottlenecks



Examples:



\* repeated folder scans

\* repeated JSON parsing

\* repeated geometry generation



Measure impact.



\---



\## BOM Bottlenecks



Examples:



\* recalculation after every change

\* full table rebuild



Measure impact.



\---



\## Preview Bottlenecks



Examples:



\* regenerating fitting geometry repeatedly

\* rebuilding previews unnecessarily



Measure impact.



\---



\# Phase 3 - Optimization Proposal



For each optimization:



Explain:



\* problem

\* root cause

\* proposed solution

\* affected modules

\* expected gain

\* risks



Example:



Problem:

Full redraw after selecting one fitting.



Root Cause:

draw\_model() rebuilds entire scene.



Proposal:

Local update mechanism.



Expected Gain:

5x faster selection.



Risk:

Potential stale graphics.



\---



\# Communication Requirements



Provide all explanations in Vietnamese.



Technical terms may remain in English when necessary.



Examples:



Cache

Graph

Render

Node

Edge

Scene



But all explanations should be understandable to a Vietnamese user.



\---



\# Change Approval Process



Before implementing any major modification:



Explain:



1\. What will change

2\. Why it is needed

3\. Risks

4\. Expected benefits



Then wait for approval.



Do not assume approval.



\---



\# Refactoring Rules



Refactoring is allowed only when:



\* behavior remains unchanged

\* outputs remain unchanged



The following outputs must remain consistent:



\* screen display

\* material table

\* JWW export



If behavior changes:



document it first.



\---



\# Code Quality Goals



Version 2.03 should improve:



\* readability

\* maintainability

\* performance



without sacrificing stability.



\---



\# Golden Rule



When multiple solutions are possible:



Choose the solution that preserves existing behavior.



A slower correct result is always better than a faster incorrect result.



