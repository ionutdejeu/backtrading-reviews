
def HL2(data):
    """Exponential moving average"""
    res= (data.High + data.Low) / 3
    return res