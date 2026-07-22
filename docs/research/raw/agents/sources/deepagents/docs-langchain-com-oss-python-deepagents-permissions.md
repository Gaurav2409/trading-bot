---
url: https://docs.langchain.com/oss/python/deepagents/permissions
title: "Permissions - Docs by LangChain"
fetched_at: 2026-07-22T18:45:48.991704+00:00
source_id: deepagents-harness
method: static
status: FETCHED
word_count: 1496
---

Control which files and directories an agent can read or write to using declarative permission rules. Pass a list of rules to
permissions=
and the agent’s built-in filesystem tools respect them.
Permissions require
deepagents>=0.5.2
.
Permissions only apply to the built-in filesystem tools (
ls
,
read_file
,
glob
,
grep
,
write_file
,
edit_file
,
delete
). Custom tools and MCP tools that access the filesystem are not covered. Permissions also do not apply to
sandbox backends
, which support arbitrary command execution via the
execute
tool.
Use
permissions
when you need
path-based allow/deny rules
on the built-in filesystem tools. Use
backend policy hooks
when you need custom validation logic (rate limiting, audit logging, content inspection) or need to control custom tools.
​
Basic usage
Pass a list of
FilesystemPermission
rules to
create_deep_agent
. Rules are evaluated in declaration order. The first matching rule wins. If no rule matches, the operation is allowed.
from
deepagents
import
FilesystemPermission
,
create_deep_agent
# Read-only agent: deny all writes
agent
=
create_deep_agent
(
model
=
model
,
backend
=
backend
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
],
)
​
Rule structure
Each
FilesystemPermission
has three fields:
Field
Type
Description
operations
list["read" | "write"]
Operations this rule applies to.
"read"
covers
ls
,
read_file
,
glob
,
grep
.
"write"
covers
write_file
,
edit_file
,
delete
.
paths
list[str]
Glob patterns for matching file paths (e.g.,
["/workspace/**"]
). Supports
**
for recursive matching and
{a,b}
for alternation.
mode
"allow" | "deny" | "interrupt"
Whether to allow, deny, or pause for human approval on matching operations. Defaults to
"allow"
. See
Pause for human approval
.
Rules use first-match-wins evaluation: the first rule whose
operations
and
paths
match the current call determines the outcome. If no rule matches, the call is
allowed
(permissive default).
​
Pause for human approval
The
"interrupt"
mode requires
deepagents>=0.6.8
.
Set
mode="interrupt"
to pause for human approval instead of allowing or denying a matching operation outright. When the agent calls a built-in write tool (
write_file
,
edit_file
,
delete
) on a path that matches an interrupt-mode rule,
create_deep_agent
raises a human-in-the-loop interrupt rather than running the tool, and a reviewer can approve, edit, or reject the call.
from
deepagents
import
FilesystemPermission
,
create_deep_agent
from
langgraph
.
checkpoint
.
memory
import
InMemorySaver
agent
=
create_deep_agent
(
model
=
model
,
permissions
=
[
# Pause for approval before writing anything under /secrets.
FilesystemPermission
(
operations
=
[
"write"
],
paths
=
[
"/secrets/**"
],
mode
=
"interrupt"
,
),
],
# Interrupt mode requires a checkpointer to pause and resume.
checkpointer
=
InMemorySaver
(),
)
Interrupt-mode rules are wired into the agent’s human-in-the-loop middleware automatically and merge with any
interrupt_on
you pass, so you handle and resume them the same way as tool-call interrupts. See
Human-in-the-loop
for the resume flow.
Deleting a directory is all-or-nothing:
delete
checks the
write
permission on the target and every descendant path, and refuses the entire operation if any of them is denied, rather than removing part of the tree.
Anchor interrupt patterns with a literal leading segment (for example,
/secrets/**
or
/projects/*/secrets/**
). Bulk tools (
ls
,
glob
,
grep
, and
delete
on a directory) fire the interrupt when their search subtree could overlap the rule’s anchored prefix, so a fully unanchored pattern like
/**/secrets
conservatively over-fires.
​
Examples
​
Isolate to a workspace directory
Allow reads and writes only under
/workspace/
and deny everything else:
agent
=
create_deep_agent
(
model
=
model
,
backend
=
backend
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/**"
],
mode
=
"allow"
,
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
],
)
​
Protect specific files
agent
=
create_deep_agent
(
model
=
model
,
backend
=
backend
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/.env"
,
"/workspace/examples/**"
],
mode
=
"deny"
,
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/**"
],
mode
=
"allow"
,
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
],
)
​
Read-only memory
Allow the agent to read memory files but prevent it from modifying them. This is useful for organization-wide policies or shared knowledge bases that should only be updated by application code. See
read-only vs writable memory
for more context.
from
deepagents
.
backends
import
CompositeBackend
,
StateBackend
,
StoreBackend
agent
=
create_deep_agent
(
model
=
model
,
backend
=
CompositeBackend
(
default
=
StateBackend
(),
routes
=
{
"/memories/"
:
StoreBackend
(
namespace
=
lambda
rt
:
(
rt
.
server_info
.
user
.
identity
,),
),
"/policies/"
:
StoreBackend
(
namespace
=
lambda
rt
:
(
rt
.
context
.
org_id
,),
),
},
),
permissions
=
[
FilesystemPermission
(
operations
=
[
"write"
],
paths
=
[
"/memories/**"
,
"/policies/**"
],
mode
=
"deny"
,
),
],
)
​
Deny all access
Block all reads and writes. This is a restrictive baseline you can layer more specific allow rules on top of:
agent
=
create_deep_agent
(
model
=
model
,
backend
=
backend
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
],
)
​
Rule ordering
Because of first-match-wins, rule order matters. Place more specific rules before broader ones:
# Correct: deny .env, allow workspace, deny everything else
correct_permissions
=
[
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/.env"
],
mode
=
"deny"
,
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/**"
],
mode
=
"allow"
,
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
]
# Bug: /workspace/** matches .env first, so the deny never triggers
incorrect_permissions
=
[
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/**"
],
mode
=
"allow"
,
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/.env"
],
mode
=
"deny"
,
# never reached
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
]
​
Subagent permissions
Subagents
inherit the parent agent’s permissions by default. To give a subagent different permissions, set the
permissions
field in its spec. This
replaces
the parent’s rules entirely.
agent
=
create_deep_agent
(
model
=
model
,
backend
=
backend
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/workspace/**"
],
mode
=
"allow"
,
),
FilesystemPermission
(
operations
=
[
"read"
,
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
],
subagents
=
[
{
"name"
:
"auditor"
,
"description"
:
"Read-only code reviewer"
,
"system_prompt"
:
"Review the code for issues."
,
"permissions"
:
[
FilesystemPermission
(
operations
=
[
"write"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
FilesystemPermission
(
operations
=
[
"read"
],
paths
=
[
"/workspace/**"
],
mode
=
"allow"
,
),
FilesystemPermission
(
operations
=
[
"read"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
],
}
],
)
​
Composite backends
When using a
CompositeBackend
with a sandbox default, every permission path must be scoped under a known route prefix. Sandboxes support arbitrary command execution, so path-based restrictions alone cannot prevent filesystem access through shell commands. Scoping permissions to route-specific
backends
avoids this conflict.
from
deepagents
.
backends
import
CompositeBackend
composite
=
CompositeBackend
(
default
=
sandbox
,
routes
=
{
"/memories/"
:
memories_backend
},
)
# Works: permissions are scoped to the /memories/ route
agent
=
create_deep_agent
(
model
=
model
,
backend
=
composite
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"write"
],
paths
=
[
"/memories/**"
],
mode
=
"deny"
,
),
],
)
Permissions that include paths outside any route raise
NotImplementedError
:
# Raises NotImplementedError: /workspace/** hits the sandbox default
try
:
create_deep_agent
(
model
=
model
,
backend
=
composite
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"write"
],
paths
=
[
"/workspace/**"
],
mode
=
"deny"
,
),
],
)
except
NotImplementedError
:
pass
# Also raises: /** covers both routes and the default
try
:
create_deep_agent
(
model
=
model
,
backend
=
composite
,
permissions
=
[
FilesystemPermission
(
operations
=
[
"read"
],
paths
=
[
"/**"
],
mode
=
"deny"
,
),
],
)
except
NotImplementedError
:
pass
Connect these docs
to Claude, VSCode, and more via MCP for real-time answers.
Edit this page on GitHub
or
file an issue
.
Was this page helpful?
Yes
No
Backends
Previous
Multimodal inputs and outputs
Next
⌘
I
