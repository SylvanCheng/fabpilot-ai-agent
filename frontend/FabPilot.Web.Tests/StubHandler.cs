using System.Net;
using System.Text;

namespace FabPilot.Web.Tests;

/// <summary>Returns a canned response; lets us test the client without a running backend.</summary>
internal sealed class StubHandler(HttpStatusCode status, string body, string mediaType = "application/json")
    : HttpMessageHandler
{
    public string? LastPath { get; private set; }

    protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        LastPath = request.RequestUri?.PathAndQuery;
        return Task.FromResult(new HttpResponseMessage(status)
        {
            Content = new StringContent(body, Encoding.UTF8, mediaType),
        });
    }

    public static HttpClient Client(HttpMessageHandler handler) =>
        new(handler) { BaseAddress = new Uri("http://backend/") };
}
