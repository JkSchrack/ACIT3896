import nurses
import schedule


def nurseRosterPopulator():
    count = 0
    for nurse in nurses:
        nurseData = [nurse, 0, 0, 0]
        nurseIndex[nurse] = count
        count += 1
        nurseRoster.append(nurseData)


def availability(day, shift, nurseRoster):
    tempAvailableNurses = []
    for n in range(len(nurseRoster)):
        nursesInfo = nurses[nurseRoster[n][0]]
        nurse = nurseRoster[n]
        if nurse[2] < 36 and nurse[3] == 0:
            if day not in nursesInfo["prefDays"]:
                nurse[1] += 3
            if shift not in nursesInfo["prefShift"]:
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


def updateRoster(nurse1, nurse2, nurseRoster):
    for i in range(len(nurseRoster)):
        nurse = nurseRoster[i]
        if nurse[0] == nurse1[0] or nurse[0] == nurse2[0]:
            nurseRoster[i][2] += 12
            nurseRoster[i][3] += 1
        elif nurseRoster[i][3] > 0:
            nurseRoster[i][3] += 1
        if nurseRoster[i][3] == 2:
            nurseRoster[i][3] = 0
        nurseRoster[i][1] = 0
    return nurseRoster


def assign(day, shift, nurse1, nurse2, nurseRoster):
    pointValue = nurse1[1] + nurse2[1]
    if nurse1[0] in nurses[nurse2[0]]["prefCoworkers"]:
        pointValue -= 1
    if nurse2[0] in nurses[nurse1[0]]["prefCoworkers"]:
        pointValue -= 1
    schedule["PointValue"] += pointValue
    schedule[day][shift] = [pointValue, nurse1[0], nurse2[0]]
    updatedNurses = updateRoster(nurse1, nurse2, nurseRoster)
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


def week(day, shift, nurseRoster):
    for i in range(len(days)):
        for n in range(len(shifts)):
            availableNurses = availability(day, shift, nurseRoster)
            sortedNurses = pointSorter(availableNurses)
            nurse1 = sortedNurses[0]
            nurse2 = sortedNurses[1]
            temp = assign(day, shift, nurse1, nurse2, nurseRoster)
            day = temp[0]
            shift = temp[1]
            nurseRoster = temp[2]


if __name__ == "__main__":
    nurses = nurses.nurses
    schedule = schedule.schedule

    nurseIndex = {}
    nurseRoster = []
    days = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
    shifts = ['Day', 'Tues']

    nurseRosterPopulator()

    week("Mon", "Day", nurseRoster)
    print(schedule)

    print("Hello World!")