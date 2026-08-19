//+------------------------------------------------------------------+
//|                                        ExportM1History_EA.mq5     |
//|                              EA to export M1 OHLC via Tester      |
//|  Strategy Tester syncs ~1yr M1 data BEFORE FromDate.              |
//|  Use FromDate=2024.01.02 to get 2023 data.                        |
//+------------------------------------------------------------------+
#property copyright "StefanIS"
#property link      ""
#property version   "1.01"

//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
{
   string sym = _Symbol;

   int totalBars = Bars(sym, PERIOD_M1);
   datetime firstBarTime = (totalBars > 0) ? iTime(sym, PERIOD_M1, totalBars - 1) : 0;
   datetime lastBarTime  = (totalBars > 0) ? iTime(sym, PERIOD_M1, 0) : 0;

   Print("==============================================");
   Print("M1 Export for ", sym);
   Print("  Total M1 bars in cache: ", totalBars);
   Print("  Range: ", TimeToString(firstBarTime, TIME_DATE|TIME_MINUTES),
                   " -> ", TimeToString(lastBarTime, TIME_DATE|TIME_MINUTES));
   Print("==============================================");

   if(totalBars <= 0)
   {
      Print("ERROR: No M1 bars available.");
      return(INIT_SUCCEEDED);
   }

   // Export everything in cache
   string fileName = sym + "_M1_" +
                     StringSubstr(TimeToString(firstBarTime, TIME_DATE), 0, 10) + "_" +
                     StringSubstr(TimeToString(lastBarTime, TIME_DATE), 0, 10) + ".csv";
   StringReplace(fileName, ".", "");

   int handle = FileOpen(fileName, FILE_WRITE|FILE_CSV|FILE_COMMON, ",");
   if(handle == INVALID_HANDLE)
   {
      Print("ERROR: Cannot create file ", fileName, " Error: ", GetLastError());
      return(INIT_SUCCEEDED);
   }

   FileWrite(handle, "Datetime", "Open", "High", "Low", "Close", "Volume");

   int written = 0, skipped = 0;
   datetime prevBarTime = 0;
   int64_t maxGapSeconds = 0;
   datetime maxGapTime = 0;

   // Iterate oldest to newest: totalBars-1 down to 0
   for(int i = totalBars - 1; i >= 0; i--)
   {
      datetime barTime = iTime(sym, PERIOD_M1, i);
      double   barOpen  = iOpen(sym, PERIOD_M1, i);
      double   barHigh  = iHigh(sym, PERIOD_M1, i);
      double   barLow   = iLow(sym, PERIOD_M1, i);
      double   barClose = iClose(sym, PERIOD_M1, i);
      long     barVol   = iTickVolume(sym, PERIOD_M1, i);

      if(barTime == 0 || (barOpen == 0 && barHigh == 0 && barLow == 0 && barClose == 0))
      {
         skipped++;
         continue;
      }

      if(prevBarTime > 0)
      {
         int64_t gapSec = (int64_t)(barTime - prevBarTime);
         if(gapSec > 86400)
         {
            Print("  GAP: ", TimeToString(prevBarTime, TIME_DATE|TIME_MINUTES),
                  " -> ", TimeToString(barTime, TIME_DATE|TIME_MINUTES),
                  " (", gapSec / 3600, "h)");
            if(gapSec > maxGapSeconds)
            {
               maxGapSeconds = gapSec;
               maxGapTime = prevBarTime;
            }
         }
      }
      prevBarTime = barTime;

      string dt = TimeToString(barTime, TIME_DATE|TIME_SECONDS);
      FileWrite(handle, dt,
                DoubleToString(barOpen, 5),
                DoubleToString(barHigh, 5),
                DoubleToString(barLow, 5),
                DoubleToString(barClose, 5),
                IntegerToString(barVol));
      written++;

      if(written % 100000 == 0)
         Print("  ... ", written / 1000, "K bars written ...");
   }

   FileClose(handle);

   Print("==============================================");
   Print("EXPORT COMPLETE");
   Print("  File: Common\\Files\\", fileName);
   Print("  Bars written: ", written);
   Print("  Bars skipped: ", skipped);
   Print("  Actual range: ", TimeToString(firstBarTime, TIME_DATE|TIME_MINUTES),
                         " -> ", TimeToString(lastBarTime, TIME_DATE|TIME_MINUTES));
   if(maxGapSeconds > 0)
      Print("  Max gap: ", maxGapSeconds / 3600, "h at ",
            TimeToString(maxGapTime, TIME_DATE|TIME_MINUTES));
   Print("==============================================");

   return(INIT_SUCCEEDED);
}

void OnTick()
{
   ExpertRemove();
}
//+------------------------------------------------------------------+
