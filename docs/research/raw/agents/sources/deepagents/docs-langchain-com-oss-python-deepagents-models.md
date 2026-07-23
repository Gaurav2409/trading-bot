---
url: https://docs.langchain.com/oss/python/deepagents/models
title: "Models - Docs by LangChain"
fetched_at: 2026-07-22T18:45:46.668008+00:00
source_id: deepagents-harness
method: static
status: FETCHED
word_count: 899
---

Deep Agents work with any
LangChain chat model
that supports
tool calling
.
​
Supported models
Specify models in
provider:model
format (for example,
google_genai:gemini-3.5-flash
,
openai:gpt-5.4
, or
anthropic:claude-sonnet-4-6
). The provider prefix selects the LangChain integration, and everything after the colon is passed through to that provider as the model identifier. For valid provider strings, see the
model_provider
parameter of
init_chat_model
. For provider-specific configuration, see
chat model integrations
.
The model identifier must match the format expected by the provider. Some providers use simple names like
gpt-5.5
; others use namespaced IDs or deployment paths like
zai-org/GLM-5.2
, so the full Deep Agents string would be
baseten:zai-org/GLM-5.2
. Check the provider’s model catalog or integration docs for the current identifiers.
​
Suggested models
These models perform well on the
Deep Agents eval suite
, which tests basic agent operations. Passing these evals is necessary but not sufficient for strong performance on longer, more complex tasks.
Provider
Models
Google
gemini-3.1-pro-preview
,
gemini-3.5-flash
OpenAI
gpt-5.5
,
gpt-5.4
Anthropic
claude-opus-4-8
,
claude-opus-4-7
,
claude-opus-4-6
Open-weight
GLM-5.2
,
Kimi-K2.7 Code
,
MiniMax-M3
Open-weight models are available through providers like
Baseten
,
Fireworks
,
OpenRouter
, and
Ollama
.
​
Model evaluations
The
Deep Agents eval suite
tests popular models:
Model
Overall
File Ops
Retrieval
Tool Use
Memory
Conversation
Summarization
google_genai:gemini-3.5-flash
82%
100%
100%
90%
54%
38%
80%
openai:gpt-5.4
18%
100%
100%
18%
51%
38%
100%
openai:gpt-5.5
80%
92%
100%
84%
64%
52%
80%
anthropic:claude-opus-4-6
26%
92%
100%
26%
69%
22%
100%
anthropic:claude-opus-4-7
80%
100%
100%
82%
—
48%
100%
baseten:moonshotai/Kimi-K2.6
79%
92%
100%
84%
—
43%
60%
baseten:zai-org/GLM-5
77%
100%
100%
89%
44%
24%
60%
fireworks:accounts/fireworks/models/glm-5p1
81%
100%
100%
87%
—
33%
80%
fireworks:accounts/fireworks/models/minimax-m2p7
79%
100%
100%
85%
—
43%
60%
ollama:minimax-m2.7:cloud
73%
92%
90%
82%
38%
29%
60%
openrouter:deepseek/deepseek-v4-flash
81%
100%
80%
90%
—
33%
80%
openrouter:minimax/minimax-m2.7
80%
92%
100%
89%
—
43%
60%
openrouter:z-ai/glm-5.1
89%
92%
100%
89%
—
33%
80%
For more information, see the
Eval runs
.
​
Configure model parameters
Pass a model string to
create_deep_agent
in
provider:model
format, or pass a configured model instance for full control. Under the hood, model strings are resolved via
init_chat_model
.
To configure model-specific parameters, use
init_chat_model
or instantiate a provider model class directly:
init_chat_model
Provider package
from
langchain
.
chat_models
import
init_chat_model
from
deepagents
import
create_deep_agent
model
=
init_chat_model
(
model
=
"google_genai:gemini-3.5-flash"
,
thinking_level
=
"medium"
,
)
agent
=
create_deep_agent
(
model
=
model
)
from
langchain_google_genai
import
ChatGoogleGenerativeAI
from
deepagents
import
create_deep_agent
model
=
ChatGoogleGenerativeAI
(
model
=
"gemini-3.1-pro-preview"
,
thinking_level
=
"medium"
,
)
agent
=
create_deep_agent
(
model
=
model
)
Available parameters vary by provider. See the
chat model integrations
page for provider-specific configuration options.
​
Provider profiles
A
ProviderProfile
packages initialization parameters that apply when you provide a
provider:model
string when creating the deep agent. It does not apply when you pass a preconfigured model with
init_chat_model
.
You can register at two levels, and both can coexist:
Provider level
— a bare provider key like
"openai"
applies to every model from the
openai
provider.
Model level
— a
provider:model
key like
"openai:gpt-5.4"
applies only to that specific model, and merges on top of any matching provider-level profile.
from
deepagents
import
ProviderProfile
,
register_provider_profile
# Provider-wide default: every openai model gets temperature=0.
register_provider_profile
(
"openai"
,
ProviderProfile
(
init_kwargs
=
{
"temperature"
:
0
}),
)
# Model-level override: gpt-5.5 additionally gets a specific reasoning effort.
# Inherits temperature=0 from the provider-level profile above.
register_provider_profile
(
"openai:gpt-5.5"
,
ProviderProfile
(
init_kwargs
=
{
"reasoning_effort"
:
"medium"
}),
)
See
Profiles
for the full field list, merge semantics, and plugin packaging.
For shaping how the
agent
behaves once the model is built, use a
harness profile
.
​
Select a model at runtime
If your application lets users choose a model (for example using a dropdown in the UI), use
middleware
to swap the model at runtime without rebuilding the agent.
Pass the user’s model selection through
runtime context
, then use a
wrap_model_call
middleware to override the model on each invocation using the
@wrap_model_call
decorator:
from
dataclasses
import
dataclass
from
typing
import
Callable
from
langchain
.
agents
.
middleware
import
ModelRequest
,
ModelResponse
,
wrap_model_call
from
langchain
.
chat_models
import
init_chat_model
from
deepagents
import
create_deep_agent
@dataclass
class
Context
:
model
:
str
@wrap_model_call
def
configurable_model
(
request
:
ModelRequest
,
handler
:
Callable
[[
ModelRequest
],
ModelResponse
],
)
->
ModelResponse
:
model_name
=
request
.
runtime
.
context
.
model
model
=
init_chat_model
(
model_name
)
return
handler
(
request
.
override
(
model
=
model
))
agent
=
create_deep_agent
(
model
=
"google_genai:gemini-3.5-flash"
,
middleware
=
[
configurable_model
],
context_schema
=
Context
,
)
# Invoke with the user's model selection
result
=
agent
.
invoke
(
{
"messages"
:
[{
"role"
:
"user"
,
"content"
:
"Hello!"
}]},
context
=
Context
(
model
=
"openai:gpt-5.5"
),
)
For more dynamic model patterns (for example routing based on conversation complexity or cost optimization), see
Dynamic model
in the LangChain agents guide.
​
Learn more
Models in LangChain
: chat model features including tool calling, structured output, and multimodality
Connect these docs
to Claude, VSCode, and more via MCP for real-time answers.
Edit this page on GitHub
or
file an issue
.
Was this page helpful?
Yes
No
Customize Deep Agents
Previous
Comparison with Claude Agent SDK
Next
⌘
I
