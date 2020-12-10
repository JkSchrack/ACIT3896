import nurses
import schedule
import copy
import random
import matplotlib.pyplot as plt


def nurseRosterPopulator():
    # Populates nurseRoster Array with nurses information
    count = 0
    for nurse in nurses:
        nurseData = [nurse, 0, 0, 0]
        nurseIndex[nurse] = count
        count += 1
        nurseRoster.append(nurseData)


def week(day, shift, roster):
    for i in range(len(days)):
        for n in range(len(shifts)):
            availableNurses = availability(day, shift, roster)
            # returns available nurses
            sortedNurses = pointSorter(availableNurses)
            # returns sorted version of availableNurses
            day, shift, roster = assign(day, shift, sortedNurses[0], sortedNurses[1], roster)
            # updates schedule and returns new day, shift, and roster


def availability(day, shift, roster):
    # Returns nurseRoster variant containing only nurses that are available and their assigned point values
    count = 0
    availableNurses = []
    for n in range(len(roster)):
        nursesInfo = nurses[roster[n][0]]
        nurse = roster[n]
        if nurse[2] < 36 and nurse[3] == 0:
            if day not in nursesInfo["prefDays"] and nursesInfo["prefDays"] != []:
                # Penalty if day is not preferred and preferred days is not empty
                nurse[1] += 3
            if shift != nursesInfo["prefShift"] and nursesInfo["prefShift"] != '':
                # Penalty if shift is not preferred and preferred shifts is not empty
                nurse[1] += 2
            if nursesInfo["prefCoworkers"]:
                # Pre-apply coworker penalty
                nurse[1] += 1
            availableNurses.append(nurse)
            nurseIndex[nurse[0]] = count
            count += 1
    return availableNurses


def pointSorter(availableNurses):
    # Bubble sort availableNurses by PointValue
    for i in range(len(availableNurses)):
        for n in range(i, len(availableNurses)):
            if availableNurses[n][1] < availableNurses[i][1]:
                tempNurse = availableNurses[i]
                tempIdx = nurseIndex[availableNurses[i][0]]
                nurseIndex[availableNurses[i][0]] = nurseIndex[availableNurses[n][0]]
                availableNurses[i] = availableNurses[n]
                nurseIndex[availableNurses[n][0]] = tempIdx
                availableNurses[n] = tempNurse
    return availableNurses


def updateRoster(nurse1, nurse2, roster):
    for i in range(len(roster)):
        nurse = roster[i]
        if nurse[0] == nurse1[0] or nurse[0] == nurse2[0]:
            # Assigned Nurses availability and hours updated
            roster[i][2] += 12
            roster[i][3] += 1
        elif roster[i][3] > 0:
            # 0 = available, 1 = unavailable, 2 = reset to available
            roster[i][3] += 1
        if roster[i][3] == 2:
            roster[i][3] = 0
        roster[i][1] = 0
    return roster


def assign(day, shift, nurse1, nurse2, roster):
    # assign nurse1 and nurse2 to schedule
    pointValue = nurse1[1] + nurse2[1]
    if nurse1[0] in nurses[nurse2[0]]["prefCoworkers"]:
        pointValue -= 1
    if nurse2[0] in nurses[nurse1[0]]["prefCoworkers"]:
        pointValue -= 1
    schedule["PointValue"] += pointValue
    # total point value of schedule
    schedule[day][shift] = [pointValue, nurse1[0], nurse2[0]]
    updatedNurses = updateRoster(nurse1, nurse2, roster)
    if shift == "Day":
        shift = "Night"
    else:
        schedule[day]["PointValue"] = schedule[day]["Day"][0] + schedule[day]["Night"][0]
        # total point value for each day
        if day == "Sun":
            day = "Mon"
            shift = "Day"
        else:
            day = days[days.index(day) + 1]
            shift = "Day"
    temp = [day, shift, updatedNurses]
    return temp


def tabu(day, shift, originalSchedule, initialRoster):
    best = copy.deepcopy(originalSchedule)
    tempSchedule = originalSchedule
    previousSchedule = []
    pv = [originalSchedule["PointValue"]]
    while previousSchedule != tempSchedule:
        previousSchedule = copy.deepcopy(tempSchedule)
        tempSchedule["PointValue"] = 0
        roster = copy.deepcopy(initialRoster)
        for i in range(len(days)):
            for n in range(len(shifts)):
                availableNurses = availability(day, shift, roster)
                sortedNurses = pointSorter(availableNurses)
                nurse1 = tempSchedule[day][shift][1]
                nurse2 = tempSchedule[day][shift][2]
                check1 = False
                check2 = False
                if nurse1 in nurseIndex:
                    nurse1 = sortedNurses[nurseIndex[nurse1]]
                    check1 = True
                if nurse2 in nurseIndex:
                    nurse2 = sortedNurses[nurseIndex[nurse2]]
                    check2 = True
                while not check1 or nurse1 == nurse2:
                    tempNurse = sortedNurses[random.randint(0, len(sortedNurses))]
                    if tempNurse != nurse2:
                        nurse1 = tempNurse
                        check1 = True
                while not check2 or nurse1 == nurse2:
                    tempNurse = sortedNurses[random.randint(0, len(sortedNurses))]
                    if tempNurse != nurse1:
                        nurse2 = tempNurse
                        check2 = True
                pointValue = nurse1[1] + nurse2[1]
                if nurse1[0] in nurses[nurse2[0]]["prefCoworkers"]:
                    pointValue -= 1
                if nurse2[0] in nurses[nurse1[0]]["prefCoworkers"]:
                    pointValue -= 1
                for nurse in sortedNurses:
                    prefCoworkers1 = nurses[nurse1[0]]["prefCoworkers"]
                    prefCoworkers2 = nurses[nurse2[0]]["prefCoworkers"]
                    prefCoworkers3 = nurses[nurse[0]]["prefCoworkers"]
                    if nurse[0] != nurse1[0] and nurse[0] != nurse2[0]:
                        if nurse[0] in prefCoworkers1 and nurse1[0] in prefCoworkers3:
                            if nurse[1] + nurse1[1] - 2 <= pointValue:
                                nurse1 = nurse1
                                nurse2 = nurse
                                pointValue = nurse[1] + nurse1[1] - 2
                        elif nurse[0] in prefCoworkers2 and nurse2[0] in prefCoworkers3:
                            if nurse[1] + nurse2[1] - 2 <= pointValue:
                                nurse1 = nurse
                                nurse2 = nurse2
                                pointValue = nurse[1] + nurse2[1] - 2
                        elif nurse[0] in prefCoworkers1 and nurse[0] != nurse2[0]:
                            if nurse[1] + nurse1[1] - 1 <= pointValue:
                                nurse1 = nurse1
                                nurse2 = nurse
                                pointValue = nurse[1] + nurse1[1] - 1
                        elif nurse[0] in prefCoworkers2 and nurse[0] != nurse1[0]:
                            if nurse[1] + nurse2[1] - 1 <= pointValue:
                                nurse1 = nurse
                                nurse2 = nurse2
                                pointValue = nurse[1] + nurse2[1] - 1
                day, shift, roster, tempSchedule = reassign(day, shift, nurse1, nurse2, roster, pointValue,
                                                            tempSchedule)
        pv.append(tempSchedule['PointValue'])
        if tempSchedule["PointValue"] < best["PointValue"]:
            best = copy.deepcopy(tempSchedule)
    return best, pv


def reassign(day, shift, nurse1, nurse2, roster, pointValue, tempSchedule):
    tempSchedule["PointValue"] += pointValue
    tempSchedule[day][shift] = [pointValue, nurse1[0], nurse2[0]]
    updatedNurses = updateRoster(nurse1, nurse2, roster)
    if shift == "Day":
        shift = "Night"
    else:
        tempSchedule[day]["PointValue"] = tempSchedule[day]["Day"][0] + tempSchedule[day]["Night"][0]
        if day == "Sun":
            day = "Mon"
            shift = "Day"
        else:
            day = days[days.index(day) + 1]
            shift = "Day"
    temp = [day, shift, updatedNurses, tempSchedule]
    return temp


# Returns False if check does not pass
# True if passes
def schedule_check(schedule_to_check):
    nurseDictionary = {}
    for i in nurses:
        nurseDictionary[i] = 0  # Hours worked, worked recently

    for index, key in enumerate(schedule_to_check):
        if key != 'PointValue':
            dayShift = schedule_to_check[key]['Day']
            nightShift = schedule_to_check[key]['Night']
            # make day 1 not check previous
            # if day, check night and previous night

            nurseDictionary[dayShift[1]] += 12
            nurseDictionary[dayShift[2]] += 12
            # day hours check 1
            if nurseDictionary[dayShift[1]] > 36:
                return False
            # day hours check 2
            if nurseDictionary[dayShift[2]] > 36:
                return False

            # recent check
            if index != 0:
                if dayShift[1] in schedule_to_check[days[index - 1]]['Night'] or dayShift[1] in nightShift:
                    return False
                if dayShift[2] in schedule_to_check[days[index - 1]]['Night'] or dayShift[2] in nightShift:
                    return False

            # if night, check day and next day (edge case of sunday)
            nurseDictionary[nightShift[1]] += 12
            nurseDictionary[nightShift[2]] += 12
            # night hours check 1
            if nurseDictionary[nightShift[1]] > 36:
                return False
            # night hours check 2
            if nurseDictionary[nightShift[2]] > 36:
                return False
            # recent check
            # on Sunday
            if index == 6:
                if nightShift[1] in dayShift:  # or nightShift[1] in schedule_to_check['Mon']['Day']:
                    return False
                if nightShift[2] in dayShift:  # or nightShift[2] in schedule_to_check['Mon']['Day']:
                    return False
            # every other day
            else:
                # if in today's DAY or tomorrow's DAY
                if nightShift[1] in dayShift or nightShift[1] in schedule_to_check[days[index + 1]]['Day']:
                    return False
                if nightShift[2] in dayShift or nightShift[2] in schedule_to_check[days[index + 1]]['Day']:
                    return False
    return True


# Replaces old at day-shift-pos with newNurse
def replace_nurse(target_schedule, day, shift, newNurse, pos):
    target_schedule[day][shift][pos] = newNurse[0]


# gets total points for
def pv_prefCoworker(nurse1, nurse2):
    pv = 0
    if nurse2 not in nurses[nurse1]['prefCoworkers'] and nurses[nurse1]['prefCoworkers'] != []:
        # print(nurse1 + ' doesnt prefer ' + nurse2)
        pv += 1
    if nurse1 not in nurses[nurse2]['prefCoworkers'] and nurses[nurse2]['prefCoworkers'] != []:
        # print(nurse2 + ' doesnt prefer ' + nurse1)
        pv += 1
    return pv


def pv_prefDaysShifts(day, shift, nurse):
    pv = 0
    if day not in nurses[nurse]['prefDays'] and nurses[nurse]['prefDays'] != []:
        # print(nurse + ' doesnt prefer ' + day)
        pv += 3
    if shift != nurses[nurse]['prefShift'] and nurses[nurse]['prefShift'] != '':
        # print(nurse + ' doesnt prefer ' + shift)
        pv += 2
    return pv


def set_pv_schedule(target_schedule):
    totalPv = 0
    for i in range(0, len(days)):
        dayPv = 0
        for n in range(0, len(shifts)):
            target_shift = target_schedule[days[i]][shifts[n]]
            # print("current day: {}, current shift: {}".format(days[i], shifts[n]))
            nurse1 = target_shift[1]
            nurse2 = target_shift[2]
            pv1 = pv_prefCoworker(nurse1, nurse2)
            pv2 = pv_prefDaysShifts(days[i], shifts[n], nurse1)
            pv3 = pv_prefDaysShifts(days[i], shifts[n], nurse2)
            dayPv += pv1
            dayPv += pv2
            dayPv += pv3
            shiftPv = pv1 + pv2 + pv3
            target_schedule[days[i]][shifts[n]][0] = shiftPv
            # print("current day: {}, current shift: {}, pv: {}".format(days[i], shifts[n], dayPv))
        totalPv += dayPv
        target_schedule[days[i]]['PointValue'] = dayPv
    target_schedule['PointValue'] = totalPv


def genetic(target_schedule):
    best = target_schedule['PointValue']
    bestSchedule = copy.deepcopy(target_schedule)
    testSchedule = copy.deepcopy(target_schedule)
    iterations = 0
    errorCheck = 0
    rosterSize = len(nurseRoster)
    pv = [best]
    while iterations < 1000 and errorCheck < 10:
        lastSchedule = copy.deepcopy(bestSchedule)
        nurse1 = nurseRoster[random.randrange(0, rosterSize)]
        nurse2 = nurseRoster[random.randrange(0, rosterSize)]
        while nurse2 == nurse1:
            nurse2 = nurseRoster[random.randrange(0, rosterSize)]
        swap = False
        for i in range(0, len(days)):
            for n in range(0, len(shifts)):
                rand = random.randint(0, 1)
                if rand == 1:
                    nurse = testSchedule[days[i]][shifts[n]][n + 1]
                    if nurse == nurse1[0]:
                        # switch in original schedule
                        replace_nurse(testSchedule, days[i], shifts[n], nurse2, n + 1)
                        swap = True
                    elif nurse == nurse2[0]:
                        replace_nurse(testSchedule, days[i], shifts[n], nurse1, n + 1)
                        swap = True
        if schedule_check(testSchedule) and swap:
            set_pv_schedule(testSchedule)
            iterations += 1
            pv.append(testSchedule['PointValue'])
            errorCheck = 0
            if testSchedule['PointValue'] < best:
                best = testSchedule['PointValue']
                bestSchedule = copy.deepcopy(testSchedule)
        elif schedule_check(testSchedule) and not swap:
            testSchedule = copy.deepcopy(lastSchedule)
            continue
        else:
            errorCheck += 1
            testSchedule = copy.deepcopy(lastSchedule)
    return bestSchedule, pv


if __name__ == "__main__":
    nurses = nurses.nurses
    schedule = schedule.schedule

    nurseIndex = {}
    nurseRoster = []
    days = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
    shifts = ['Day', 'Night']

    nurseRosterPopulator()


    week("Mon", "Day", copy.deepcopy(nurseRoster))

    tomato = tabu("Mon", "Day", copy.deepcopy(schedule), copy.deepcopy(nurseRoster))

    pv = tomato[1]
    plt.xlabel('Valid Schedules')
    plt.ylabel('Fitness Points')
    plt.plot(pv)
    plt.show()

    gen = genetic(copy.deepcopy(tomato[0]))

    print(schedule["PointValue"])
    print(schedule["Mon"])
    print(schedule["Tues"])
    print(schedule["Wed"])
    print(schedule["Thur"])
    print(schedule["Fri"])
    print(schedule["Sat"])
    print(schedule["Sun"])

    print(gen[0]["PointValue"])
    print(gen[0]["Mon"])
    print(gen[0]["Tues"])
    print(gen[0]["Wed"])
    print(gen[0]["Thur"])
    print(gen[0]["Fri"])
    print(gen[0]["Sat"])
    print(gen[0]["Sun"])

    print(tomato[0]["PointValue"])
    print(tomato[0]["Mon"])
    print(tomato[0]["Tues"])
    print(tomato[0]["Wed"])
    print(tomato[0]["Thur"])
    print(tomato[0]["Fri"])
    print(tomato[0]["Sat"])
    print(tomato[0]["Sun"])

    pv = gen[1]
    plt.xlabel('Valid Schedules')
    plt.ylabel('Fitness Points')
    plt.plot(pv)
    plt.show()

