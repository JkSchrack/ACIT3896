import nurses
import schedule


def nurseRosterPopulator():
    count = 0
    for nurse in nurses:
        nurseData = [nurse, 0, 0, 0]
        nurseIndex[nurse] = count
        count += 1
        nurseRoster.append(nurseData)


def availability(day, shift, roster):
    tempAvailableNurses = []
    for n in range(len(roster)):
        nursesInfo = nurses[roster[n][0]]
        nurse = roster[n]
        if nurse[2] < 36 and nurse[3] == 0:
            if day not in nursesInfo["prefDays"] and nursesInfo["prefDays"] != []:
                nurse[1] += 3
            if shift != nursesInfo["prefShift"] and nursesInfo["prefShift"] != '':
                nurse[1] += 2
            nurse[1] += 1
            tempAvailableNurses.append(nurse)
    return tempAvailableNurses


def pointSorter(unsortedNurses):
    for i in range(len(unsortedNurses)):
        for n in range(i, len(unsortedNurses)):
            if unsortedNurses[n][1] < unsortedNurses[i][1]:
                tempNurse = unsortedNurses[i]
                unsortedNurses[i] = unsortedNurses[n]
                unsortedNurses[n] = tempNurse
    return unsortedNurses


def updateRoster(nurse1, nurse2, roster):
    for i in range(len(roster)):
        nurse = roster[i]
        if nurse[0] == nurse1[0] or nurse[0] == nurse2[0]:
            roster[i][2] += 12
            roster[i][3] += 1
        elif roster[i][3] > 0:
            roster[i][3] += 1
        if roster[i][3] == 2:
            roster[i][3] = 0
        roster[i][1] = 0
    return roster


def assign(day, shift, nurse1, nurse2, roster, pointValue):
    schedule["PointValue"] += pointValue
    schedule[day][shift] = [pointValue, nurse1[0], nurse2[0]]
    updatedNurses = updateRoster(nurse1, nurse2, roster)
    if shift == "Day":
        shift = "Night"
    else:
        schedule[day]["PointValue"] = schedule[day]["Day"][0] + schedule[day]["Night"][0]
        if day == "Sun":
            day = "Mon"
        else:
            day = days[days.index(day) + 1]
            shift = "Day"
    temp = [day, shift, updatedNurses]
    return temp


def week(day, shift, roster):
    for i in range(len(days)):
        for n in range(len(shifts)):
            availableNurses = availability(day, shift, roster)
            sortedNurses = pointSorter(availableNurses)
            nurse1 = sortedNurses[0]
            nurse2 = sortedNurses[1]
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
            temp = assign(day, shift, nurse1, nurse2, roster, pointValue)
            day = temp[0]
            shift = temp[1]
            roster = temp[2]


def stopCondition(best):
    if best == 0:
            return True


def tabu(day, shift, schedule, initialRoster):
    tabuList = []
    best = schedule["PointValue"]
    tempSchedule = schedule
    tempSchedule["PointValue"] = 0
    while len(tabuList) < 10:
        roster = initialRoster
        for i in range(len(days)):
            for n in range(len(shifts)):
                availableNurses = availability(day, shift, roster)
                print(availableNurses)
                sortedNurses = pointSorter(availableNurses)
                nurse1 = tempSchedule[day][shift][1]
                nurse2 = tempSchedule[day][shift][2]
                prefCoworkers1 = nurses[nurse1]["prefCoworkers"]
                prefCoworkers2 = nurses[nurse2]["prefCoworkers"]
                newPv = tempSchedule[day][shift][0]
                for nurse in sortedNurses:
                    prefCoworkers3 = nurses[nurse[0]]["prefCoworkers"]
                    if nurse1[0] in prefCoworkers3 and nurse[0] in prefCoworkers1 and nurse[0] != nurse2[0]:
                        if nurse[1] + nurse1[1] - 2 <= newPv:
                            nurse11 = nurse
                            nurse22 = nurse1
                    elif nurse2[0] in prefCoworkers3 and nurse[0] in prefCoworkers2 and nurse[0] != nurse1[0]:
                        if nurse[1] + nurse2[1] - 2 <= newPv:
                            nurse11 = nurse
                            nurse22 = nurse2
                    elif nurse[0] in prefCoworkers1 and nurse[0] != nurse2[0]:
                        if nurse[1] + nurse1[1] - 1 <= newPv:
                            nurse11 = nurse
                            nurse22 = nurse1
                    elif nurse[0] in prefCoworkers2 and nurse[0] != nurse1[0]:
                        if nurse[1] + nurse2[1] - 1 <= newPv:
                            nurse11 = nurse
                            nurse22 = nurse2
                temp = assign(day, shift, nurse11, nurse22, roster)
                day = temp[0]
                shift = temp[1]
                roster = temp[2]
            if (tempSchedule["PointValue"] < best):
                best = tempSchedule["PointValue"]
        tabuList.append(tempSchedule)
    for each in tabuList:
        print(each)

if __name__ == "__main__":
    nurses = nurses.nurses
    schedule = schedule.schedule

    nurseIndex = {}
    nurseRoster = []
    days = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
    shifts = ['Day', 'Night']

    nurseRosterPopulator()

    week("Mon", "Day", nurseRoster)

    #nurseRoster = []
    #nurseRosterPopulator()

    #tabu("Mon", "Day", schedule, nurseRoster)

    print(schedule["PointValue"])
    print(schedule["Mon"])
    print(schedule["Tues"])
    print(schedule["Wed"])
    print(schedule["Thur"])
    print(schedule["Fri"])
    print(schedule["Sat"])
    print(schedule["Sun"])

    print("Hello World!")