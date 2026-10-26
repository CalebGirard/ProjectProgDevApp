class random_eventer():

    # Pre-generates and schedules the full list of events before the simulation.
    # Minor events will affect only their stock.
    # Major events will affect their stock and the ones of the same tag(s). 
    # Global events will affect the whole market.
    # Impact coefficients can be positive or negative.

    # Types of minor events :
    # [CEO of x company] publicly supports [x candidate] from [x country].
    # Employees of [x company] have started a strike !
    # {company} beats consensus quarterly earnings by {pct}% and raises full-year forward revenue guidance.
    # Patent office grants {company} exclusive 20-year rights to an unannounced proprietary technology.
    # Billionaire hedge fund manager discloses a {pct}% stake in {company} and demands immediate share buybacks.
    # Regulatory filing reveals {company} inflated subscription renewals and cash reserves for three quarters.
    # [tbd]

    # Types of major events :
    # Donald Trump announces [random %] of tariffs on all countries.
    # [tbd]

    # Types of global events :
    # [major country] attacks [major region]
    # [tbd]

    # Dataframe structure :
    # Turn count - Headline - Scope (Mi/Ma/Gl) - Impact

    # Lists of files : region/countries, ceos of companies, templates of events, list of tags


    def __init__(self, chaos):
        self.event_list = None # dataframe
        self.chaos = chaos

    def build_headline(scope):
        return

    def generate_impact():
        return

    def build_event(scope):
        return