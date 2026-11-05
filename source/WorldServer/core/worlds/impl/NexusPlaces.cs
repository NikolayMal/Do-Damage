using System.Collections.Generic;
using System.Linq;
using Shared.resources;
using WorldServer.core.objects;

namespace WorldServer.core.worlds.impl
{
    // The places of the Nexus the minimap marks (the Rust client's events.rs, NEXUS_PLACES): those
    // you talk to (the Warcaller, the Herald, the Divine Forge, the Market Broker, the Pen Keeper...)
    // and the portals (the realms', the vault's, the Arena's), wherever the map puts them, so
    // players can find the way to them before they've been there. Worked out once the map's objects
    // are in.
    public static class NexusPlaces
    {
        // the classes of those you talk to, with what the map calls them when their name won't do
        private static readonly Dictionary<string, string> Talkers = new Dictionary<string, string>
        {
            ["CommunityGoals"] = null, ["Herald"] = null, ["QuestMaster"] = null, ["Chronicler"] = null,
            ["Forge"] = "Divine Forge", ["MarketNPC"] = null, ["PetPen"] = null, ["ChampionsBoard"] = "Hall of Champions",
            ["ReskinVendor"] = null, ["GuildRegister"] = null
        };

        public static (string Name, byte Kind, float X, float Y)[] Of(World world)
        {
            var places = new List<(string, byte, float, float)>();
            var entities = world.StaticObjects.Values.Cast<Entity>().Concat(world.Enemies.Values).Concat(world.SellableObjects.Values)
                .Concat(world.Portals.Values);
            var seen = new HashSet<string>();
            foreach (var e in entities)
            {
                var desc = e.ObjectDesc;
                if (desc?.Class == null)
                    continue;
                if (Talkers.TryGetValue(desc.Class, out var name))
                {
                    name ??= desc.DisplayName;
                    if (seen.Add(name))
                        places.Add((name, 0, e.X, e.Y));
                }
                else if (desc.IdName == "Vault Portal" || desc.IdName.Contains("Guild Hall"))
                {
                    if (seen.Add(desc.DisplayName))
                        places.Add((desc.DisplayName, 1, e.X, e.Y));
                }
            }
            void Region(TileRegion region, string name)
            {
                var tiles = world.RegionTiles(region);
                if (tiles.Count > 0 && seen.Add(name))
                    places.Add((name, 1, (float)tiles.Average(t => t.Point.X) + 0.5f, (float)tiles.Average(t => t.Point.Y) + 0.5f));
            }
            Region(TileRegion.Realm_Portals, "Realm Portals");
            Region(TileRegion.Realm2_Portal, "Realm 2");
            Region(TileRegion.Arena_Portal, "The Arena");
            Region(TileRegion.Nexus_Bar, "Sky Bar");
            return places.ToArray();
        }
    }
}
