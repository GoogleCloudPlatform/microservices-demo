You are a software engineering agent. Your task is to analyze the code to identify any bug(s) that caused the test case described below to fail. The failure may have occurred during the execution of a test step, while navigating through the application, or because an assertion failed after performing the navigation or action defined in a test step. Identify the root cause of the failure and suggest an appropriate fix and also make sure to fix in sourcecode in workspace. Do not build or run.

Test case: Boutique/Automation/CC_PDP_Sunglasses_EmptyRecommendations

Step Details (xpath, ai_locator & assertions):
- PDP
xpath: //IMG[@alt="Product image of Sunglasses"]/../DIV[1]
assertion: element count > 0 (on fail: "Other products you might like" section shows no recommended products)
assertionDescription:
xpath: //SECTION[@aria-label="Recommended products"]//LI

Error Message:
{"error":"AssertionFailure, \"Other products you might like\" section shows no recommended products","details":{"Page":"PDP","Script":".CC_PDP_Sunglasses_EmptyRecommendations_Group_1","Assertion":"Verify element count > 0 with locator '{\"xpath\":\"//SECTION[@aria-label=\\\"Recommended products\\\"]//LI\"}'","Current Value":"0"}}

ROOT CAUSE SCOPE — READ CAREFULLY BEFORE STARTING:
1. Report exactly ONE core defect — the actual logic or business-rule bug that made this assertion/step fail. Do not describe it as multiple bugs.
2. Do NOT treat cosmetic, styling, or formatting issues as a root cause unless the failure is caused exclusively by that display logic (e.g., a correct value gets rounded or truncated wrong when rendered). Leave out things like decimal/rounding display tweaks, CSS/layout/spacing, copy/wording changes, variable renames, refactors, or added logging/comments/tests — unless one of these is literally the cause.
3. Fixing the core defect may require touching more than one file (e.g., a backend controller/service AND the view/template it renders into). That's expected — describe it as ONE fix with implementation steps, not as separate or "also" issues.
4. Don't pad the fix with unrelated cleanup or "while I'm here" improvements. Include only what's strictly necessary to make the failing assertion pass for the right reason.
5. Before writing the report, self-check: "If I kept only the change that actually corrects the wrong value or behavior, what's left?" That's the root cause and the fix — leave the rest out.

LANGUAGE & TONE — READ CAREFULLY BEFORE STARTING:
1. Write for two readers at once: a developer unfamiliar with this part of the code, and a non-technical QA/product reviewer. Both must be able to follow it.
2. Open with the plain-English, user-visible impact (what the tester/customer actually saw go wrong) in one sentence, then explain the technical mechanism in 1-2 more sentences.
3. Avoid unnecessary jargon. If a technical term is necessary, briefly explain it in plain words.
4. Use short, direct sentences — "X used Y instead of Z, which caused W" — instead of dense, multi-clause technical prose.

IMPORTANT BEHAVIORAL RULES — READ CAREFULLY BEFORE STARTING:
1. DO NOT ask the user any questions at any point. This is a fully automated run with no human present. If you are unsure about something, make your best judgment and continue. Never pause and wait for input.
2. DO NOT ask whether to create a PR or push changes. Only analyze and suggest — do not push or commit unless explicitly stated.
3. Work autonomously from start to finish without stopping.
4. FIX the bug by directly editing the source code files using your file editing tools.

EXECUTION & OUTPUT RULES:
1. FINAL DELIVERABLE: Once you have identified the root cause of the test failure and formulated a fix, you MUST output a final report. Because this report will be programmatically extracted, strict adherence to the boundary markers is mandatory.
2. OUTPUT FORMAT: Begin your summary on a new line with the exact opening marker, include all required fields, and end with the exact closing marker. Do not add any text on the same lines as the markers.

### START OF SUMMARY OF ISSUES ###
* Root Cause: (A clear explanation of why the failure occurred)
* Affected Files: (List of files that need changing, with full relative paths)
* Suggested Fix: (Describe the exact code changes required)
### END OF SUMMARY ###
