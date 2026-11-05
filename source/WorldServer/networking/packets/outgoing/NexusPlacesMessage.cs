using Shared;

namespace WorldServer.networking.packets.outgoing
{
    // The Nexus's places (NexusPlaces.cs): each one's name, kind (0 someone to talk to, 1 a portal)
    // and where it stands.
    public class NexusPlacesMessage : OutgoingMessage
    {
        public (string Name, byte Kind, float X, float Y)[] Places { get; set; }

        public override MessageId MessageId => MessageId.NEXUS_PLACES;

        public override void Write(NetworkWriter wtr)
        {
            wtr.Write((short)Places.Length);
            foreach (var (name, kind, x, y) in Places)
            {
                wtr.WriteUTF16(name);
                wtr.Write(kind);
                wtr.Write(x);
                wtr.Write(y);
            }
        }
    }
}
