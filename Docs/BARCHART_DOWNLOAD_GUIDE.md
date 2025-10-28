# Barchart Premier Options Data Download Guide

**For Zero Loss Butterfly Strategy Backtesting**

---

## 🎯 **The Problem with Single-Contract Interface**

The interface you found (Equity Options Price History) is designed for **single option contract queries**:
- ❌ One strike at a time
- ❌ One expiration at a time  
- ❌ Manual data entry
- ❌ Not practical for backtesting

## 🔍 **Finding the Right Barchart Interface**

### **Look for These Interfaces Instead:**

1. **"Options Chain Download"** or **"Bulk Options Data"**
2. **"Historical Options Data Export"**
3. **"Options Data Download"** (bulk, not single contract)
4. **"Options Analytics"** or **"Options Overview"**

### **What You Need:**
- ✅ **All strikes** for multiple expirations
- ✅ **Date range** selection (April-October 2024)
- ✅ **Bulk download** (CSV/Excel format)
- ✅ **Multiple symbols** (V, SPY)

---

## 📋 **Step-by-Step Download Instructions**

### **Step 1: Find the Bulk Download Interface**

In Barchart Premier, look for:
- **"Data"** or **"Downloads"** menu
- **"Options"** section
- **"Historical Data"** or **"Bulk Data"**

### **Step 2: Configure the Download**

When you find the right interface, look for these options:

#### **Symbol Selection:**
- **V** (Visa) - for your main strategy
- **SPY** (S&P 500) - for testing

#### **Date Range:**
- **Start Date**: 2024-04-15
- **End Date**: 2024-10-17

#### **Options Configuration:**
- **Expiration Range**: 40-70 DTE (Days to Expiration)
- **Strike Range**: ±20% from current price
- **Option Types**: Both CALL and PUT
- **Data Frequency**: Daily

#### **Required Fields:**
- Date
- Symbol
- Expiration Date
- Strike Price
- Option Type (CALL/PUT)
- Bid Price
- Ask Price
- Last Price
- Volume
- Open Interest

### **Step 3: Download the Data**

1. **Select all required fields**
2. **Choose CSV format**
3. **Download** (should be one file per symbol)

---

## 🛠️ **Alternative: Automated Download**

If you can't find the bulk download interface, I've created an automated solution:

```bash
# Run the automated downloader
python DataTools/barchart_options_downloader.py
```

This will:
- ✅ Login to Barchart Premier
- ✅ Automatically collect data for all strikes and expirations
- ✅ Save to CSV format
- ✅ Generate summary reports

---

## 📊 **Expected Data Structure**

Your downloaded data should look like this:

```csv
date,symbol,expiration,strike,type,bid,ask,last,volume,open_interest
2024-04-15,V,2024-07-19,330.00,PUT,2.80,2.90,2.85,800,3000
2024-04-15,V,2024-07-19,340.00,CALL,5.20,5.30,5.25,1000,5000
2024-04-15,V,2024-07-19,350.00,CALL,3.10,3.20,3.15,1200,4000
...
```

---

## 🎯 **What to Look For in Barchart**

### **Good Interfaces:**
- ✅ **"Download"** or **"Export"** buttons
- ✅ **Multiple symbol selection**
- ✅ **Date range pickers**
- ✅ **Strike range options**
- ✅ **Bulk data options**

### **Avoid These:**
- ❌ **Single contract forms** (like the one you found)
- ❌ **Manual entry interfaces**
- ❌ **One-at-a-time downloads**

---

## 🔧 **If You Can't Find Bulk Download**

### **Option 1: Contact Barchart Support**
- Ask for **"bulk options data download"**
- Request **"historical options chain data"**
- Mention you need **"multiple strikes and expirations"**

### **Option 2: Use the Automated Tool**
- The `barchart_options_downloader.py` I created
- Handles the complexity automatically
- Generates the data you need

### **Option 3: Alternative Data Sources**
- **ThetaData** ($59/month) - designed for options backtesting
- **Upgrade Polygon** to Options Developer ($79/month)

---

## 📁 **File Organization**

Once you have the data, organize it like this:

```
data/barchart/
├── V_options_20240415_20241017.csv
├── SPY_options_20240501_20241031.csv
├── V_options_summary.json
└── SPY_options_summary.json
```

---

## 🚀 **Next Steps After Download**

1. **Verify data quality** - check for missing dates/strikes
2. **Convert to Lumibot format** using `barchart_to_lumibot_converter.py`
3. **Run your Zero Loss Butterfly backtest**
4. **Compare results** with previous tests

---

## 💡 **Pro Tips**

1. **Start with V data** - it's less liquid than SPY, easier to test
2. **Download 6+ months** - gives you room for rolling strategies
3. **Include all strikes** - ±20% range covers most scenarios
4. **Save multiple formats** - CSV for processing, Excel for review

The key is finding Barchart's **bulk download interface**, not the single-contract form you found. Look for terms like "bulk", "export", "download", or "chain data" in their interface.

