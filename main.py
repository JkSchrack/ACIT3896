import nurses
import schedule
import copy
import random

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
            if nursesInfo["prefCoworkers"] != []:
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
    count = 0
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
                while not check1:
                    tempNurse = sortedNurses[random.randint(0, len(sortedNurses))]
                    if tempNurse != nurse2:
                        nurse1 = tempNurse
                        check1 = True
                        print("check1")
                while not check2:
                    tempNurse = sortedNurses[random.randint(0, len(sortedNurses))]
                    if tempNurse != nurse1:
                        nurse2 = tempNurse
                        check2 = True
                        print("check2")
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
                day, shift, roster, tempSchedule = reassign(day, shift, nurse1, nurse2, roster, pointValue, tempSchedule)
        if tempSchedule["PointValue"] < best["PointValue"]:
            best = copy.deepcopy(tempSchedule)
    return best


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


def stopCondition(best):
    if best == 0:
        return True


if __name__ == "__main__":
    nurses = nurses.nurses
    schedule = schedule.schedule

    nurseIndex = {}
    nurseRoster = []
    days = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
    shifts = ['Day', 'Night']

    nurseRosterPopulator()

    week("Mon", "Day", copy.deepcopy(nurseRoster))

    best = tabu("Mon", "Day", copy.deepcopy(schedule), copy.deepcopy(nurseRoster))

    print(schedule["PointValue"])
    print(schedule["Mon"])
    print(schedule["Tues"])
    print(schedule["Wed"])
    print(schedule["Thur"])
    print(schedule["Fri"])
    print(schedule["Sat"])
    print(schedule["Sun"])

    print(best["PointValue"])
    print(best["Mon"])
    print(best["Tues"])
    print(best["Wed"])
    print(best["Thur"])
    print(best["Fri"])
    print(best["Sat"])
    print(best["Sun"])

    print("Hello World!")
