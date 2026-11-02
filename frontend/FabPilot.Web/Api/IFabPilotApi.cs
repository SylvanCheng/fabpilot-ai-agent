using FabPilot.Web.Api.Contracts;

namespace FabPilot.Web.Api;

/// <summary>
/// Everything the UI needs from the backend. Pages depend on this interface only, so they can be
/// tested with a fake and the transport (HTTP today, SSE for chat in P2) can change behind it.
/// </summary>
public interface IFabPilotApi
{
    /// <summary>Readiness report. Returned for both 200 (ok) and 503 (degraded).</summary>
    Task<Readiness> GetReadinessAsync(CancellationToken ct = default);

    Task<FabOverview> GetFabOverviewAsync(CancellationToken ct = default);
}

/// <summary>Raised for any backend failure; carries the problem details when the backend sent them.</summary>
public sealed class FabPilotApiException(string message, Problem? problem = null, Exception? inner = null)
    : Exception(message, inner)
{
    public Problem? Problem { get; } = problem;
}
