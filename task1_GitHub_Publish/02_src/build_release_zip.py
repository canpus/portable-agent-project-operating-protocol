#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task-local helper: build the layered release zip (GlobalRules + ProjectRules, 4 files).

Usage: python build_release_zip.py
Output: <task_root>/06_outputs/portable-agent-project-operating-protocol-v0.1.0.zip
"""
import hashlib
import os
import zipfile

BASE = r"F:\AgenticCoding\Portable_Agent_Project_Framework"
OUT = r"F:\AgenticCoding\_agent_tasks\20260819\task1_GitHub_Publish\06_outputs\portable-agent-project-operating-protocol-v0.1.0.zip"

FILES = [
    ("GlobalRules/AGENTS.md", os.path.join(BASE, "GlobalRules", "AGENTS.md")),
    ("ProjectRules/AGENTS.md", os.path.join(BASE, "ProjectRules", "AGENTS.md")),
    ("ProjectRules/SCHEMA.md", os.path.join(BASE, "ProjectRules", "SCHEMA.md")),
    ("ProjectRules/TASK_STATE_MACHINE.md", os.path.join(BASE, "ProjectRules", "TASK_STATE_MACHINE.md")),
]

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
    for arcname, src in FILES:
        zf.write(src, arcname)

print("== zip entries ==")
with zipfile.ZipFile(OUT) as zf:
    for info in zf.infolist():
        digest = hashlib.sha256(zf.read(info.filename)).hexdigest()[:16]
        print(f"{info.filename}\t{info.file_size} bytes\tsha256[:16]={digest}")
print("zip written:", OUT)
