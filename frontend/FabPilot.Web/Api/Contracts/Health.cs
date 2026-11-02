using System.Text.Json;
using System.Text.Json.Serialization;

namespace FabPilot.Web.Api.Contracts;

// Mirrors components/schemas in contracts/openapi.json (ReadinessOut, CheckOut).

public sealed record Readiness(
    string Status,
    string Version,
    Dictionary<string, Check> Checks)
{
    public bool IsOk => Status == "ok";
}

public sealed record Check(
    bool Ok,
    [property: JsonPropertyName("latency_ms")] double? LatencyMs,
    string? Error,
    Dictionary<string, JsonElement>? Detail);
