using System;

namespace shinemonitor_api
{
    public class EnergySummary
    {
        public double Today { get; set; }
        public double Month { get; set; }
        public double Year { get; set; }
        public double Total { get; set; }
        public String Unit { get; set; }
    }
}