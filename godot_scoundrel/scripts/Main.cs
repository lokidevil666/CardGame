using System;
using System.Collections.Generic;
using Godot;
using ScoundrelGodot.Models;
using ScoundrelGodot.View;

namespace ScoundrelGodot;

public partial class Main : Control
{
    private enum ScreenState
    {
        Menu,
        Combat,
        End
    }

    private static readonly Color BgColor = new(0.05f, 0.07f, 0.12f, 1f);
    private static readonly Color PanelColor = new(0.14f, 0.17f, 0.24f, 1f);
    private static readonly Color BorderColor = new(0.03f, 0.04f, 0.07f, 1f);
    private static readonly Color TextColor = new(0.93f, 0.94f, 0.97f, 1f);
    private static readonly Color SubtextColor = new(0.72f, 0.75f, 0.83f, 1f);

    private ScreenState _screen = ScreenState.Menu;

    private Control _menuLayer = null!;
    private LineEdit _menuSeedInput = null!;
    private Label _menuFeedback = null!;

    private Control _combatLayer = null!;
    private Button _combatCopySeedButton = null!;
    private Button _combatAvoidButton = null!;

    private Control _endLayer = null!;
    private Label _endTitleLabel = null!;
    private Label _endSubtitleLabel = null!;
    private Label _endStatsLabel = null!;

    private string _currentSeed = string.Empty;

    private DeckModel? _deck;
    private readonly PlayerModel _player = new();
    private readonly List<CardViewState> _roomCards = [];
    private CardViewState? _resolvingCard;
    private float _resolveTimer;
    private bool _runOver;

    private int _roomIndex;
    private int _cardsTakenThisRoom;
    private int _cardsRequiredThisRoom;
    private bool _roomStarted;
    private bool _potionUsedThisRoom;
    private bool _avoidedLastRoom;

    private CardType? _lastCardType;
    private int _lastCardValue;
    private int _finalScore;
    private int _perfectPotionBonus;

    private readonly List<string> _logs = [];
    private const int MaxLogs = 7;

    private Rect2 _topPanel = Rect2.Zero;
    private Rect2 _logPanel = Rect2.Zero;
    private Rect2 _boardRect = Rect2.Zero;
    private Rect2 _deckSlotRect = Rect2.Zero;
    private Rect2 _weaponSlotRect = Rect2.Zero;
    private readonly Rect2[] _roomSlotRects = new Rect2[4];
    private Vector2 _cardSize = new(122f, 180f);

    private readonly RandomNumberGenerator _seedRng = new();

    public override void _Ready()
    {
        MouseFilter = MouseFilterEnum.Stop;
        FocusMode = FocusModeEnum.All;
        _seedRng.Randomize();

        BuildMenuLayer();
        BuildCombatLayer();
        BuildEndLayer();

        SetScreen(ScreenState.Menu);
    }

    public override void _Process(double delta)
    {
        if (_screen == ScreenState.Combat)
        {
            UpdateCombat((float)delta);
        }

        QueueRedraw();
    }

    public override void _UnhandledInput(InputEvent @event)
    {
        if (@event is InputEventKey keyEvent && keyEvent.Pressed && !keyEvent.Echo)
        {
            HandleKeyInput(keyEvent);
            return;
        }

        if (_screen == ScreenState.Combat &&
            @event is InputEventMouseButton buttonEvent &&
            buttonEvent.Pressed &&
            (buttonEvent.ButtonIndex == MouseButton.Left || buttonEvent.ButtonIndex == MouseButton.Right))
        {
            HandleCombatCardClick(buttonEvent.ButtonIndex, buttonEvent.Position);
        }
    }

    public override void _Draw()
    {
        DrawRect(new Rect2(Vector2.Zero, Size), BgColor, true);

        if (_screen == ScreenState.Combat)
        {
            DrawCombat();
            return;
        }

        if (_screen == ScreenState.Menu)
        {
            DrawMenuBackground();
            return;
        }

        DrawEndBackground();
    }

    private void BuildMenuLayer()
    {
        _menuLayer = new Control();
        _menuLayer.SetAnchorsPreset(LayoutPreset.FullRect);
        AddChild(_menuLayer);

        var center = new CenterContainer();
        center.SetAnchorsPreset(LayoutPreset.FullRect);
        _menuLayer.AddChild(center);

        var panel = new PanelContainer
        {
            CustomMinimumSize = new Vector2(920f, 560f)
        };
        center.AddChild(panel);

        var margins = new MarginContainer();
        margins.AddThemeConstantOverride("margin_left", 28);
        margins.AddThemeConstantOverride("margin_right", 28);
        margins.AddThemeConstantOverride("margin_top", 22);
        margins.AddThemeConstantOverride("margin_bottom", 22);
        panel.AddChild(margins);

        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 14);
        margins.AddChild(vbox);

        var title = new Label
        {
            Text = "SCOUNDREL ROGUELIKE - GODOT C#",
            HorizontalAlignment = HorizontalAlignment.Center
        };
        title.AddThemeFontSizeOverride("font_size", 34);
        vbox.AddChild(title);

        var subtitle = new Label
        {
            Text = "Versao Godot 4 + C# com foco em performance grafica 2D.",
            HorizontalAlignment = HorizontalAlignment.Center
        };
        subtitle.AddThemeFontSizeOverride("font_size", 20);
        vbox.AddChild(subtitle);

        var rules = new Label
        {
            Text =
                "Regras oficiais Scoundrel: HP 20, sala com 4 cartas, resolves 3 e deixas 1.\n" +
                "Podes evitar sala, mas nao duas seguidas. 1 pocao por sala.\n" +
                "Monstro: click esquerdo tenta arma, direito usa mao nua.\n" +
                "Layout: deck no topo, 4 cartas no meio e arma equipada em baixo.",
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Left
        };
        rules.AddThemeFontSizeOverride("font_size", 18);
        vbox.AddChild(rules);

        var seedLabel = new Label
        {
            Text = "Seed (opcional):"
        };
        seedLabel.AddThemeFontSizeOverride("font_size", 20);
        vbox.AddChild(seedLabel);

        _menuSeedInput = new LineEdit
        {
            PlaceholderText = "deixa vazio para seed aleatoria",
            MaxLength = 32
        };
        _menuSeedInput.AddThemeFontSizeOverride("font_size", 20);
        vbox.AddChild(_menuSeedInput);

        var row = new HBoxContainer();
        row.AddThemeConstantOverride("separation", 12);
        vbox.AddChild(row);

        var startButton = new Button
        {
            Text = "INICIAR RUN (ENTER)",
            SizeFlagsHorizontal = SizeFlags.ExpandFill
        };
        startButton.AddThemeFontSizeOverride("font_size", 20);
        startButton.Pressed += StartRunFromMenu;
        row.AddChild(startButton);

        var copyButton = new Button
        {
            Text = "COPIAR SEED",
            CustomMinimumSize = new Vector2(190f, 0f)
        };
        copyButton.AddThemeFontSizeOverride("font_size", 20);
        copyButton.Pressed += CopySeedFromMenu;
        row.AddChild(copyButton);

        var controls = new Label
        {
            Text = "TAB foca seed | CTRL+C copia seed | F11 fullscreen",
            HorizontalAlignment = HorizontalAlignment.Center
        };
        controls.AddThemeFontSizeOverride("font_size", 17);
        vbox.AddChild(controls);

        _menuFeedback = new Label
        {
            Text = "",
            HorizontalAlignment = HorizontalAlignment.Center,
            Modulate = new Color(0.67f, 0.84f, 1f)
        };
        _menuFeedback.AddThemeFontSizeOverride("font_size", 18);
        vbox.AddChild(_menuFeedback);
    }

    private void BuildCombatLayer()
    {
        _combatLayer = new Control();
        _combatLayer.SetAnchorsPreset(LayoutPreset.FullRect);
        _combatLayer.Visible = false;
        AddChild(_combatLayer);

        _combatCopySeedButton = new Button
        {
            Text = "COPIAR SEED (C)",
            CustomMinimumSize = new Vector2(220f, 40f)
        };
        _combatCopySeedButton.Pressed += CopyCurrentSeed;
        _combatLayer.AddChild(_combatCopySeedButton);

        _combatAvoidButton = new Button
        {
            Text = "EVITAR SALA (A)",
            CustomMinimumSize = new Vector2(220f, 40f)
        };
        _combatAvoidButton.Pressed += AvoidRoom;
        _combatLayer.AddChild(_combatAvoidButton);
    }

    private void BuildEndLayer()
    {
        _endLayer = new Control();
        _endLayer.SetAnchorsPreset(LayoutPreset.FullRect);
        _endLayer.Visible = false;
        AddChild(_endLayer);

        var center = new CenterContainer();
        center.SetAnchorsPreset(LayoutPreset.FullRect);
        _endLayer.AddChild(center);

        var panel = new PanelContainer
        {
            CustomMinimumSize = new Vector2(780f, 450f)
        };
        center.AddChild(panel);

        var margins = new MarginContainer();
        margins.AddThemeConstantOverride("margin_left", 24);
        margins.AddThemeConstantOverride("margin_right", 24);
        margins.AddThemeConstantOverride("margin_top", 24);
        margins.AddThemeConstantOverride("margin_bottom", 24);
        panel.AddChild(margins);

        var vbox = new VBoxContainer();
        vbox.AddThemeConstantOverride("separation", 12);
        margins.AddChild(vbox);

        _endTitleLabel = new Label
        {
            Text = "FIM",
            HorizontalAlignment = HorizontalAlignment.Center
        };
        _endTitleLabel.AddThemeFontSizeOverride("font_size", 40);
        vbox.AddChild(_endTitleLabel);

        _endSubtitleLabel = new Label
        {
            Text = "",
            HorizontalAlignment = HorizontalAlignment.Center
        };
        _endSubtitleLabel.AddThemeFontSizeOverride("font_size", 20);
        vbox.AddChild(_endSubtitleLabel);

        _endStatsLabel = new Label
        {
            Text = "",
            AutowrapMode = TextServer.AutowrapMode.WordSmart,
            HorizontalAlignment = HorizontalAlignment.Left,
            VerticalAlignment = VerticalAlignment.Top,
            SizeFlagsVertical = SizeFlags.ExpandFill
        };
        _endStatsLabel.AddThemeFontSizeOverride("font_size", 20);
        vbox.AddChild(_endStatsLabel);

        var row = new HBoxContainer();
        row.AddThemeConstantOverride("separation", 10);
        vbox.AddChild(row);

        var restart = new Button
        {
            Text = "REINICIAR (R)",
            SizeFlagsHorizontal = SizeFlags.ExpandFill
        };
        restart.Pressed += () => StartRun(_currentSeed);
        row.AddChild(restart);

        var copySeed = new Button
        {
            Text = "COPIAR SEED (C)",
            SizeFlagsHorizontal = SizeFlags.ExpandFill
        };
        copySeed.Pressed += CopyCurrentSeed;
        row.AddChild(copySeed);

        var menu = new Button
        {
            Text = "MENU (M)",
            SizeFlagsHorizontal = SizeFlags.ExpandFill
        };
        menu.Pressed += () => SetScreen(ScreenState.Menu);
        row.AddChild(menu);
    }

    private void HandleKeyInput(InputEventKey keyEvent)
    {
        if (keyEvent.Keycode == Key.F11)
        {
            ToggleFullscreen();
            return;
        }

        switch (_screen)
        {
            case ScreenState.Menu:
                HandleMenuKeys(keyEvent);
                break;
            case ScreenState.Combat:
                HandleCombatKeys(keyEvent);
                break;
            case ScreenState.End:
                HandleEndKeys(keyEvent);
                break;
        }
    }

    private void HandleMenuKeys(InputEventKey keyEvent)
    {
        if (keyEvent.Keycode is Key.Enter or Key.KpEnter)
        {
            StartRunFromMenu();
            return;
        }

        if (keyEvent.CtrlPressed && keyEvent.Keycode == Key.C)
        {
            CopySeedFromMenu();
            return;
        }

        if (keyEvent.Keycode == Key.Escape)
        {
            GetTree().Quit();
        }
    }

    private void HandleCombatKeys(InputEventKey keyEvent)
    {
        if (keyEvent.Keycode == Key.Escape)
        {
            SetScreen(ScreenState.Menu);
            return;
        }
        if (keyEvent.Keycode == Key.R)
        {
            StartRun(_currentSeed);
            return;
        }
        if (keyEvent.Keycode == Key.A)
        {
            AvoidRoom();
            return;
        }
        if (keyEvent.Keycode == Key.C)
        {
            CopyCurrentSeed();
        }
    }

    private void HandleEndKeys(InputEventKey keyEvent)
    {
        if (keyEvent.Keycode == Key.R)
        {
            StartRun(_currentSeed);
            return;
        }
        if (keyEvent.Keycode == Key.M)
        {
            SetScreen(ScreenState.Menu);
            return;
        }
        if (keyEvent.Keycode == Key.C)
        {
            CopyCurrentSeed();
            return;
        }
        if (keyEvent.Keycode == Key.Escape)
        {
            GetTree().Quit();
        }
    }

    private void SetScreen(ScreenState state)
    {
        _screen = state;
        _menuLayer.Visible = state == ScreenState.Menu;
        _combatLayer.Visible = state == ScreenState.Combat;
        _endLayer.Visible = state == ScreenState.End;

        if (state == ScreenState.Menu)
        {
            if (!string.IsNullOrWhiteSpace(_currentSeed))
            {
                _menuSeedInput.Text = _currentSeed;
            }
            _menuSeedInput.GrabFocus();
        }
    }

    private void StartRunFromMenu()
    {
        var seed = _menuSeedInput.Text.Trim();
        if (string.IsNullOrWhiteSpace(seed))
        {
            seed = GenerateSeed();
            _menuSeedInput.Text = seed;
        }

        StartRun(seed);
        _menuFeedback.Text = $"Run iniciada com seed {seed}";
    }

    private void StartRun(string seed)
    {
        _currentSeed = seed;
        _deck = new DeckModel(seed, originalMode: true);
        _player.Reset();

        _roomCards.Clear();
        _resolvingCard = null;
        _resolveTimer = 0f;
        _runOver = false;

        _roomIndex = 1;
        _cardsTakenThisRoom = 0;
        _cardsRequiredThisRoom = 0;
        _roomStarted = false;
        _potionUsedThisRoom = false;
        _avoidedLastRoom = false;

        _lastCardType = null;
        _lastCardValue = 0;
        _finalScore = 0;
        _perfectPotionBonus = 0;

        _logs.Clear();
        AddLog("Regras oficiais: sala de 4 cartas, escolhe 3 e deixa 1.");
        AddLog($"Seed ativa: {seed}");

        FillRoomToFour();
        BeginRoomActions();
        LayoutCombatRects();
        SetScreen(ScreenState.Combat);
    }

    private string GenerateSeed()
    {
        return $"{_seedRng.Randi():X8}{_seedRng.Randi():X8}";
    }

    private void CopySeedFromMenu()
    {
        var text = _menuSeedInput.Text.Trim();
        if (string.IsNullOrWhiteSpace(text))
        {
            text = _currentSeed;
        }

        if (string.IsNullOrWhiteSpace(text))
        {
            _menuFeedback.Text = "Sem seed para copiar.";
            return;
        }

        DisplayServer.ClipboardSet(text);
        _menuFeedback.Text = $"Seed copiada: {text}";
    }

    private void CopyCurrentSeed()
    {
        if (string.IsNullOrWhiteSpace(_currentSeed))
        {
            return;
        }
        DisplayServer.ClipboardSet(_currentSeed);
        AddLog($"Seed copiada: {_currentSeed}");
    }

    private void ToggleFullscreen()
    {
        var mode = DisplayServer.WindowGetMode();
        if (mode == DisplayServer.WindowMode.Fullscreen ||
            mode == DisplayServer.WindowMode.ExclusiveFullscreen)
        {
            DisplayServer.WindowSetMode(DisplayServer.WindowMode.Windowed);
            return;
        }
        DisplayServer.WindowSetMode(DisplayServer.WindowMode.Fullscreen);
    }

    private void FillRoomToFour()
    {
        if (_deck is null)
        {
            return;
        }

        while (_roomCards.Count < 4)
        {
            var drawn = _deck.Draw();
            if (drawn is null)
            {
                break;
            }
            _roomCards.Add(new CardViewState(drawn.Value, entryPending: true));
        }
    }

    private void BeginRoomActions()
    {
        _cardsTakenThisRoom = 0;
        _potionUsedThisRoom = false;
        _roomStarted = false;

        if (_roomCards.Count <= 0)
        {
            _cardsRequiredThisRoom = 0;
            return;
        }
        if (_roomCards.Count == 1)
        {
            _cardsRequiredThisRoom = 1;
            return;
        }
        _cardsRequiredThisRoom = Math.Min(3, _roomCards.Count - 1);
    }

    private void LayoutCombatRects()
    {
        if (_screen != ScreenState.Combat)
        {
            return;
        }

        var viewportSize = GetViewportRect().Size;
        _topPanel = new Rect2(24f, 16f, viewportSize.X - 48f, 96f);
        _logPanel = new Rect2(24f, viewportSize.Y - 132f, viewportSize.X - 48f, 108f);

        var boardTop = _topPanel.End.Y + 8f;
        var boardBottom = _logPanel.Position.Y - 8f;
        var boardHeight = Mathf.Max(220f, boardBottom - boardTop);
        _boardRect = new Rect2(24f, boardTop, viewportSize.X - 48f, boardHeight);

        var cardHeight = Mathf.Clamp(_boardRect.Size.Y * 0.30f, 128f, 180f);
        var cardWidth = cardHeight * 0.68f;
        _cardSize = new Vector2(cardWidth, cardHeight);

        _deckSlotRect = RectFromCenter(new Vector2(_boardRect.GetCenter().X, _boardRect.Position.Y + cardHeight / 2f + 2f), _cardSize);
        _weaponSlotRect = RectFromCenter(new Vector2(_boardRect.GetCenter().X, _boardRect.End.Y - cardHeight / 2f - 2f), _cardSize);

        var gap = Mathf.Max(18f, cardWidth * 0.16f);
        var totalWidth = cardWidth * 4f + gap * 3f;
        var firstCenterX = _boardRect.GetCenter().X - totalWidth / 2f + cardWidth / 2f;
        var rowY = _boardRect.GetCenter().Y;
        for (var i = 0; i < _roomSlotRects.Length; i++)
        {
            var center = new Vector2(firstCenterX + i * (cardWidth + gap), rowY);
            _roomSlotRects[i] = RectFromCenter(center, _cardSize);
        }

        var pendingIndex = 0;
        for (var i = 0; i < _roomCards.Count; i++)
        {
            var view = _roomCards[i];
            var slot = _roomSlotRects[Mathf.Min(i, _roomSlotRects.Length - 1)];
            view.TargetPosition = slot.GetCenter();

            if (view.EntryPending)
            {
                view.StartSlideFrom(_deckSlotRect.GetCenter(), 0.07f * pendingIndex, 0.28f);
                pendingIndex += 1;
            }
            else if (!view.HasDrawPosition && !view.IsSliding)
            {
                view.SnapToTarget();
            }
        }

        _combatCopySeedButton.Size = new Vector2(220f, 40f);
        _combatCopySeedButton.Position = new Vector2(_topPanel.End.X - 14f - _combatCopySeedButton.Size.X, _topPanel.Position.Y + 10f);
        _combatAvoidButton.Size = new Vector2(220f, 40f);
        _combatAvoidButton.Position = new Vector2(_topPanel.End.X - 14f - _combatAvoidButton.Size.X, _topPanel.Position.Y + 52f);
        _combatAvoidButton.Disabled = !CanAvoidRoom();
    }

    private bool IsDealAnimationActive()
    {
        for (var i = 0; i < _roomCards.Count; i++)
        {
            var card = _roomCards[i];
            if (card.EntryPending || card.IsSliding)
            {
                return true;
            }
        }
        return false;
    }

    private bool CanAvoidRoom()
    {
        return _roomCards.Count == 4 &&
               !_roomStarted &&
               !_avoidedLastRoom &&
               _resolveTimer <= 0f &&
               !IsDealAnimationActive();
    }

    private void AvoidRoom()
    {
        if (!CanAvoidRoom())
        {
            AddLog("Nao podes evitar esta sala agora.");
            return;
        }
        if (_deck is null)
        {
            return;
        }

        var cards = new List<CardData>(_roomCards.Count);
        for (var i = 0; i < _roomCards.Count; i++)
        {
            cards.Add(_roomCards[i].Card);
        }

        _deck.PlaceManyBottom(cards);
        _roomCards.Clear();
        _roomIndex += 1;
        _avoidedLastRoom = true;

        FillRoomToFour();
        BeginRoomActions();
        LayoutCombatRects();
        AddLog($"Sala evitada. Entraste na sala {_roomIndex}.");
    }

    private void UpdateCombat(float delta)
    {
        if (_deck is null || _runOver)
        {
            return;
        }

        LayoutCombatRects();
        var canInteract = _resolveTimer <= 0f && _player.Hp > 0 && !IsDealAnimationActive();
        var mouse = GetViewport().GetMousePosition();

        for (var i = 0; i < _roomCards.Count; i++)
        {
            var card = _roomCards[i];
            var cardInteract = canInteract && !card.IsResolving;
            card.Update(delta, mouse, cardInteract, _cardSize);
        }

        if (_resolveTimer > 0f)
        {
            _resolveTimer = Mathf.Max(0f, _resolveTimer - delta);
            if (_resolveTimer == 0f && _resolvingCard is not null)
            {
                _roomCards.Remove(_resolvingCard);
                _resolvingCard = null;
                LayoutCombatRects();
                FinishRoomIfNeeded();
            }
        }
    }

    private void HandleCombatCardClick(MouseButton button, Vector2 position)
    {
        if (_deck is null)
        {
            return;
        }
        if (_resolveTimer > 0f || _player.Hp <= 0 || IsDealAnimationActive())
        {
            return;
        }

        for (var i = _roomCards.Count - 1; i >= 0; i--)
        {
            var cardView = _roomCards[i];
            if (!cardView.Contains(position, _cardSize))
            {
                continue;
            }

            var preferWeapon = button == MouseButton.Left && cardView.Card.Type == CardType.Monster;
            cardView.IsResolving = true;
            cardView.TriggerClick();
            _resolvingCard = cardView;
            _resolveTimer = 0.18f;
            ResolveCard(cardView.Card, preferWeapon);
            return;
        }
    }

    private void ResolveCard(CardData card, bool preferWeapon)
    {
        _roomStarted = true;
        _avoidedLastRoom = false;
        _cardsTakenThisRoom += 1;
        _lastCardType = card.Type;
        _lastCardValue = card.Value;

        if (card.Type == CardType.Weapon)
        {
            var old = _player.EquipWeapon(card.Value);
            if (old == 0)
            {
                AddLog($"Equipaste {card.ShortName}. Poder da arma = {card.Value}.");
            }
            else
            {
                AddLog($"Trocaste arma {old} -> {card.Value}.");
            }
            return;
        }

        if (card.Type == CardType.Potion)
        {
            if (_potionUsedThisRoom)
            {
                AddLog($"Pocao {card.ShortName} descartada (ja usaste uma nesta sala).");
                return;
            }

            var healed = _player.Heal(card.Value);
            _potionUsedThisRoom = true;
            AddLog($"Pocao {card.ShortName}: curaste {healed} HP.");
            return;
        }

        var usedWeapon = preferWeapon && _player.CanUseWeapon(card.Value);
        if (usedWeapon)
        {
            var damage = _player.FightWithWeapon(card.Value);
            AddLog($"Monstro {card.ShortName} com arma {_player.WeaponPower}: dano {damage}.");
            return;
        }

        if (preferWeapon && _player.WeaponPower > 0 && !_player.CanUseWeapon(card.Value))
        {
            AddLog($"Arma bloqueada contra {card.ShortName} (limite <= {_player.WeaponLastSlain}).");
        }

        var bareDamage = _player.FightBarehand(card.Value);
        AddLog($"Monstro {card.ShortName} na mao nua: levaste {bareDamage}.");
    }

    private void FinishRoomIfNeeded()
    {
        if (_deck is null || _runOver)
        {
            return;
        }

        if (_player.Hp <= 0)
        {
            _finalScore = _player.Hp - RemainingMonsterValue();
            ShowEndScreen(victory: false);
            return;
        }

        if (_cardsTakenThisRoom < _cardsRequiredThisRoom)
        {
            return;
        }

        if (_deck.Remaining == 0 && _roomCards.Count == 0)
        {
            _perfectPotionBonus = 0;
            if (_player.Hp == _player.MaxHp && _lastCardType == CardType.Potion)
            {
                _perfectPotionBonus = _lastCardValue;
            }
            _finalScore = _player.Hp + _perfectPotionBonus;
            ShowEndScreen(victory: true);
            return;
        }

        _roomIndex += 1;
        FillRoomToFour();
        BeginRoomActions();
        LayoutCombatRects();
        AddLog($"Sala {_roomIndex} iniciada.");
    }

    private int RemainingMonsterValue()
    {
        if (_deck is null)
        {
            return 0;
        }

        var roomValue = 0;
        for (var i = 0; i < _roomCards.Count; i++)
        {
            if (_roomCards[i].Card.Type == CardType.Monster)
            {
                roomValue += _roomCards[i].Card.Value;
            }
        }
        return roomValue + _deck.RemainingMonsterValue();
    }

    private void ShowEndScreen(bool victory)
    {
        _runOver = true;
        var title = victory ? "VITORIA!" : "DERROTA!";
        var subtitle = victory
            ? "Limpaste o dungeon do Scoundrel."
            : "Chegaste a 0 HP antes de terminar o dungeon.";

        _endTitleLabel.Text = title;
        _endTitleLabel.Modulate = victory ? new Color(0.49f, 0.90f, 0.59f) : new Color(0.93f, 0.49f, 0.43f);
        _endSubtitleLabel.Text = subtitle;

        var stats =
            $"Salas jogadas: {_roomIndex}\n" +
            $"Monstros derrotados: {_player.MonstersDefeated}\n" +
            $"HP final: {_player.Hp}\n" +
            $"Score: {_finalScore}\n" +
            $"Seed: {_currentSeed}";
        if (victory && _perfectPotionBonus > 0)
        {
            stats += $"\nBonus de pocao perfeita: +{_perfectPotionBonus}";
        }
        _endStatsLabel.Text = stats;

        SetScreen(ScreenState.End);
    }

    private void AddLog(string message)
    {
        _logs.Insert(0, message);
        if (_logs.Count > MaxLogs)
        {
            _logs.RemoveAt(_logs.Count - 1);
        }
    }

    private void DrawMenuBackground()
    {
        var glow = new Rect2(0f, 0f, Size.X, Size.Y * 0.34f);
        DrawRect(glow, new Color(0.13f, 0.17f, 0.31f, 0.45f), true);
    }

    private void DrawEndBackground()
    {
        var fade = new Rect2(0f, 0f, Size.X, Size.Y);
        DrawRect(fade, new Color(0.08f, 0.10f, 0.16f, 0.82f), true);
    }

    private void DrawCombat()
    {
        if (_deck is null)
        {
            return;
        }

        LayoutCombatRects();
        DrawPanel(_topPanel);
        DrawPanel(_logPanel);

        DrawTextLeft("SCOUNDREL | Godot C# | Deck / Sala / Arma", _topPanel.Position.X + 16f, _topPanel.Position.Y + 8f, 28, SubtextColor);
        DrawTextLeft($"HP {_player.Hp}/{_player.MaxHp}", _topPanel.Position.X + 16f, _topPanel.Position.Y + 38f, 24, TextColor);

        var hpBarBg = new Rect2(_topPanel.Position.X + 146f, _topPanel.Position.Y + 44f, 210f, 16f);
        DrawRect(hpBarBg, new Color(0.24f, 0.24f, 0.30f), true);
        var ratio = _player.Hp / (float)_player.MaxHp;
        var hpBar = hpBarBg;
        hpBar.Size = new Vector2(hpBar.Size.X * ratio, hpBar.Size.Y);
        DrawRect(hpBar, ratio > 0.45f ? new Color(0.31f, 0.80f, 0.49f) : new Color(0.90f, 0.50f, 0.34f), true);

        var weaponText = $"Arma {_player.WeaponPower}";
        if (_player.WeaponLastSlain is not null)
        {
            weaponText += $" | limite <= {_player.WeaponLastSlain.Value}";
        }
        DrawTextLeft(weaponText, _topPanel.Position.X + 370f, _topPanel.Position.Y + 38f, 22, TextColor);
        DrawTextLeft(
            $"Sala {_roomIndex}  Escolhas {_cardsTakenThisRoom}/{_cardsRequiredThisRoom}  Dungeon {_deck.Remaining}",
            _topPanel.Position.X + 16f,
            _topPanel.Position.Y + 68f,
            22,
            TextColor);

        DrawSlotOutline(_deckSlotRect, new Color(1f, 0.25f, 0.82f));
        DrawSlotOutline(_weaponSlotRect, new Color(0.15f, 0.49f, 1f));
        for (var i = 0; i < _roomSlotRects.Length; i++)
        {
            DrawSlotOutline(_roomSlotRects[i], new Color(0.20f, 0.95f, 0.32f));
        }

        if (_deck.Remaining > 0)
        {
            DrawDeckBack(_deckSlotRect);
        }
        else
        {
            DrawRect(_deckSlotRect, new Color(0.14f, 0.16f, 0.23f), true);
            DrawTextCentered("VAZIO", _deckSlotRect, 16, SubtextColor);
        }
        DrawTextCentered($"DECK ({_deck.Remaining})", new Rect2(_deckSlotRect.Position.X - 30f, _deckSlotRect.Position.Y - 26f, _deckSlotRect.Size.X + 60f, 20f), 16, new Color(1f, 0.80f, 0.95f));

        var equippedCard = EquippedWeaponCard();
        if (equippedCard is null)
        {
            DrawRect(_weaponSlotRect, new Color(0.09f, 0.12f, 0.20f), true);
            DrawRect(_weaponSlotRect, new Color(0.17f, 0.26f, 0.46f), false, 2f);
            DrawTextCentered("SEM ARMA", _weaponSlotRect, 20, new Color(0.74f, 0.79f, 0.90f));
        }
        else
        {
            DrawCardAtRect(equippedCard.Value, _weaponSlotRect, true, false);
        }
        DrawTextCentered("ESPADA EQUIPADA", new Rect2(_weaponSlotRect.Position.X - 20f, _weaponSlotRect.End.Y + 4f, _weaponSlotRect.Size.X + 40f, 20f), 16, new Color(0.68f, 0.85f, 1f));

        var canInteract = _resolveTimer <= 0f && _player.Hp > 0 && !IsDealAnimationActive();
        for (var i = 0; i < _roomCards.Count; i++)
        {
            if (_roomCards[i].IsResolving)
            {
                continue;
            }
            DrawRoomCard(_roomCards[i], canInteract);
        }

        if (_resolvingCard is not null && _roomCards.Contains(_resolvingCard))
        {
            DrawRoomCard(_resolvingCard, canInteract);
        }

        DrawTextLeft("LOG", _logPanel.Position.X + 14f, _logPanel.Position.Y + 8f, 24, new Color(0.41f, 0.64f, 1f));
        var logY = _logPanel.Position.Y + 38f;
        var maxLines = Math.Min(3, _logs.Count);
        for (var i = 0; i < maxLines; i++)
        {
            DrawTextLeft(_logs[i], _logPanel.Position.X + 14f, logY, 20, TextColor);
            logY += 20f;
        }

        DrawTextRight(
            "Click esq monstro=arma | dir=mao nua | R reinicia | F11 fullscreen",
            _logPanel.End.X - 14f,
            _logPanel.Position.Y + 8f,
            20,
            SubtextColor);
    }

    private void DrawRoomCard(CardViewState view, bool enabled)
    {
        var rect = view.DrawRect(_cardSize);
        DrawCardAtRect(view.Card, rect, enabled, enabled && view.Hovered);
    }

    private void DrawCardAtRect(CardData card, Rect2 rect, bool enabled, bool hovered)
    {
        var shadow = rect;
        shadow.Position += new Vector2(0f, 8f);
        DrawRect(shadow, new Color(0.03f, 0.04f, 0.06f, 0.85f), true);

        DrawRect(rect, new Color(0.93f, 0.95f, 0.98f), true);
        DrawRect(rect, new Color(0.08f, 0.10f, 0.17f), false, 3f);

        var suitColor = card.Suit is SuitType.Hearts or SuitType.Diamonds
            ? new Color(0.77f, 0.20f, 0.30f)
            : new Color(0.13f, 0.15f, 0.22f);
        DrawTextLeft(card.ShortName, rect.Position.X + 8f, rect.Position.Y + 6f, 16, suitColor);

        var topTag = new Rect2(rect.Position.X + 8f, rect.Position.Y + 10f, rect.Size.X - 16f, 24f);
        DrawRect(topTag, new Color(0.95f, 0.97f, 0.99f), true);
        DrawRect(topTag, new Color(0.19f, 0.22f, 0.31f), false, 2f);
        DrawTextCentered(CardTypeTitle(card), topTag, 16, TypeColor(card));

        var iconArea = new Rect2(rect.Position.X + rect.Size.X * 0.30f, rect.Position.Y + rect.Size.Y * 0.36f, rect.Size.X * 0.40f, rect.Size.Y * 0.24f);
        DrawCardIcon(card.Type, iconArea);

        var detailTag = new Rect2(rect.Position.X + 8f, rect.End.Y - 36f, rect.Size.X - 16f, 28f);
        DrawRect(detailTag, new Color(0.95f, 0.97f, 0.99f), true);
        DrawRect(detailTag, new Color(0.19f, 0.22f, 0.31f), false, 2f);
        DrawTextCentered(CardDetail(card), detailTag, 16, new Color(0.12f, 0.14f, 0.21f));

        if (hovered)
        {
            DrawRect(rect.Grow(4f), new Color(0.52f, 0.76f, 1f), false, 3f);
        }

        if (!enabled)
        {
            DrawRect(rect, new Color(0.05f, 0.07f, 0.12f, 0.45f), true);
        }
    }

    private static string CardTypeTitle(CardData card)
    {
        return card.Type switch
        {
            CardType.Monster => "MONSTRO",
            CardType.Potion => "POCAO",
            _ => "ESPADA"
        };
    }

    private static string CardDetail(CardData card)
    {
        return card.Type switch
        {
            CardType.Monster => $"Dano {card.Value}",
            CardType.Potion => $"Cura {card.Value}",
            _ => $"Ataque {card.Value}"
        };
    }

    private static Color TypeColor(CardData card)
    {
        return card.Type switch
        {
            CardType.Monster => new Color(0.55f, 0.21f, 0.26f),
            CardType.Potion => new Color(0.18f, 0.46f, 0.33f),
            _ => new Color(0.20f, 0.33f, 0.59f)
        };
    }

    private void DrawCardIcon(CardType type, Rect2 area)
    {
        switch (type)
        {
            case CardType.Monster:
                DrawRect(area, new Color(0.27f, 0.33f, 0.50f), true);
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.20f, area.Position.Y + area.Size.Y * 0.30f, area.Size.X * 0.20f, area.Size.Y * 0.20f), new Color(0.95f, 0.96f, 0.98f), true);
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.60f, area.Position.Y + area.Size.Y * 0.30f, area.Size.X * 0.20f, area.Size.Y * 0.20f), new Color(0.95f, 0.96f, 0.98f), true);
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.30f, area.Position.Y + area.Size.Y * 0.68f, area.Size.X * 0.40f, area.Size.Y * 0.15f), new Color(0.10f, 0.12f, 0.17f), true);
                break;
            case CardType.Potion:
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.35f, area.Position.Y + area.Size.Y * 0.02f, area.Size.X * 0.30f, area.Size.Y * 0.18f), new Color(0.43f, 0.34f, 0.25f), true);
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.20f, area.Position.Y + area.Size.Y * 0.20f, area.Size.X * 0.60f, area.Size.Y * 0.72f), new Color(0.33f, 0.40f, 0.56f), true);
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.24f, area.Position.Y + area.Size.Y * 0.56f, area.Size.X * 0.52f, area.Size.Y * 0.30f), new Color(0.36f, 0.73f, 0.54f), true);
                break;
            case CardType.Weapon:
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.45f, area.Position.Y + area.Size.Y * 0.05f, area.Size.X * 0.10f, area.Size.Y * 0.68f), new Color(0.82f, 0.86f, 0.93f), true);
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.28f, area.Position.Y + area.Size.Y * 0.66f, area.Size.X * 0.44f, area.Size.Y * 0.12f), new Color(0.73f, 0.58f, 0.34f), true);
                DrawRect(new Rect2(area.Position.X + area.Size.X * 0.42f, area.Position.Y + area.Size.Y * 0.76f, area.Size.X * 0.16f, area.Size.Y * 0.20f), new Color(0.44f, 0.31f, 0.19f), true);
                break;
        }
    }

    private void DrawPanel(Rect2 rect)
    {
        DrawRect(rect, PanelColor, true);
        DrawRect(rect, BorderColor, false, 3f);
    }

    private void DrawSlotOutline(Rect2 rect, Color color)
    {
        DrawRect(rect.Grow(4f), color, false, 3f);
    }

    private void DrawDeckBack(Rect2 rect)
    {
        DrawRect(rect, new Color(0.14f, 0.14f, 0.28f), true);
        DrawRect(rect, new Color(0.05f, 0.06f, 0.10f), false, 3f);

        var inner = rect.Grow(-12f);
        DrawRect(inner, new Color(0.22f, 0.25f, 0.47f), true);
        DrawRect(inner, new Color(0.09f, 0.11f, 0.20f), false, 2f);

        var cell = Mathf.Max(5f, rect.Size.X / 12f);
        for (var y = inner.Position.Y + 4f; y < inner.End.Y - 2f; y += cell)
        {
            for (var x = inner.Position.X + 4f; x < inner.End.X - 2f; x += cell)
            {
                var index = ((int)((x + y) / cell)) % 2;
                var color = index == 0 ? new Color(0.36f, 0.39f, 0.69f) : new Color(0.29f, 0.32f, 0.58f);
                DrawRect(new Rect2(x, y, Mathf.Max(3f, cell - 2f), Mathf.Max(3f, cell - 2f)), color, true);
            }
        }
    }

    private CardData? EquippedWeaponCard()
    {
        if (_player.WeaponPower <= 0)
        {
            return null;
        }
        var rank = _player.WeaponPower == 14 ? 1 : Mathf.Clamp(_player.WeaponPower, 1, 13);
        return new CardData(SuitType.Diamonds, rank);
    }

    private static Rect2 RectFromCenter(Vector2 center, Vector2 size)
    {
        return new Rect2(center - size / 2f, size);
    }

    private void DrawTextLeft(string text, float x, float y, int fontSize, Color color)
    {
        DrawString(ThemeDB.FallbackFont, new Vector2(x, y + fontSize), text, HorizontalAlignment.Left, -1f, fontSize, color);
    }

    private void DrawTextRight(string text, float xRight, float y, int fontSize, Color color)
    {
        var width = xRight - _logPanel.Position.X;
        DrawString(
            ThemeDB.FallbackFont,
            new Vector2(_logPanel.Position.X, y + fontSize),
            text,
            HorizontalAlignment.Right,
            width,
            fontSize,
            color
        );
    }

    private void DrawTextCentered(string text, Rect2 rect, int fontSize, Color color)
    {
        var baseline = rect.Position.Y + (rect.Size.Y + fontSize) * 0.5f - 2f;
        DrawString(ThemeDB.FallbackFont, new Vector2(rect.Position.X, baseline), text, HorizontalAlignment.Center, rect.Size.X, fontSize, color);
    }
}
