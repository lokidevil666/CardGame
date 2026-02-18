using System;

namespace ScoundrelGodot.Models;

public sealed class PlayerModel
{
    public const int StartHp = 20;

    public int MaxHp { get; } = StartHp;
    public int Hp { get; private set; } = StartHp;
    public int WeaponPower { get; private set; }
    public int? WeaponLastSlain { get; private set; }
    public int MonstersDefeated { get; private set; }

    public void Reset()
    {
        Hp = StartHp;
        WeaponPower = 0;
        WeaponLastSlain = null;
        MonstersDefeated = 0;
    }

    public int Heal(int amount)
    {
        var old = Hp;
        Hp = Math.Min(MaxHp, Hp + amount);
        return Hp - old;
    }

    public int EquipWeapon(int power)
    {
        var old = WeaponPower;
        WeaponPower = power;
        WeaponLastSlain = null;
        return old;
    }

    public bool CanUseWeapon(int monsterValue)
    {
        if (WeaponPower <= 0)
        {
            return false;
        }
        if (WeaponLastSlain is null)
        {
            return true;
        }
        return monsterValue <= WeaponLastSlain.Value;
    }

    public int FightBarehand(int monsterValue)
    {
        TakeDamage(monsterValue);
        MonstersDefeated += 1;
        return monsterValue;
    }

    public int FightWithWeapon(int monsterValue)
    {
        var damage = Math.Max(0, monsterValue - WeaponPower);
        TakeDamage(damage);
        WeaponLastSlain = monsterValue;
        MonstersDefeated += 1;
        return damage;
    }

    private void TakeDamage(int amount)
    {
        Hp = Math.Max(0, Hp - amount);
    }
}
