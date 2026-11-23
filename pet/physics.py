def fall_step(y, velocity, dt, floor):
    velocity = min(velocity + 1100 * dt, 1500)
    y += velocity * dt
    return (floor, 0.0, True) if y >= floor else (y, velocity, False)

def clamp(value, low, high):
    return max(low, min(value, max(low, high)))
