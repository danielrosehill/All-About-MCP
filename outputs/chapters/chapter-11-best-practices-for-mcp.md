## Chapter 11: Best Practices for MCP

The successful implementation of the Model Context Protocol (MCP) requires adherence to architectural standards that ensure security, reliability, and interoperability. While the core specification provides the mechanisms for communication between hosts and servers, it does not mandate specific design patterns for the internal logic of those components. This chapter establishes a comprehensive set of best practices for designing, deploying, and maintaining MCP integrations, focusing on enterprise-grade requirements and long-term ecosystem stability.

### Designing Robust MCP Servers

The foundation of a reliable MCP ecosystem lies in the quality of individual servers. A well-designed server separates concerns effectively, manages state predictably, and provides clear contracts to the host application.

#### Resource vs. Tool Abstraction

A common architectural error involves conflating Resources and Tools. While both expose capabilities to the Language Model (LLM), they serve distinct semantic purposes that influence how the model perceives and utilizes data.

*   **Resources** should be used for reading data. They represent context—files, database rows, API responses—that can be loaded into the prompt context window. Resources must be read-only and idempotent; reading a resource multiple times should not change the state of the system.
*   **Tools** should be used for performing actions. They represent executable functions that may have side effects, such as writing to a database, sending an API request, or triggering a deployment.

Strictly adhering to this separation allows the host application to cache resources aggressively while treating tool execution with necessary caution.

**Example: Separation of Concerns**

In a database integration, a direct SQL query should be exposed as a Tool because it carries execution risks. However, a specific, safe view of a table schema should be exposed as a Resource.

```python
# Improper Design: Exposing a read-operation as a Tool
# This prevents the host from pre-fetching or caching the data as context.
@mcp.tool()
async def get_table_schema(table_name: str) -> str:
    return db.query(f"DESCRIBE {table_name}")

# Proper Design: Exposing static/read-only data as a Resource
# This allows the host to treat the schema as context.
@mcp.resource("postgres://schema/{table_name}")
async def get_table_schema_resource(table_name: str) -> str:
    schema = await db.fetch_schema(table_name)
    return format_as_text(schema)
```

#### Schema Precision and Descriptions

The Model Context Protocol relies heavily on JSON Schema to define the structure of tool arguments and resource parameters. The quality of these schemas directly correlates to the performance of the LLM. Vague schemas lead to hallucinations or malformed requests.

Implementers must provide detailed descriptions for every field in the schema, not just the top-level function. The LLM uses these descriptions to understand semantic intent. Furthermore, using strict typing (e.g., enums rather than open-ended strings) significantly reduces error rates.

![Image: Diagram showing the flow of schema validation. An LLM generates a JSON payload, which passes through a Schema Validator gate before reaching the Tool logic. The validator rejects invalid types based on the MCP definition.](images/chapter-11-figure-1.jpg)
*Figure 11.1: Schema validation acts as the primary firewall between non-deterministic LLM output and deterministic code execution.*

### Security Implementation

Security in MCP is paramount, particularly because the protocol acts as a bridge between probabilistic AI models and deterministic systems with access to sensitive data. Chapter 3 covers the theoretical security landscape; this section details implementation hardening.

#### Input Validation and Sanitization

Standard schema validation ensures types are correct, but it does not ensure safety. All inputs received from an MCP host—effectively, inputs from an LLM—must be treated as untrusted user input.

1.  **Path Traversal Prevention:** When a tool accepts file paths, the server must normalize the path and verify it resolves within an allowed root directory before file access occurs.
2.  **Injection Defense:** For tools interacting with SQL databases or shell commands, parameterized queries and strict argument escaping are mandatory. Never concatenate LLM-generated strings directly into executable commands.

**Example: Secure Path Handling**

```python
import os
from pathlib import Path

ALLOWED_ROOT = Path("/var/data/safe_dir").resolve()

def read_safe_file(user_path: str) -> str:
    # Resolve the absolute path
    target_path = (ALLOWED_ROOT / user_path).resolve()

    # strict check: Is the target still inside the allowed root?
    if not str(target_path).startswith(str(ALLOWED_ROOT)):
        raise ValueError("Access denied: Path traversal attempt detected.")

    if not target_path.exists():
        raise FileNotFoundError("File does not exist.")

    return target_path.read_text()
```

#### Least Privilege and Scoping

MCP servers should run with the minimum necessary system permissions. If a server is designed to read logs, the underlying operating system process should not have write access to the filesystem.

In an enterprise environment, it is best practice to decouple the MCP server from the sensitive backend using a service account with scoped permissions. For example, a "Cloud Infrastructure MCP" should not use an Admin API key; instead, it should use a key restricted to the specific resource groups defined in the server's scope.

#### Transport Security

When deploying MCP over stdio (standard input/output), security relies on the host's operating system user permissions. However, when deploying over Server-Sent Events (SSE) or other network transports, standard web security practices apply.

*   **TLS is Mandatory:** Never expose an MCP server over plain HTTP.
*   **Authentication:** Implement authentication headers (e.g., Bearer tokens) to ensure only authorized hosts can connect to the server. The MCP specification allows for custom headers during the initialization handshake; these should be utilized for identity verification.

### Performance and Scalability

As agentic workflows grow complex, the latency introduced by MCP interactions becomes a bottleneck. Optimizing the performance of MCP servers ensures a responsive user experience.

#### Asynchronous Processing

The MCP protocol supports asynchronous request handling. Servers should implement all I/O-bound operations (database queries, network requests, file reads) asynchronously. Blocking the main event loop prevents the server from handling concurrent requests (e.g., processing a tool call while simultaneously serving a ping or a resource subscription update).

#### Payload Optimization

Large text payloads consume significant token budgets in LLMs and increase network latency.

*   **Truncation:** Tools returning large datasets (e.g., "read_logs") must implement default truncation or pagination. Returning 10MB of log data will likely overflow the context window of the host LLM.
*   **Summarization:** Where possible, offer tools that return metadata or summaries rather than raw data. A tool named `analyze_data` is often preferable to `download_data` followed by client-side analysis.

#### Caching Strategies

Resources that are computationally expensive to generate but change infrequently should be cached by the server. While the MCP protocol includes mechanisms for the host to cache resources, server-side caching reduces load on backend systems.

Additionally, servers should implement the `notifications/resources/updated` capability. Rather than forcing the host to poll for changes, the server should push a notification only when the underlying data changes.

![Image: A sequence diagram contrasting polling vs. subscription. The polling side shows high network traffic with redundant requests. The subscription side shows a single connection with updates pushed only upon state changes.](images/chapter-11-figure-2.jpg)
*Figure 11.2: Event-driven resource updates significantly reduce network overhead compared to polling architectures.*

### Enterprise Management and Governance

Managing a fleet of MCP servers in a corporate environment requires governance structures similar to microservices management.

#### Versioning and Compatibility

MCP servers must adhere to Semantic Versioning. Changes to tool schemas (e.g., renaming an argument or making an optional argument required) constitute breaking changes.

*   **Backward Compatibility:** When modifying a tool, prefer adding optional arguments over changing existing ones.
*   **Deprecation Notices:** Use the `description` field in the schema to mark tools as deprecated before removing them in future versions.
*   **Protocol Versioning:** Servers must check the `protocolVersion` sent by the client during the `initialize` handshake and degrade gracefully if the client does not support newer features.

#### Logging and Observability

Standard application logging is insufficient for MCP servers because the "user" is an AI. Logs must capture the *intent* and the *outcome* clearly to diagnose hallucinations vs. system errors.

Use the MCP `logging/message` notification capability to send structured logs back to the host. This allows the host application to display server-side logs to the user or developer within the main interface, providing a unified debugging experience.

**Example: Structured Logging via MCP**

```python
async def perform_critical_action(ctx, params):
    try:
        # Standard server-side log
        logger.info(f"Action started with params: {params}")

        # Notification to the MCP Host
        await ctx.send_logging_message(
            level="info",
            data=f"Server executing action on ID {params['id']}",
            logger="sys_admin_mcp"
        )
        result = run_process(params)
        return result
    except Exception as e:
        await ctx.send_logging_message(
            level="error",
            data=f"Operation failed: {str(e)}",
            logger="sys_admin_mcp"
        )
        raise
```

#### Configuration Management

Avoid hardcoding configuration values. MCP servers should accept configuration via environment variables or a config file loaded at startup. This enables the same server artifact to be deployed across Development, Staging, and Production environments without code modification.

For sensitive credentials (API keys, database passwords), use environment variables injection rather than command-line arguments, as command-line arguments are often visible in process listings.

### Contributing to the Ecosystem

A healthy MCP ecosystem relies on community standards and shared libraries. When releasing public MCP servers, developers should follow specific packaging and documentation guidelines to ensure broad compatibility.

#### Documentation Standards

Every public MCP server must include a `README.md` that addresses:

1.  **Transport Configuration:** Explicit commands to run the server via stdio (e.g., `npx -y server-name` or `docker run ...`).
2.  **Environment Variables:** A comprehensive list of required and optional environment variables.
3.  **Tool/Resource Manifest:** A high-level description of what tools and resources are exposed.
4.  **Security Scope:** A declaration of what the server accesses (internet, filesystem, etc.).

#### Interface Stability

Public servers should aim for interface stability. Frequent changes to tool names or parameter structures disrupt the prompts of users who have optimized their agent instructions for a specific version of the server. If a major refactor is necessary, release it as a separate server package or a major version bump, allowing users to pin their dependencies.

#### Error Handling Hierarchies

Standardize error reporting. When an MCP server encounters an error, it should map internal exceptions to standard JSON-RPC error codes where applicable (e.g., `-32602` for Invalid Params). For domain-specific errors, return clear, human-readable messages. The LLM reads these error messages to self-correct.

A message like "Error 500" is useless to an LLM. A message like "Error: The date format must be YYYY-MM-DD" allows the LLM to retry the request with the correct format immediately.

### Summary

Best practices for the Model Context Protocol revolve around treating the interface between the LLM and the system as a critical boundary. By rigorously separating Resources from Tools, enforcing strict schema validation, and adopting security-first input handling, developers can build servers that are safe and reliable. In enterprise contexts, observability, versioning, and performance optimization become the defining characteristics of a successful deployment. Adhering to these standards ensures that MCP integrations scale effectively and remain maintainable as the ecosystem evolves.