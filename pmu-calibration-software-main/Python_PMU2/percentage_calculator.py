def calculate_percentage(x):

    if not (0x0000 <= x <= 0xFFFF): # making sure that the percentage is calculated between 0x0000 and 0xFFFF
        raise ValueError("Input value must be between 0x0000 and 0xFFFF")

    
    # Calculating the percentage
    percentage = (x / 0xFFFF)*100

    return percentage


        