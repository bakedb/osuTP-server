def calculate_normal_value(raw_score, accuracy, star_rating=None):
    """
    Calculate normal_value using a formula based on accuracy and score.
    Formula: raw_score * accuracy
    If star_rating is provided, we can incorporate it: raw_score * accuracy * star_rating
    """
    if star_rating:
        return raw_score * accuracy * star_rating
    return raw_score * accuracy

def calculate_custom_hit_value(count_300, count_100, count_50):
    """
    Calculate custom_hit_value using the custom scoring:
    300 → 300
    100 → 285
    50 → 60
    """
    return (count_300 * 300) + (count_100 * 285) + (count_50 * 60)

def calculate_final_value(normal_value, custom_hit_value):
    """
    Calculate final_value as the maximum of normal_value and custom_hit_value
    """
    return max(normal_value, custom_hit_value)

def calculate_global_rank_score(final_values):
    """
    Calculate global ranking score for a player.
    Takes top 20 scores and applies weights: 1.00, 0.95, 0.90, ..., 0.05
    """
    if not final_values:
        return 0.0
    
    # Sort descending and take top 20
    sorted_scores = sorted(final_values, reverse=True)[:20]
    
    # Apply weights: 1.00, 0.95, 0.90, ..., 0.05
    weights = [1.0 - (i * 0.05) for i in range(20)]
    
    # Calculate weighted sum
    weighted_sum = 0.0
    for i, score in enumerate(sorted_scores):
        if i < len(weights):
            weighted_sum += score * weights[i]
    
    return weighted_sum
