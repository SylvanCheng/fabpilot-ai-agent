using System.Net;
using System.Net.Http.Json;
using FabPilot.Web.Api.Contracts;

namespace FabPilot.Web.Api;

/// <summary>HTTP implementation of <see cref="IFabPilotApi"/>.</summary>
public sealed class FabPilotApiClient(HttpClient http) : IFabPilotApi
{
    public Task<Readiness> GetReadinessAsync(CancellationToken ct = default) =>
        // 503 still carries a valid readiness body: it is data, not an error.
        SendAsync<Readiness>("health/ready", ct, HttpStatusCode.ServiceUnavailable);

    public Task<FabOverview> GetFabOverviewAsync(CancellationToken ct = default) =>
        SendAsync<FabOverview>("api/v1/fab/overview", ct);

    private async Task<T> SendAsync<T>(string path, CancellationToken ct, params HttpStatusCode[] alsoOk)
    {
        HttpResponseMessage resp;
        try
        {
            resp = await http.GetAsync(path, ct);
        }
        catch (Exception ex) when (ex is HttpRequestException or TaskCanceledException)
        {
            throw new FabPilotApiException($"Backend unreachable: {ex.Message}", inner: ex);
        }

        using (resp)
        {
            if (resp.IsSuccessStatusCode || alsoOk.Contains(resp.StatusCode))
            {
                return await resp.Content.ReadFromJsonAsync<T>(ct)
                    ?? throw new FabPilotApiException($"Empty response from {path}");
            }

            Problem? problem = null;
            if (resp.Content.Headers.ContentType?.MediaType == "application/problem+json")
            {
                problem = await resp.Content.ReadFromJsonAsync<Problem>(ct);
            }
            throw new FabPilotApiException(
                problem?.Detail ?? problem?.Title ?? $"{(int)resp.StatusCode} from {path}", problem);
        }
    }
}
