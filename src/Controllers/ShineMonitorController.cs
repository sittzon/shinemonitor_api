using System;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Text.Json;

namespace shinemonitor_api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Produces("application/json")]
    public class ShineMonitorController : ControllerBase
    {
        private readonly ILogger<ShineMonitorController> _logger;
        #nullable enable
        private static EnergyNowObj? cachedEnergyNowObj = null;
        #nullable disable
        public ShineMonitorController(ILogger<ShineMonitorController> logger)
        {
            _logger = logger;
        }

        private DateTime handleDaylightSavingTime(DateTime d) {
            TimeZoneInfo time = TimeZoneInfo.Local;
            int addHours = 0;
            if (time.IsDaylightSavingTime(DateTime.Now)) {
                addHours = 1;
            }
            return d.AddHours(addHours);
        }

        [HttpGet("/EnergyNow")]
        public EnergyNowObj GetEnergyNow()
        {
            //Data from the inverter is sent to the server about every 5min
            //If not 4min has passed since last query, just send cached result
            if (cachedEnergyNowObj != null && DateTime.Now < cachedEnergyNowObj.Date.AddMinutes(4)) {
                _logger.LogDebug("DateTime.Now: "+DateTime.Now);
                _logger.LogDebug("cachedEnergyNowObj.Date.AddMinutes(4): "+cachedEnergyNowObj.Date.AddMinutes(4));
                _logger.LogDebug("Returning cached EnergyNowObj");
            }
            else {
                _logger.LogDebug("Calling python script get_data.py");
                var output = "python3 src/get_data.py --energyNow".Bash();
                _logger.LogDebug("Python output: "+output);
                try {
                    EnergyNowObj e = JsonSerializer.Deserialize<EnergyNowObj>(output);
                    e.Date = DateTime.ParseExact(e.TimeStamp, "yyyy-MM-dd HH:mm:ss",System.Globalization.CultureInfo.InvariantCulture);
                    e.Date = handleDaylightSavingTime(e.Date); // Compensate for daylight savings
                    e.TimeStamp = null; // Do not serialize timestamp, only Date
                    cachedEnergyNowObj = e;
                } catch(Exception e)  {
                    _logger.LogError(output);
                    cachedEnergyNowObj = null;
                    throw new ArgumentException(e.ToString());
                }
            }
            return cachedEnergyNowObj;
        }


        [HttpGet("/EnergySummary")]
        public EnergySummaryObj GetEnergySummary()
        {
            var output = "python3 src/get_data.py --energySummary".Bash();
            _logger.LogDebug(output);
            try {
                EnergySummaryObj e = JsonSerializer.Deserialize<EnergySummaryObj>(output);
                return e;
            } catch(Exception e)  {
                _logger.LogError(output);
                throw new ArgumentException(e.ToString());
            }
        }

        [HttpGet("/Status")]
        public StatusObj GetStatus()
        {
            var output = "python3 src/get_data.py --status".Bash();
            _logger.LogDebug(output);
            try {
                StatusObj status = JsonSerializer.Deserialize<StatusObj>(output);
                return status;
            } catch(Exception e) {
                _logger.LogError(output);
                throw new ArgumentException(e.ToString());
            }
        }

        [HttpGet("/Timeline")]
        public EnergyTimelineObj[] GetEnergyTimeline()
        {
            var output = "python3 src/get_data.py --energyTimeline".Bash();
            _logger.LogDebug(output);
            try {
                EnergyTimelineObj[] timeline = JsonSerializer.Deserialize<EnergyTimelineObj[]>(output);
                return timeline;
            } catch(Exception e) {
                _logger.LogError(output);
                throw new ArgumentException(e.ToString());
            }
        }
    }
}