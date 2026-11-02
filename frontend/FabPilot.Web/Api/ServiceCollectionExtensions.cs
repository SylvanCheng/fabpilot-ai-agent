namespace FabPilot.Web.Api;

public static class ServiceCollectionExtensions
{
    /// <summary>Registers <see cref="IFabPilotApi"/>; base URL comes from config <c>Backend:BaseUrl</c>.</summary>
    public static IServiceCollection AddFabPilotApi(this IServiceCollection services, IConfiguration config)
    {
        var baseUrl = config["Backend:BaseUrl"]
            ?? throw new InvalidOperationException("Backend:BaseUrl is not configured");
        services.AddHttpClient<IFabPilotApi, FabPilotApiClient>(c =>
        {
            c.BaseAddress = new Uri(baseUrl.TrimEnd('/') + "/");
            c.Timeout = TimeSpan.FromSeconds(10);
        });
        return services;
    }
}
