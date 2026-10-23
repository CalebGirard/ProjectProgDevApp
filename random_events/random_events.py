class random_eventer():

    # Pre-generates and schedules the full list of events before the simulation.
    # Minor events will affect only their stock.
    # Major events will affect their stock and the ones of the same tag(s). 
    # Global events will affect the whole market.
    # Impact coefficients can be positive or negative.

    # Types of minor events :
    # [CEO of x company] publicly supports [x candidate] from [x country].
    # [tbd]

    # Types of major events :
    # [tbd]

    # Types of global events :
    # [major country] attacks [major region]
    # [tbd]


    def __init__(self, chaos):
        self.event_list = None # dataframe
        self.chaos = chaos

    def generate_name():
        return

    def generate_impact():
        return