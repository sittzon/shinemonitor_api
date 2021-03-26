using System;

namespace shinemonitor_api
{
    public class EnergyTimelineObj
    {
        public String Val { get; set; }
        public int Ts { get; set; }
    }

    public class EnergyTimeline
    {
        public EnergyTimelineObj[] Obj { get; set; }
    }
}