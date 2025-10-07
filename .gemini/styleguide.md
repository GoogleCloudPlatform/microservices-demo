# Instructions for Code Review and Suggestions

## CRITICAL EXCLUSION RULE

**You MUST completely ignore any code blocks or sections that contain the following exact string:**
`// @generatedCode`
`# @generatedCode`
`@gGeneratedCode`
`@generatedCode`
`@generatedcode`
`// Generated Code`
`/* Generated Code */`
`# Generated Code`
`/* @generatedCode */`

**Reason:** This code is automatically generated and should not be reviewed, commented on, or modified by the agent. If you see this annotation, you must skip to the next section of user-written code.
