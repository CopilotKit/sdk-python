# list

curl -X POST http://localhost:8000/copilotkit/actions/list \
-H "Content-Type: application/json" \
-d '{"properties": {}}' | jq

# execute action

curl -X POST http://localhost:8000/copilotkit/actions/execute -H "Content-Type: application/json" -d '{"name": "greet", "parameters": {"name": "Markus"}}' | jq

# execute agent

curl -X POST http://localhost:8000/copilotkit/actions/execute -H "Content-Type: application/json" -d '{"name": "askUser", "parameters": {"copilot": {}}}' | jq

# continue executing agent

curl -X POST http://localhost:8000/copilotkit/actions/execute -H "Content-Type: application/json" -d '{"name": "askUser", "agentThreadId": "33785f49-5916-42f6-88e1-8c13fe203bae", "agentState": {"name":"","copilot":{"ask":{"question":"What is your name?","answer":"Markus"}}}}' | jq
