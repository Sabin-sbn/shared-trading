//+------------------------------------------------------------------+
//|                                             ExportM1History_EA.mq5 |
//|  Exports ALL cached M1 bars to a CSV file via Strategy Tester.    |
//|                                                                   |
//|  HOW TO USE:                                                      |
//|   1. Compile this EA (MetaEditor -> F7).                          |
//|   2. Strategy Tester: Expert = ExportM1History_EA,                |
//|      Symbol = your pair, Period = M1  (CRITICAL),                 |
//|      Model = 0 (Every tick), Optimization = 0, Visual = 0.        |
//|   3. Output lands in the shared Common\Files folder               |
//|      (FILE_COMMON).                                               |
//|                                                                   |
//|  NOTE: Period=M1 makes the tester sync the maximum M1 history     |
//|  (~2.5 years). Use two passes with different FromDate to cover    |
//|  the full range (see download_m1.py).                             |
//+------------------------------------------------------------------+
#property copyright "Shared Trading Project"
#property version   "1.00"
#property strict

// Optional output filename override (set via TesterInputs in the .ini).
// Empty string -> auto name: "<SYM>_M1_full.csv"
input string InpFileName = "";

//+------------------------------------------------------------------+
//| Format a datetime as "YYYY-MM-DD HH:MM:SS" (hyphens, no dots)    |
//+------------------------------------------------------------------+
string FormatDateTime(datetime t)
  {
   MqlDateTime dt;
   TimeToStruct(t, dt);
   return StringFormat("%04d-%02d-%02d %02d:%02d:%02d",
                       dt.year, dt.mon, dt.day, dt.hour, dt.min, dt.sec);
  }

//+------------------------------------------------------------------+
int OnInit()
  {
   string fname = (InpFileName != "") ? InpFileName : (_Symbol + "_M1_full.csv");

   // FILE_COMMON writes to the shared Common\Files folder (easy to find).
   int handle = FileOpen(fname, FILE_WRITE | FILE_CSV | FILE_COMMON | FILE_ANSI, ',');
   if(handle == INVALID_HANDLE)
     {
      Print("ExportM1History_EA: cannot open file ", fname);
      return INIT_FAILED;
     }

   FileWrite(handle, "Datetime", "Open", "High", "Low", "Close", "Volume", "Spread", "RealVolume");

   int total = Bars(_Symbol, PERIOD_M1);
   Print("ExportM1History_EA: exporting ", total, " M1 bars for ", _Symbol);

   for(int i = total - 1; i >= 0; i--)
     {
      FileWrite(handle,
                FormatDateTime(iTime(_Symbol, PERIOD_M1, i)),
                DoubleToString(iOpen(_Symbol, PERIOD_M1, i), _Digits),
                DoubleToString(iHigh(_Symbol, PERIOD_M1, i), _Digits),
                DoubleToString(iLow(_Symbol, PERIOD_M1, i), _Digits),
                DoubleToString(iClose(_Symbol, PERIOD_M1, i), _Digits),
                IntegerToString(iVolume(_Symbol, PERIOD_M1, i)),
                IntegerToString(iSpread(_Symbol, PERIOD_M1, i)),
                IntegerToString(iRealVolume(_Symbol, PERIOD_M1, i)));
     }

   FileClose(handle);
   Print("ExportM1History_EA: done. Bars written: ", total, " -> ", fname);
   return INIT_SUCCEEDED;
  }
//+------------------------------------------------------------------+
