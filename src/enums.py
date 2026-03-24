from enum import Enum

#action = :
#queryPlantCurrentData - Returns json summary of energy generated
#queryPlantActiveOuputPowerOneDay - (Misspelled in API) Returns json data used in shinemonitor for displaying today graph over generated energy
#queryDeviceDataOneDayPaging - Returns various json data, ex. energy generated now
#queryPlantDeviceDesignatedInformation - Return for example offline/online status of inverter
class Action(Enum):
    SUMMARY = "queryPlantCurrentData"
    TIMELINE_DAY = "queryPlantActiveOuputPowerOneDay"
    TIMELINE_MONTH = "queryPlantEnergyMonthPerDay"
    TIMELINE_YEAR = "queryPlantEnergyYearPerMonth"
    TIMELINE_TOTAL = "queryPlantEnergyTotalPerYear"
    PLANT_INFO = "queryPlantInfo"
    ENERGY_TODAY = "queryDeviceDataOneDayPaging"
    STATUS = "queryPlantDeviceDesignatedInformation"
