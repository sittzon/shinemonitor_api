using System;
using System.Text.Json.Serialization;

namespace shinemonitor_api
{
    public class EnergyNow
    {
       
        public String TimeStamp { get; set; }
        public DateTime Date { get; set; }
        public int Energy { get; set; }
        public String Unit { get; set; }
    }
}