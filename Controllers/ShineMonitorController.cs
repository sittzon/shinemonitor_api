using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Text.Json;
using System.Text.Json.Serialization;

namespace shinemonitor_api.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class ShineMonitorController : ControllerBase
    {
        private readonly ILogger<ShineMonitorController> _logger;
        public ShineMonitorController(ILogger<ShineMonitorController> logger)
        {
            _logger = logger;
        }

        [HttpGet("/EnergyNow")]
        public EnergyNow GetEnergyNow()
        {
            //Data is sent to the server about every 5min
            //If not 5min has passed since last query, just send previous result
            var output = "python3 get_data.py --energyNow".Bash();
            //Console.WriteLine(output);
            _logger.LogDebug(output);
            try {
                EnergyNow e = JsonSerializer.Deserialize<EnergyNow>(output);
                e.Date = DateTime.ParseExact(e.TimeStamp, "yyyy-MM-dd HH:mm:ss",System.Globalization.CultureInfo.InvariantCulture);
                return e;
            } catch {
                _logger.LogError(output);
                throw new ArgumentException($"JSON serialisation error.");
            }
        }


        [HttpGet("/EnergySummary")]
        public EnergySummary GetEnergySummary()
        {
            var output = "python3 get_data.py --energySummary".Bash();
            _logger.LogDebug(output);
            try {
                EnergySummary e = JsonSerializer.Deserialize<EnergySummary>(output);
                return e;
            } catch {
                _logger.LogError(output);
                throw new ArgumentException($"JSON serialisation error.");
            }
        }

        [HttpGet("/Status")]
        public StatusObj GetStatus()
        {
            var output = "python3 get_data.py --status".Bash();
            _logger.LogDebug(output);
            try {
                StatusObj status = JsonSerializer.Deserialize<StatusObj>(output);
                return status;
            } catch {
                _logger.LogError(output);
                throw new ArgumentException($"JSON serialisation error.");
            }
        }

        [HttpGet("/Timeline")]
        public EnergyTimelineObj[] GetEnergyTimeline()
        {
            var output = "python3 get_data.py --energyTimeline".Bash();
            _logger.LogDebug(output);
            try {
                EnergyTimelineObj[] timeline = JsonSerializer.Deserialize<EnergyTimelineObj[]>(output);
                return timeline;
            } catch {
                _logger.LogError(output);
                throw new ArgumentException($"JSON serialisation error.");
            }
        }
    }
}