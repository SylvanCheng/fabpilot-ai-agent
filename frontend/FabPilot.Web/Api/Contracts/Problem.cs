namespace FabPilot.Web.Api.Contracts;

/// <summary>RFC 9457 problem details, the backend's single error shape.</summary>
public sealed record Problem(string Type, string Title, int Status, string Code, string? Detail);
