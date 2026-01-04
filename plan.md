1. Player submits a score

You receive:

    user_id

    beatmap_id

    hit counts (300/100/50/miss)

    accuracy

    raw score

    mods

    timestamp

2. Compute two internal values

These are internal calculations, not separate leaderboards.
A. normal_value

Whatever formula you choose (accuracy, score, star rating × accuracy, etc.).
B. custom_hit_value

Using your custom scoring:

    300 → 300

    100 → 285

    50 → 60

custom_hit_value=300n300+285n100+60n50
3. Collapse them into one value
final_value=max⁡(normal_value, custom_hit_value)

This is the only value stored for ranking.
4. Store the score

Database row contains:

    user_id

    beatmap_id

    final_value

    timestamp

    (optional) raw score, accuracy, hit counts for display

5. Leaderboards
Per‑beatmap leaderboard

Sort all scores for that beatmap by final_value.
Global ranking

For each player:

    Gather all their final_values

    Sort descending

    Take top 20

    Apply your weights:

        1.00, 0.95, 0.90, …, 0.05

    Sum them

This produces the player’s global rank score.
🎯 Result

You now have:

    One scoring system

    One leaderboard per map

    One global ranking

    No branching logic

    No separate tournament mode

    No server‑side decisions about which scoring to use

The server simply computes two values and keeps the better one — but the output is always a single unified number.