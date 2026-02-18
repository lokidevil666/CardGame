using Godot;
using ScoundrelGodot.Models;

namespace ScoundrelGodot.View;

public sealed class CardViewState
{
    public CardViewState(CardData card, bool entryPending = false)
    {
        Card = card;
        EntryPending = entryPending;
    }

    public CardData Card { get; }
    public Vector2 TargetPosition { get; set; } = Vector2.Zero;
    public Vector2 DrawPosition { get; private set; } = Vector2.Zero;

    public bool HasDrawPosition { get; private set; }
    public bool Hovered { get; private set; }
    public bool IsResolving { get; set; }
    public float ClickTimer { get; private set; }

    public float Scale { get; private set; } = 1f;
    public float Lift { get; private set; }

    public bool EntryPending { get; set; }
    public bool IsSliding { get; private set; }

    private Vector2 _slideFrom = Vector2.Zero;
    private float _slideElapsed;
    private float _slideDelay;
    private float _slideDuration = 0.32f;

    public void SnapToTarget()
    {
        DrawPosition = TargetPosition;
        HasDrawPosition = true;
        EntryPending = false;
        IsSliding = false;
    }

    public void StartSlideFrom(Vector2 startPosition, float delaySeconds = 0f, float durationSeconds = 0.32f)
    {
        _slideFrom = startPosition;
        DrawPosition = startPosition;
        HasDrawPosition = true;
        _slideElapsed = 0f;
        _slideDelay = Mathf.Max(0f, delaySeconds);
        _slideDuration = Mathf.Max(0.05f, durationSeconds);
        IsSliding = true;
        EntryPending = false;
    }

    public void TriggerClick()
    {
        ClickTimer = 0.16f;
    }

    public void Update(float delta, Vector2 mousePosition, bool canInteract, Vector2 cardSize)
    {
        if (!HasDrawPosition)
        {
            SnapToTarget();
        }

        if (IsSliding)
        {
            _slideElapsed += delta;
            var effective = _slideElapsed - _slideDelay;
            if (effective <= 0f)
            {
                DrawPosition = _slideFrom;
            }
            else
            {
                var t = Mathf.Clamp(effective / _slideDuration, 0f, 1f);
                var eased = 1f - Mathf.Pow(1f - t, 3f);
                DrawPosition = _slideFrom.Lerp(TargetPosition, eased);
                if (t >= 1f)
                {
                    IsSliding = false;
                    DrawPosition = TargetPosition;
                }
            }
        }
        else
        {
            DrawPosition = TargetPosition;
        }

        Hovered = canInteract && !IsSliding && InteractionRect(cardSize).HasPoint(mousePosition);
        var targetScale = Hovered ? 1.08f : 1f;
        var targetLift = Hovered ? 16f : 0f;
        Scale = Damp(Scale, targetScale, 15f, delta);
        Lift = Damp(Lift, targetLift, 14f, delta);

        if (ClickTimer > 0f)
        {
            ClickTimer = Mathf.Max(0f, ClickTimer - delta);
        }
    }

    public bool Contains(Vector2 point, Vector2 cardSize)
    {
        return InteractionRect(cardSize).HasPoint(point);
    }

    public Rect2 InteractionRect(Vector2 cardSize)
    {
        var size = cardSize;
        var topLeft = DrawPosition - size / 2f;
        return new Rect2(topLeft, size);
    }

    public Rect2 DrawRect(Vector2 cardSize)
    {
        var clickScale = ClickTimer > 0.10f ? 0.92f : 1f;
        var finalScale = Scale * clickScale;
        var size = cardSize * finalScale;
        var center = DrawPosition + new Vector2(0f, -Lift);
        return new Rect2(center - size / 2f, size);
    }

    private static float Damp(float current, float target, float speed, float delta)
    {
        var amount = Mathf.Clamp(speed * delta, 0f, 1f);
        return current + (target - current) * amount;
    }
}
