using System.Text.Json.Serialization;

namespace FabPilot.Web.Api.Contracts;

// Mirrors components/schemas/FabOverviewOut in contracts/openapi.json.
public sealed record FabOverview(
    [property: JsonPropertyName("lot_count")] int LotCount,
    [property: JsonPropertyName("lots_by_status")] Dictionary<string, int> LotsByStatus,
    [property: JsonPropertyName("wafer_count")] int WaferCount,
    [property: JsonPropertyName("equipment_count")] int EquipmentCount,
    [property: JsonPropertyName("first_lot_start")] DateTimeOffset? FirstLotStart,
    [property: JsonPropertyName("last_lot_start")] DateTimeOffset? LastLotStart);
