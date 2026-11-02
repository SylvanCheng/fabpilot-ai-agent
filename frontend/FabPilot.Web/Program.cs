using FabPilot.Web.Components;
using FabPilot.Web.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddRazorComponents()
    .AddInteractiveServerComponents();

// Backend URL comes from configuration (appsettings / env var Backend__BaseUrl), never hard-coded.
var backendUrl = builder.Configuration["Backend:BaseUrl"]
    ?? throw new InvalidOperationException("Backend:BaseUrl is not configured");
builder.Services.AddHttpClient<BackendClient>(c =>
{
    c.BaseAddress = new Uri(backendUrl.TrimEnd('/') + "/");
    c.Timeout = TimeSpan.FromSeconds(10);
});

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
