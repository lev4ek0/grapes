PERCENTAGE_COLOURS = {
    1: "#05CB04",
    0.9: "#34D901",
    0.8: "#67E300",
    0.7: "#ABF001",
    0.6: "#DCF901",
    0.5: "#FFFF02",
    0.4: "#FFCA01",
    0.3: "#FF9703",
    0.2: "#FF6700",
    0.1: "#FF4200",
    0.0: "#FF2E00",
}


def get_color_code_by_number(current_value: int, max_value: int, min_value: int):
    percentage = (current_value - min_value) / (max_value - min_value)
    return PERCENTAGE_COLOURS[round(1 - round(percentage, 1), 1)]
