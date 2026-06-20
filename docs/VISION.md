\# VISION.md



\# NEVIS LONG-TERM VISION



\## What Is NEVIS?



NEVIS (New Vision Integrated System) is not intended to be another CAD application.



NEVIS is not intended to become a simplified version of Revit, Rebro, or AutoCAD.



NEVIS is intended to become an engineering design, coordination, and construction validation platform focused on Japanese building services systems.



The primary objective is not drawing.



The primary objective is preventing engineering and construction mistakes before work begins on site.



\---



\# Ultimate Mission



The final mission of NEVIS is:



To help engineers detect design errors, coordination conflicts, constructability problems, and installation risks before construction starts.



Success is measured by:



\* fewer site modifications

\* fewer clashes

\* fewer installation errors

\* fewer redesigns

\* fewer construction delays



Not by drawing appearance alone.



\---



\# Engineering Domains



NEVIS must eventually support the following systems.



\## Drainage Systems (排水)



\* 汚水

\* 雑排水

\* 雨水

\* 通気

\* ドレン排水



\---



\## Water Supply Systems (給水)



\* Cold Water

\* Hot Water

\* Circulation Water

\* Pressure Systems



\---



\## Fire Protection Systems (消火)



\* 消火栓

\* 屋内消火栓

\* 屋外消火栓

\* スプリンクラー

\* 連結送水管

\* 泡消火設備

\* 消防水槽

\* Fire Water Tanks

\* Fire Pumps



Each fire protection system may require its own engineering rules.



\---



\## HVAC Systems



\* Drain Pipes

\* Refrigerant Pipes

\* Air Ducts

\* Ventilation Ducts

\* Exhaust Systems



\---



\## Infrastructure Systems



\* Underground Pipes

\* External Utility Networks

\* Pit Piping

\* Buried Pipes

\* Site Drainage

\* Stormwater Systems



\---



\# Building Types



NEVIS should not be limited to apartments.



Target projects include:



\* Apartments

\* Condominiums

\* Houses

\* Schools

\* Factories

\* Warehouses

\* Hospitals

\* Hotels

\* Commercial Buildings

\* Technical Basements

\* Utility Buildings

\* Industrial Facilities



\---



\# Spatial Understanding



NEVIS must evolve beyond 2D drafting.



The future model should understand:



\## Level 1



2D Plan View



X,Y coordinates



\---



\## Level 2



Engineering Elevation Model



X,Y,Z coordinates



Pipe elevations



Floor elevations



Beam elevations



Ceiling elevations



\---



\## Level 3



Constructability Model



The system should understand:



\* above slab

\* below slab

\* above ceiling

\* inside pit

\* underground

\* vertical risers

\* floor penetrations

\* wall penetrations



without requiring full BIM complexity.



\---



\# Core Engineering Data



Every pipe should eventually contain:



\* Start Point

\* End Point

\* Start Elevation

\* End Elevation

\* Slope

\* Length

\* Material

\* System Type



\---



Every fitting should eventually contain:



\* 3D Position

\* Orientation

\* Elevation

\* Connection Information



\---



\# Structural Model



NEVIS should eventually support simplified structural elements:



\* Slab

\* Beam

\* Column

\* Wall

\* Opening

\* Sleeve

\* Shaft



Simple engineering geometry is preferred.



Full BIM geometry is not required.



\---



\# Clash Detection



One of the most important future objectives.



NEVIS should eventually detect:



\## Pipe vs Pipe



Pipe collision.



\---



\## Pipe vs Beam



Pipe crossing beam.



\---



\## Pipe vs Slab



Pipe crossing slab.



\---



\## Pipe vs Column



Pipe collision with column.



\---



\## Pipe vs Wall



Pipe collision with wall.



\---



\## Pipe vs Duct



MEP coordination conflict.



\---



\## Pipe vs Cable Tray



Electrical coordination conflict.



\---



\## Pipe vs Equipment



Installation conflict.



\---



\# Engineering Validation



NEVIS should eventually validate:



\## Pipe Slope



Incorrect slope.



Insufficient slope.



Excessive slope.



Reverse slope.



\---



\## Pipe Elevation



Incorrect elevation.



Insufficient clearance.



Impossible installation.



\---



\## Sleeve Validation



Incorrect sleeve position.



Incorrect sleeve elevation.



Missing sleeve.



\---



\## Floor Opening Validation



Incorrect opening position.



Insufficient opening size.



Opening conflicts.



\---



\## Maintenance Validation



Insufficient maintenance access.



Insufficient service space.



Insufficient inspection space.



\---



\# Water Tank Validation



Future support:



\* Rainwater Tanks

\* Fire Water Tanks

\* Storage Tanks



Validation examples:



\* volume check

\* capacity check

\* regulation check



\---



\# Drawing Generation



The future system should generate:



\* Plan Views

\* Section Views

\* Longitudinal Sections

\* Cross Sections

\* Installation Diagrams



from a single engineering model.



\---



\# Design Philosophy



NEVIS must think like a site engineer.



Not like a CAD operator.



Not like a BIM modeler.



The central question should always be:



"Can this be built correctly on site?"



\# Multilingual Product Vision



NEVIS must support multilingual operation.



Initial target languages:



\- Japanese

\- Vietnamese



Japanese is the primary engineering language because the target workflow follows Japanese construction and MEP practice.



Vietnamese is required because the project owner, development team, and many future users may work in Vietnamese.



The software should allow switching language from a global setting.



Future languages may be added later.



Important:



Multilingual support is not only a UI translation issue.



It is an architectural requirement.



Engineering logic must not depend on display language.



\---





\# Development Priority



Priority order:



1\. Engineering Correctness

2\. Constructability

3\. Clash Prevention

4\. Elevation Accuracy

5\. Material Accuracy

6\. Drawing Accuracy

7\. Performance

8\. UI Convenience



Never reverse this order.



\---



\# Long-Term Rule



Every major design decision should be evaluated against this vision.



When multiple implementation options exist:



Choose the option that moves NEVIS closer to becoming an engineering coordination and construction validation platform.



Even if that option requires more work initially.



Important:



The ultimate goal of NEVIS is already defined.



Future development should move toward this vision.



Do not redefine the product direction.



When uncertain, ask how a proposed change contributes to the final vision.

\# Legacy Drawing Digitization



One of the long-term goals of NEVIS is converting existing engineering drawings into editable engineering models.



Many projects start from:



\- PDF drawings

\- scanned drawings

\- image-based drawings

\- legacy CAD exports



The objective is not perfect CAD conversion.



The objective is extracting engineering information.



Future workflow:



PDF/Image

→ Recognition

→ Pipe Centerlines

→ Network Reconstruction

→ Preliminary BOM

→ User Verification

→ Final Engineering Model



The system should eventually recognize:



\- pipe centerlines

\- pipe sizes

\- fittings

\- equipment

\- walls

\- beams

\- columns

\- symbols

\- text annotations



Priority:



1\. Pipe centerlines

2\. Pipe sizes

3\. Network reconstruction

4\. Preliminary BOM

5\. Structural elements

\# Long-Term Goal #2



\## Engineering Drawing Digitization



One of the long-term goals of NEVIS is the ability to convert existing engineering drawings into editable engineering models.



Many real projects do not start from a clean CAD model.



Instead, engineers often receive:



\* PDF drawings

\* scanned drawings

\* image-based drawings

\* printed drawings

\* old CAD exports

\* incomplete documentation



Recreating these drawings manually is time-consuming and error-prone.



NEVIS should eventually assist engineers by extracting engineering information directly from these documents.



\---



\## Objective



The objective is NOT perfect CAD conversion.



The objective is recovering engineering information.



The system should focus on:



\* pipe centerlines

\* pipe sizes

\* pipe routes

\* fittings

\* equipment

\* engineering relationships



rather than visual appearance.



\---



\## Future Workflow



PDF / Image



↓



Drawing Recognition



↓



Centerline Extraction



↓



Network Reconstruction



↓



Preliminary Material Takeoff



↓



User Verification



↓



Final Engineering Model



\---



\## Recognition Priorities



The system should gradually learn to recognize:



\### Priority 1



Pipe centerlines.



This is the most important information.



Without centerlines there is no engineering network.



\---



\### Priority 2



Pipe sizes.



Examples:



\* VP50

\* VP65

\* VP75

\* HIVP40

\* STPG80A



\---



\### Priority 3



Pipe direction and flow relationships.



Examples:



\* main pipe

\* branch pipe

\* riser pipe



\---



\### Priority 4



Fittings.



Examples:



\* LT

\* Y

\* DT

\* DL

\* LL

\* IN

\* 集合管



\---



\### Priority 5



Equipment and fixtures.



Examples:



\* floor drain

\* cleanout

\* sanitary fixtures

\* pumps

\* tanks



\---



\### Priority 6



Structural elements.



Examples:



\* wall

\* slab

\* beam

\* column

\* shaft



\---



\## Preliminary Material Takeoff



After reconstruction, NEVIS should be able to generate a preliminary BOM.



Example:



\* pipe lengths

\* fitting quantities

\* equipment counts



The BOM does not need to be perfect.



Its purpose is to provide an initial estimate for engineering review.



\---



\## User Verification



Human verification remains mandatory.



The engineer must always have final control.



The software should assist engineers, not replace them.



\---



\## Data Model Requirement



All recognized information should be converted into the same internal model used by manually created projects.



Regardless of the source:



\* user drawing

\* DXF

\* PDF

\* scanned image

\* AI recognition



the result should become:



\* Nodes

\* Edges

\* Pipes

\* Fittings

\* Equipment



inside the NEVIS network model.



\---



\## Engineering Priority



The goal is not visual accuracy.



The goal is engineering usefulness.



A rough but correct engineering network is more valuable than a visually perfect drawing that cannot be analyzed.



\---



\## Future Benefit



This capability should eventually allow:



\* rapid project digitization

\* renovation projects

\* existing building surveys

\* material estimation from PDF drawings

\* engineering analysis of legacy drawings

\* automatic conversion from drawing to engineering model



with minimal manual work.

