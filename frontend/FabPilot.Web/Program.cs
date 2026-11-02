using FabPilot.Web.Api;
using FabPilot.Web.Components;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();
builder.Services.AddFabPilotApi(builder.Configuration);

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error", createScopeForErrors: true);
}

app.UseStaticFiles();
app.UseAntiforgery();

app.MapGet("/healthz", () => Results.Ok(new { status = "ok" }));
app.MapRazorComponents<App>()
    .AddInteractiveServerRenderMode();

app.Run();

// Exposed for WebApplicationFactory-based tests.
public partial class Program;
