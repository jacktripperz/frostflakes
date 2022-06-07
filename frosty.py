import json
import time
import contract as c
import cyclemanager as cmanager
from datetime import datetime,timedelta
import time
import json

dm_contract_addr = "0xAA1E1Ea6E32888A67D37c87FCcd19B5414ac2398"
loop_sleep_seconds = 2
start_polling_threshold_in_seconds = 0

# load private key
wallet_private_key = open('key.txt', "r").readline().strip().strip('\'').strip('\"').strip()

# load public address
wallet_public_addr = open('pa.txt', "r").readline().strip().strip('\'').strip('\"').strip()

# load abi
f = open('abi.json')
dm_abi = json.load(f)

# create contract
dm_contract = c.connect_to_contract(dm_contract_addr, dm_abi)

# create cycle
cycle = cmanager.build_cycle_from_config()

# methods
def compound():
    txn = dm_contract.functions.freeze().buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def claim():
    txn = dm_contract.functions.defrost().buildTransaction(c.get_tx_options(wallet_public_addr, 500000))
    return c.send_txn(txn, wallet_private_key)

def myRewards():
    total = dm_contract.functions.getBnbRewards(wallet_public_addr).call()
    return total

def lockedFrostFlakes():
    total = dm_contract.functions.getLockedFrostFlakes(wallet_public_addr).call()
    return total

def buildTimer(t):
    mins, secs = divmod(int(t), 60)
    hours, mins = divmod(int(mins), 60)
    timer = '{:02d} hours, {:02d} minutes, {:02d} seconds'.format(hours, mins, secs)
    return timer

def countdown(t):
    while t:
        print(f"Next poll in: {buildTimer(t)}", end="\r")
        time.sleep(1)
        t -= 1

def findCycleMinimumBnb(cycleId):
    for x in cycle:
        if x.id == cycleId:
            return x.minimumBnb
            break
        else:
            x = None

def findCycleType(cycleId):
    for x in cycle:
        if x.id == cycleId:
            return x.type
            break
        else:
            x = None

def findCycleEndTimerAt(cycleId):
    for x in cycle:
        if x.id == cycleId:
            return x.endTimerAt
            break
        else:
            x = None

def calcNextCycleId(currentCycleId):
    cycleLength = len(cycle)
    if currentCycleId == cycleLength:
        return 1
    else:
        newCycleId = currentCycleId + 1
        return newCycleId

def seconds_until_cycle(endTimerAt):
    time_delta = datetime.combine(
        datetime.now().date(), datetime.strptime(endTimerAt, "%H:%M").time()
    ) - datetime.now()
    return time_delta.seconds

# create infinate loop that checks contract every set sleep time
nextCycleId = cmanager.getNextCycleId()
nextCycleType = findCycleType(nextCycleId)
retryCount = 0

def itterate():
    global nextCycleId
    global nextCycleType
    cycleMinimumBnb = findCycleMinimumBnb(nextCycleId)
    nextCycleTime = findCycleEndTimerAt(nextCycleId)
    secondsUntilCycle = seconds_until_cycle(nextCycleTime)
    my_rewards = myRewards()
    locked_frostFlakes = lockedFrostFlakes()

    dateTimeObj = datetime.now()
    timestampStr = dateTimeObj.strftime("[%d-%b-%Y (%H:%M:%S)]")

    sleep = loop_sleep_seconds 
    
    print("********** FrostFlakes *******")
    print(f"{timestampStr} Next cycle id: {nextCycleId}")
    print(f"{timestampStr} Next cycle type: {nextCycleType}")
    print(f"{timestampStr} Next cycle time: {nextCycleTime}")
    print(f"{timestampStr} My locked frostflakes: {locked_frostFlakes}")
    print(f"{timestampStr} Payout available for compound/claim: {my_rewards:.8f} BNB")
    print(f"{timestampStr} Minimum set for compound/claim: {cycleMinimumBnb:.8f} BNB")
    print("******************************")

    if secondsUntilCycle > start_polling_threshold_in_seconds:
        sleep = secondsUntilCycle - start_polling_threshold_in_seconds

    countdown(int(sleep))

    payoutTocompound = payout_to_compound()

    if payoutTocompound >= cycleMinimumBnb:
        if nextCycleType == "freeze":
            compound()
        if nextCycleType == "defrost":
            claim()
        
        if nextCycleType == "freeze":
            print("********** COMPOUNDED *******")
            print(f"{timestampStr} COMPOUNDED {my_rewards:.8f} BNB to the pool!")
        if nextCycleType == "defrost":
            print("********** CLAIMED ***********")
            print(f"{timestampStr} CLAIMED {my_rewards:.8f} BNB!")
        
        print("**************************")

        print(f"{timestampStr} Sleeping for 1 min until next cycle starts..")
        countdown(60)

    print("********** IDLE ***********")
    calculatedNextCycleId = calcNextCycleId(nextCycleId)
    cmanager.updateNextCycleId(calculatedNextCycleId)
    nextCycleId = cmanager.getNextCycleId()
    nextCycleType = findCycleType(nextCycleId)
    print(f"{timestampStr} Available compound/claim did not meet the minimum requirements")
    print(f"{timestampStr} Moving on to next cycle")
    print(f"{timestampStr} Next cycleId is: {nextCycleId}")
    print(f"{timestampStr} Next cycle type will be: {nextCycleType}")
    print("**************************")
 
def run(): 
    global retryCount
    try: 
        itterate()
        run()
    except Exception as e:
        retryCount = retryCount + 1
        print("********* EXCEPTION *****************")
        print("Something went wrong! Message:")
        print(f"{e}")
        if retryCount < 5:
            print(f"[EXCEPTION] Retrying! (retryCount: {retryCount})")
            print("*************************************")
            run()
        else:
            print("********* TERMINATING *****************")
            print("Expection occurred 5 times. Terminating!")

run()
