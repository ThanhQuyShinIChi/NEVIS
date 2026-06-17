NEVIS 2.03 PROJECT CONTEXT

Project Name



NEVIS (New Vision Integrated System)



MEP CAD System chuyên cho thị trường Nhật Bản.



Mục tiêu:



Thiết kế hệ thống cấp thoát nước

Tự động sinh fitting

Tự động thống kê vật tư

Xuất bản vẽ JWW

Thay thế một phần thao tác thủ công của Jw\_cad và Rebro



Ngôn ngữ:



Python 3

PySide6

Current Version

NEVIS 2.02



Trạng thái:



Hoạt động ổn định

Đã hoàn thiện phần lớn hệ thống thoát nước

Đã xử lý nhiều lỗi propagation kích thước và fitting



Dung lượng:



File chính:

Nevis\_no\_ui.py



Quy mô:



\~15.000+ dòng code

Core Philosophy



NEVIS không phải phần mềm CAD vẽ đường.



NEVIS là:



Pipe Network Generator



Người dùng chỉ định:



tuyến ống

thiết bị

hướng thoát



Hệ thống tự:



chọn fitting

chọn kích thước

cập nhật toàn bộ mạng lưới



giống tư duy của:



Rebro

Revit MEP



không phải AutoCAD.



Supported Systems

排水 (Drainage)

Materials

DV

VP

VU

HTVP

耐火VP

TMP

Fittings

DL

LL

LT

DT

Y

45

IN

CO

集合管

脚部

給水 (Water Supply)



Partial support



HIVP

HTVP

AW

VB

VD

消火



Partial support



STPG

風管



Experimental



Spiral Duct

Drawing Rules

8 Direction System



Only allow:



0°

45°

90°

135°

180°

225°

270°

315°



No arbitrary angles.



Pipe Graphics

VP



1 dashed line

2 solid lines



TMP



2 dashed lines

1 solid line



JWW Export



Current exporter:



TXT based



Main commands:



\#hc

\#1

\#10#



Features:



Pipe export

Fitting export

Material export

Layer export

Material Table



Current Output:



Size	Name	Qty	Unit



Example:



| 65 | DV DL継手 | 4 | 個 |



Rules:



U/D removed

Up/Down removed

Same fitting merged

Major Systems Completed In 2.02

1\. Auto Fitting Engine



Automatically generate:



LT

Y

DT

45

DL

LL



based on geometry.



2\. Size Propagation Engine



Automatically update downstream sizes.



Rules:



downstream follows reducer

unrelated branches must never change



Solved several critical bugs.



3\. Special Equipment System



Supports:



IN

特



Insertion into existing pipe.



Automatic:



trim

reconnect

update BOM

4\. Fire Protection Zone Engine



Supports:



1200mm fire zone



Automatic:



fire pipe conversion

fire fitting conversion



Materials:



VP

HTVP

耐火VP

TMP

5\. Library Learning System



Current state:



Library normalization implemented.



Supports:



JSON

TXT



Purpose:



future AI fitting generation



Location:



Library/

Learning/

Critical Bugs Solved During 2.02

Propagation Bug



Problem:



Changing one fitting changed unrelated downstream branches.



Example:



65 main



4 branches



65x50

65x50

65x50

65x50



Changing branch #2 to 65x65 caused:



branch #3

branch #4



to become 65.



Fixed.



Reducer Direction Bug



Problem:



IN 65x50 sometimes reversed.



Fixed.



Double Click Replacement Bug



Problem:



Double-click replacement used different logic from Apply button.



Fixed.



Current rule:



Both use same update engine.



Fire Boundary Conversion Bug



Problem:



Pipe converted incorrectly across fire boundary.



Fixed.



Current Architecture



Main components:



Data Model



Node



fitting

equipment

endpoint



Edge



pipe segment



Graph based.



Rendering Engine



QGraphicsScene



Responsibilities:



pipe drawing

fitting drawing

labels

selection

Library Engine



Responsibilities:



library scan

JSON parsing

preview generation

BOM Engine



Responsibilities:



quantity count

merge same parts

export table

Export Engine



Responsibilities:



JWW TXT generation

Goals For 2.03

Performance



Current issue:



Many operations redraw entire scene.



Target:



Local update only.



Expected:



5\~20x faster.



Library Cache



Current:



Parse JSON repeatedly.



Target:



Memory cache.



Expected:



Instant preview.



Smart Fitting Replacement



Target:



Real-time replacement suggestions.



Similar to:



Rebro

Revit MEP

Auto Route Optimization



Future AI route suggestion.



Advanced Equipment Library



Support:



manufacturer libraries

custom libraries

AI-generated fittings

Important Constraints



NEVER break:



Existing drainage workflow.

Existing BOM output.

Existing JWW export.

Existing library format.



Backward compatibility is mandatory.



Entry Point



Main file:



Nevis\_no\_ui.py



Main class:



MainWindow



Startup:



main()

Development Priority For 2.03



Priority 1



Performance optimization



Priority 2



Library cache



Priority 3



Local redraw



Priority 4



Advanced fitting intelligence



Priority 5



Future AI-assisted routing

