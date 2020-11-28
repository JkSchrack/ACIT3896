import nurses
import schedule


def nurseRosterPopulator():
    count = 0
    for nurse in nurses:
        nurseData = [nurse, 0, 0, 0]
        nurseIndex[nurse] = count
        count += 1
        nurseRoster.append(nurseData)

def availability(day, shift, tempNurses):
    count = 0
    for n in range(len(nurseRoster)):
        nursesInfo = nurses[nurseRoster[n][0]]
        nurse = nurseRoster[n]
        if nurse[2] < 36 and nurse[3] == 0:
            if day not in nursesInfo["prefDays"]:
                nurse[1] += 3
            if shift not in nursesInfo["prefShift"]:
                nurse[1] += 2
            nurse[1] += 1
            tempNurses.append(nurse)
            nurseIndex[nurse[0]] = count
            count += 1
    return tempNurses


def week(day, shift, tempNurseRoster):
    tempAvailableNurses = availability(day, shift, tempNurseRoster)
    for i in range(len(days)):
        if (shift == "Day"):
            tempAvailableNurses = availability(day, shift, tempAvailableNurses)



if __name__ == "__main__":
    nurses = nurses.nurses
    schedule = schedule.schedule

    nurseIndex = {}
    nurseRoster = []
    days = ['Mon', 'Tues', 'Wed', 'Thur', 'Fri', 'Sat', 'Sun']
    shifts = ['Day', 'Tues']

    nurseRosterPopulator()

    week("Mon", "Day", nurseRoster)

    print("Hello World!")