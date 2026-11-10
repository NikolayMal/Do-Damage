using System;
using System.Collections.Generic;
using System.Linq;
using Shared.resources;
using WorldServer.core.net.datas;
using WorldServer.core.structures;
using WorldServer.core.worlds;
using WorldServer.networking.packets.outgoing;

namespace WorldServer.core.objects
{
    // The Black Between's gear (tools/build_black_between.py, the Mysterious One's white bags): what
    // each does beyond its numbers, by its <RelicPower>. BetweenAbility runs when the ability is
    // used (after its own activations, so the Cloak's wearer has already landed), BetweenHit when
    // one of the ability's own shots hits an enemy, DecoyTick for the Prism's decoy.
    partial class Player
    {
        private long _veilShotAt;

        private const uint Gold = 0xFFFFD24A, Violet = 0xFFB040FF, Rift = 0xFF6A40C0;

        private void Blast(Position at, float radius, uint color) =>
            World?.BroadcastIfVisible(new ShowEffect { EffectType = EffectType.AreaBlast, TargetObjectId = Id, Pos1 = new Position(radius, 0), Pos2 = at, Color = new ARGB(color) }, ref at);

        private void Burst(Position at, float radius, uint color) =>
            World?.BroadcastIfVisible(new ShowEffect { EffectType = EffectType.Diffuse, TargetObjectId = Id, Pos1 = at, Pos2 = new Position(at.X + radius, at.Y), Color = new ARGB(color) }, ref at);

        // the ability's projectile with this index, fired by the server from `from` (it counts as
        // the ability's, so its hits come back through BetweenHit)
        private void ShootFrom(Item item, int index, Position from, IEnumerable<float> angles, bool noAttack = false)
        {
            if (World == null || item == null || item.Projectiles.Length <= index)
                return;
            var desc = item.Projectiles[index];
            var shots = new List<OutgoingMessage>();
            foreach (var angle in angles)
            {
                var roll = Random.Shared.Next(desc.MinDamage, desc.MaxDamage + 1);
                var damage = noAttack ? roll : (int)(roll * Stats.GetAttackMult());
                shots.Add(new ServerPlayerShoot(Id, GetNextBulletId(1, true), item.ObjectType, from, angle, damage, desc));
            }
            World.BroadcastIfVisible(shots, ref from);
        }

        private static IEnumerable<float> Ring(int n, float start = 0) =>
            Enumerable.Range(0, n).Select(i => start + i * MathF.PI * 2 / n);

        private void BetweenAbility(Position pos, ref TickTime time)
        {
            if (World == null)
                return;
            var item = Inventory[1];
            switch (item?.RelicPower)
            {
                // three stages at the target, half a second apart: Aurel's lightning, Vesper's
                // veil, their father's rift
                case "TrinityTrap":
                {
                    var at = pos;
                    Burst(at, 3, Gold);
                    World.StartNewTimer(300, (w, t) =>
                    {
                        if (World != w)
                            return;
                        foreach (var e in EnemiesNear(at.X, at.Y, 3.5f))
                        {
                            w.BroadcastIfVisible(new ShowEffect { EffectType = EffectType.Lightning, TargetObjectId = Id, Pos1 = new Position(e.X, e.Y), Pos2 = new Position(90, 0), Color = new ARGB(Gold) }, this);
                            RelicDamage(e, 300, ref t, false);
                            e.ApplyConditionEffect(ConditionEffectIndex.Paralyzed, 2000);
                        }
                    });
                    World.StartNewTimer(900, (w, t) =>
                    {
                        if (World != w)
                            return;
                        Blast(at, 3.5f, Violet);
                        foreach (var e in EnemiesNear(at.X, at.Y, 3.5f))
                        {
                            RelicDamage(e, 300, ref t, false);
                            e.ApplyConditionEffect(ConditionEffectIndex.Slowed, 4000);
                        }
                    });
                    World.StartNewTimer(1500, (w, t) =>
                    {
                        if (World != w)
                            return;
                        Burst(at, 4, Rift);
                        foreach (var e in EnemiesNear(at.X, at.Y, 4))
                        {
                            RelicDamage(e, 200, ref t, false);
                            e.Bleed(this, 450, 3000);
                        }
                    });
                    break;
                }
                // the Cloak: where its wearer lands, the ground bursts, five sunsparks fly out and
                // they're armored for 2 s
                case "PlanarRift":
                {
                    var at = new Position(X, Y);
                    Blast(at, 3, Gold);
                    foreach (var e in EnemiesNear(X, Y, 3))
                        RelicDamage(e, 400, ref time, false);
                    ShootFrom(item, 0, at, Ring(5, (float)(Random.Shared.NextDouble() * Math.PI)));
                    ApplyConditionEffect(ConditionEffectIndex.Armored, 2000);
                    break;
                }
                // the Vial: a splash, then four round it at half, then four beyond at half again
                case "CascadeDusk":
                {
                    var at = pos;
                    Splash(at, 1f, ref time);
                    for (var wave = 1; wave <= 2; wave++)
                    {
                        var scale = wave == 1 ? 0.5f : 0.25f;
                        var dist = wave * 3.5f;
                        var turn = wave == 1 ? 0 : MathF.PI / 4;
                        World.StartNewTimer(wave * 600, (w, t) =>
                        {
                            if (World != w)
                                return;
                            foreach (var a in Ring(4, turn))
                                Splash(new Position(at.X + MathF.Cos(a) * dist, at.Y + MathF.Sin(a) * dist), scale, ref t);
                        });
                    }
                    break;
                }
            }
        }

        // one splash of the Vial: 200 and 1,500 over 6 s at full strength
        private void Splash(Position at, float scale, ref TickTime time)
        {
            Burst(at, 2.5f, Violet);
            foreach (var e in EnemiesNear(at.X, at.Y, 2.5f))
            {
                RelicDamage(e, (int)(200 * scale), ref time, false);
                e.Bleed(this, (int)(1500 * scale), 6000);
            }
        }

        // one of the ability's own shots hit an enemy for dmg
        private void BetweenHit(Enemy enemy, int dmg, ProjectileDesc desc, ref TickTime time)
        {
            if (_inRelic || World == null)
                return;
            var item = Inventory[1];
            switch (item?.RelicPower)
            {
                // the Cyclone Arrow (projectile 0, not its sunsparks) bursts: 2,000 round it, then
                // eight sunsparks
                case "SolarCyclone":
                {
                    if (desc.BulletType != 0)
                        break;
                    var at = new Position(enemy.X, enemy.Y);
                    Blast(at, 3, Gold);
                    foreach (var e in EnemiesNear(at.X, at.Y, 3))
                        RelicDamage(e, 2000, ref time, false);
                    ShootFrom(item, 1, at, Ring(8, (float)(Random.Shared.NextDouble() * Math.PI)));
                    break;
                }
                // each dawn sword heals its wielder 8% of what it does
                case "DawnHelm":
                    if (Health < Stats[0])
                        Player.HealDiscrete(this, Math.Max(1, dmg * 8 / 100), false);
                    break;
            }
        }

        // the Prism's decoy, every tick it lasts: once a second, Vesper's three dusk bolts at the
        // nearest enemy
        internal void DecoyTick(Decoy decoy)
        {
            var item = Inventory[1];
            if (World == null || decoy.World != World || item?.RelicPower != "DuskVeil" || Now < _veilShotAt)
                return;
            var target = EnemiesNear(decoy.X, decoy.Y, 11).OrderBy(e => e.DistTo(decoy)).FirstOrDefault();
            if (target == null)
                return;
            _veilShotAt = Now + 1000;
            var a = MathF.Atan2(target.Y - decoy.Y, target.X - decoy.X);
            ShootFrom(item, 0, new Position(decoy.X, decoy.Y), new[] { a - 0.18f, a, a + 0.18f });
        }
    }
}
