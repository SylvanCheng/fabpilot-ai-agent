using System.Net;
using FabPilot.Web.Api;

namespace FabPilot.Web.Tests;

public class FabPilotApiClientTests
{
    private const string ReadyJson = """
        {"status":"degraded","version":"0.1.0","checks":{
          "business_db":{"ok":false,"latency_ms":null,"error":"OperationalError","detail":{}},
          "llm":{"ok":true,"latency_ms":null,"error":null,"detail":{"model":"qwen3:8b","probed":false}}}}
        """;

    [Fact]
    public async Task Readiness_503_is_returned_as_data_not_error()
    {
        var api = new FabPilotApiClient(StubHandler.Client(new StubHandler(HttpStatusCode.ServiceUnavailable, ReadyJson)));

        var ready = await api.GetReadinessAsync();

        Assert.False(ready.IsOk);
        Assert.False(ready.Checks["business_db"].Ok);
        Assert.Equal("qwen3:8b", ready.Checks["llm"].Detail!["model"].GetString());
    }

    [Fact]
    public async Task Overview_maps_snake_case_contract()
    {
        var handler = new StubHandler(HttpStatusCode.OK, """
            {"lot_count":4,"lots_by_status":{"WIP":1,"FINISHED":3},"wafer_count":100,
             "equipment_count":27,"first_lot_start":"2026-09-01T00:00:00Z","last_lot_start":null}
            """);
        var api = new FabPilotApiClient(StubHandler.Client(handler));

        var o = await api.GetFabOverviewAsync();

        Assert.Equal("/api/v1/fab/overview", handler.LastPath);
        Assert.Equal(4, o.LotCount);
        Assert.Equal(3, o.LotsByStatus["FINISHED"]);
        Assert.Null(o.LastLotStart);
    }

    [Fact]
    public async Task Problem_json_becomes_typed_exception()
    {
        var handler = new StubHandler(HttpStatusCode.ServiceUnavailable, """
            {"type":"urn:fabpilot:error:dependency_unavailable","title":"A dependency is unavailable",
             "status":503,"code":"dependency_unavailable","detail":"business database unreachable"}
            """, "application/problem+json");
        var api = new FabPilotApiClient(StubHandler.Client(handler));

        var ex = await Assert.ThrowsAsync<FabPilotApiException>(() => api.GetFabOverviewAsync());

        Assert.Equal("dependency_unavailable", ex.Problem?.Code);
        Assert.Equal("business database unreachable", ex.Message);
    }

    [Fact]
    public async Task Network_failure_becomes_typed_exception()
    {
        var api = new FabPilotApiClient(StubHandler.Client(new ThrowingHandler()));
        await Assert.ThrowsAsync<FabPilotApiException>(() => api.GetReadinessAsync());
    }

    private sealed class ThrowingHandler : HttpMessageHandler
    {
        protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage r, CancellationToken ct) =>
            throw new HttpRequestException("connection refused");
    }
}
