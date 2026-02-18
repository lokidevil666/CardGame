using System;

namespace ScoundrelGodot.Models;

public enum SuitType
{
    Spades,
    Clubs,
    Hearts,
    Diamonds
}

public enum CardType
{
    Monster,
    Potion,
    Weapon
}

public readonly record struct CardData(SuitType Suit, int Rank)
{
    public CardType Type => Suit switch
    {
        SuitType.Spades or SuitType.Clubs => CardType.Monster,
        SuitType.Hearts => CardType.Potion,
        _ => CardType.Weapon
    };

    public int Value => Rank == 1 ? 14 : Rank;

    public string RankName => Rank switch
    {
        1 => "A",
        11 => "J",
        12 => "Q",
        13 => "K",
        _ => Rank.ToString()
    };

    public string SuitShort => Suit switch
    {
        SuitType.Spades => "S",
        SuitType.Clubs => "C",
        SuitType.Hearts => "H",
        SuitType.Diamonds => "D",
        _ => "?"
    };

    public string ShortName => $"{RankName}{SuitShort}";

    public ColorScheme Colors => Type switch
    {
        CardType.Monster => new ColorScheme(0.56f, 0.20f, 0.24f),
        CardType.Potion => new ColorScheme(0.20f, 0.49f, 0.35f),
        _ => new ColorScheme(0.24f, 0.34f, 0.60f)
    };
}

public readonly record struct ColorScheme(float R, float G, float B);
