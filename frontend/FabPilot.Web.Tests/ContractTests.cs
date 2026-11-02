using System.Reflection;
using System.Text.Json;
using System.Text.Json.Serialization;
using FabPilot.Web.Api.Contracts;

namespace FabPilot.Web.Tests;

/// <summary>
/// Cross-language contract check: every property of a frontend DTO must exist in the matching
/// schema of contracts/openapi.json (exported from the FastAPI code). Renaming a field in Python
/// without updating C# fails here instead of at runtime.
/// </summary>
public class ContractTests
{
    private static readonly JsonElement Schemas = LoadSchemas();

    private static JsonElement LoadSchemas()
    {
        var path = Path.Combine(AppContext.BaseDirectory, "openapi.json");
        using var doc = JsonDocument.Parse(File.ReadAllText(path));
        return doc.RootElement.GetProperty("components").GetProperty("schemas").Clone();
    }

    [Theory]
    [InlineData(typeof(Readiness), "ReadinessOut")]
    [InlineData(typeof(Check), "CheckOut")]
    [InlineData(typeof(FabOverview), "FabOverviewOut")]
    public void Dto_properties_exist_in_contract(Type dto, string schemaName)
    {
        var schemaProps = Schemas.GetProperty(schemaName).GetProperty("properties")
            .EnumerateObject().Select(p => p.Name).ToHashSet();

        var dtoProps = dto.GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(p => IsPositional(dto, p))
            .Select(p => p.GetCustomAttribute<JsonPropertyNameAttribute>()?.Name ?? JsonNamingPolicy.CamelCase.ConvertName(p.Name))
            .ToList();

        Assert.NotEmpty(dtoProps);
        Assert.All(dtoProps, name => Assert.Contains(name, schemaProps));
    }

    // Only constructor (positional record) parameters are wire fields; computed props like IsOk are not.
    private static bool IsPositional(Type dto, PropertyInfo p) =>
        dto.GetConstructors().Any(c => c.GetParameters().Any(a => a.Name == p.Name));
}
