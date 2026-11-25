"""Exploratory CFH-13 timing recalibration on new public decks."""
import frontier
from targeted import timed


def conservative(fn,args,expected):
    # The largest of nine one-call samples, with an extra 50% margin.
    _,samples=timed(fn,args,expected,repeats=9,inner=1)
    return (3*max(samples)+1)//2,samples


if __name__=='__main__':
    frontier.timed=conservative
    frontier.main()
