import json
# cycle types are "freeze" or "defrost"

class Iteration: 
    def __init__(self, id, type, endTimerAt, minimumBnb): 
        self.id = id 
        self.type = type
        self.endTimerAt = endTimerAt
        self.minimumBnb = minimumBnb

def build_cycle_from_config():
    cycle = []
    cycle_file = open('cycle_config.json')
    cycle_json = json.load(cycle_file)
    for iteration in cycle_json['cycle']:
        iterationClass = Iteration(**iteration)
        cycle.append(iterationClass)
    return cycle

def getNextCycleId():
    cycle_file = open('cycle_config.json')
    cycle_json = json.load(cycle_file)
    return cycle_json['nextCycleId']

def updateNextCycleId(newId):
    with open("cycle_config.json", "r+") as cycle_file:
        data = json.load(cycle_file)

        # The change
        data['nextCycleId'] = newId

        cycle_file.seek(0)
        json.dump(data, cycle_file)
        cycle_file.truncate()
