---
name: penetration-testing
description: Penetration testing of code using owasp zap
arguments:
  - name: port
    description: Port of the application to scan
    type: number
    required: true
---

# OWASP ZAP Agent Skill

## Overview

This skill enables an AI agent to run OWASP ZAP for penetration testing for frontend and backend.

## Purpose

- Run OWASP ZAP for penetration testing
- To find vulnerabilities in the application especially OWASP Top 10 vulnerabilities

## Inputs / Prerequisites

- Docker must be installed on the system. If not present then run below command.

## When to use this skill

Use this skill when you are going to scan the application for vulnerabilities.

## How to use this skill

```bash
docker run --rm zaproxy/zap-stable zap-full-scan.py -t http://localhost:{{port}}
```

## Output

Please put the output of the owasp zap scan in the owasp_zap_report.txt file.