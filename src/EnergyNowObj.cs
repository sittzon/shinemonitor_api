using System;
using System.Text.Json.Serialization;

namespace shinemonitor_api
{
    public class EnergyNowObj
    {
        // Do not serialize timestamp, only Date
        [JsonIgnore(Condition = JsonIgnoreCondition.WhenWritingNull)]
        public String TimeStamp { get; set; }
        public DateTime Date { get; set; }
        public int Energy { get; set; }
        public String Unit { get; set; }
    }
}