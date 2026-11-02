using System.Net.Http.Json;
using System.Text.Json.Serialization;

namespace FabPilot.Web.Services;

/// <summary>Typed HTTP client for the FabPilot FastAPI backend.</summary>
public sealed class BackendClient(HttpClient http)
{
    public async Task<Readiness?> GetReadinessAsync(CancellationToken ct = default)
    {
        // /health/ready returns 503 with a body when degraded, so read the body either way.
        using var resp = await http.GetAsync("health/ready", ct);
        return await resp.Content.ReadFromJsonAsync<Readiness>(ct);
    }
}

public sealed record Readiness(
    string Status,
    string Version,
    Dictionary<string, CheckResult> Checks,
    LlmInfo Llm);

public sealed record CheckResult(
    bool Ok,
    [property: JsonPropertyName("latency_ms")] double? LatencyMs,
    string? Error);

public sealed record LlmInfo(
    string Provider,
    [property: JsonPropertyName("base_url")] string BaseUrl,
    string Model);
