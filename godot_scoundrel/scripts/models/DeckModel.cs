using System;
using System.Collections.Generic;

namespace ScoundrelGodot.Models;

public sealed class DeckModel
{
    private readonly List<CardData> _cards = [];
    private readonly Random _rng;

    public DeckModel(string seed, bool originalMode = true)
    {
        _rng = new Random(StableSeed(seed));
        BuildDeck(originalMode);
        Shuffle();
    }

    public int Remaining => _cards.Count;

    public CardData? Draw()
    {
        if (_cards.Count == 0)
        {
            return null;
        }

        var lastIndex = _cards.Count - 1;
        var card = _cards[lastIndex];
        _cards.RemoveAt(lastIndex);
        return card;
    }

    public void PlaceManyBottom(IReadOnlyList<CardData> cards)
    {
        if (cards.Count == 0)
        {
            return;
        }
        _cards.InsertRange(0, cards);
    }

    public int RemainingMonsterValue()
    {
        var value = 0;
        foreach (var card in _cards)
        {
            if (card.Type == CardType.Monster)
            {
                value += card.Value;
            }
        }
        return value;
    }

    private void BuildDeck(bool originalMode)
    {
        foreach (SuitType suit in Enum.GetValues(typeof(SuitType)))
        {
            for (var rank = 1; rank <= 13; rank++)
            {
                if (!IncludeCard(originalMode, suit, rank))
                {
                    continue;
                }
                _cards.Add(new CardData(suit, rank));
            }
        }
    }

    private static bool IncludeCard(bool originalMode, SuitType suit, int rank)
    {
        if (!originalMode)
        {
            return true;
        }

        // Official original setup removes red aces and red face cards.
        if (suit is SuitType.Hearts or SuitType.Diamonds)
        {
            if (rank is 1 or 11 or 12 or 13)
            {
                return false;
            }
        }
        return true;
    }

    private void Shuffle()
    {
        for (var i = _cards.Count - 1; i > 0; i--)
        {
            var j = _rng.Next(i + 1);
            (_cards[i], _cards[j]) = (_cards[j], _cards[i]);
        }
    }

    private static int StableSeed(string seed)
    {
        unchecked
        {
            uint hash = 2166136261;
            foreach (var ch in seed)
            {
                hash ^= ch;
                hash *= 16777619;
            }
            return (int)(hash & 0x7FFFFFFF);
        }
    }
}
