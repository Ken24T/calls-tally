# Touch-Point Tracker Installation Guide

This guide will help you install the Touch-Point Tracker on your computer using a provided zip file. No technical knowledge is required—just follow the steps below.

---

## What is Touch-Point Tracker?

Touch-Point Tracker is a desktop application designed for Validum Institute team members to record and track daily customer interactions. It helps you maintain accurate records of:

- **Call Activity**: Connects, Non-Connects, and In-Between calls across different lead sources (Paid Leads, Organic Leads, Agents)
- **Digital Touchpoints**: SMS and Email communications
- **Key Metrics**: Enrolment Packs sent, Quotes provided, and CPD sessions booked
- **Daily Notes**: Comments and observations from your workday

The app automatically saves your entries and can generate weekly reports that can be emailed directly from the application.

---

## 1. Download and Extract the Zip File
1. Download the zip file containing the Touch-Point Tracker to your computer.
2. Right-click the zip file and select **Extract All...**
3. Choose a location on your computer (such as your Desktop or Documents folder) and click **Extract**.
4. After extraction, you will see a new folder (for example, `TouchPointTracker` or similar).

## 2. Run the Application
1. Open the extracted folder.
2. Find the file named **touch-point-tracker.exe** (it may just show as "touch-point-tracker" if file extensions are hidden).
3. Double-click **touch-point-tracker.exe** to start the app.
   - The first time you run the app, it will create a folder named **data** inside the same folder as the app. This is where your information is stored.

## 3. Migrating Your Existing Tally Data

⚠️ **Important Note**: If you previously used the old Call Tracker app with a different data structure, your old data will not be automatically migrated. The new Touch-Point Tracker uses an enhanced data schema to support the expanded metrics.

If you need to migrate historical data, please contact your system administrator for assistance with data conversion.

For fresh installations, skip this section and proceed to **First-Time Setup** below.

---

## 4. First-Time Setup: Adding a User and Configuring Settings

After starting the Touch-Point Tracker for the first time:

### **Add Your User Profile**
1. Go to the **Users** menu in the menu bar at the top of the window.
2. Click **Add User**.
3. Enter your name exactly as you want it to appear in reports.
4. Click **OK** to save.

### **Configure Report Email Settings**
1. Go to the **Edit** menu in the menu bar.
2. Click **Settings**.
3. In the Settings dialog, locate the **Default Email Recipients** field.
4. Enter one or more email addresses where reports should be sent (separate multiple addresses with semicolons: `;`).
   - Example: `manager@validumgroup.com.au;admin@validumgroup.com.au`
5. Click **Save** to confirm your settings.

### **Window Position Settings (Optional)**
- If you want the app to remember its size and position between sessions:
  1. Open **Edit → Settings**
  2. Check the box for **Remember window position and size**
  3. The app will now restore its window size and position when you reopen it
- If unchecked, the app will always start at the default size (320 x 1024) centered on your screen.

---

## 5. Using the Application

### **Daily Data Entry**

1. **Select User and Date**
   - At the top of the window, select your name from the dropdown
   - Choose the date you're entering data for (defaults to today)

2. **Recording Touch-Points**
   
   The app has two tabs: **Current Leads** and **Prospects**. Each tab tracks the same metrics but for different customer categories.

   **CALL Activity Sections:**
   - **CALL - Connects**: Successful phone conversations
   - **CALL - Non-Connects**: Calls that didn't reach the contact
   - **CALL - In Betweens**: Calls that fall between connects and non-connects
   
   For each section, record the count by source:
   - **Paid Lead**: Calls from paid advertising campaigns
   - **Organic Lead**: Calls from organic/natural sources
   - **Agents**: Calls involving agents
   
   Each section shows an auto-calculated **Total** which you can manually override if needed.

   **OTHER Section:**
   - **SMS**: Number of text messages sent
   - **Email**: Number of emails sent
   
   **Grand Total:** Automatically sums all call sections and OTHER touchpoints. Can be manually adjusted if needed.

   **Additional Metrics:**
   - **Enrolment Packs**: Number of enrolment packages sent
   - **Quotes**: Number of quotes provided to customers
   - **CPD Booked**: Number of CPD (Continuing Professional Development) sessions booked
   
   **Grand Total (Bottom):** Automatically sums the three additional metrics above.

3. **Manual Override Indicators**
   - If you manually edit any auto-calculated total, it will display with a **yellow background**
   - Hover over the yellow field to see a tooltip showing how much it differs from the calculated value
   - Example: "Override: +2 from calculated value"

4. **Adding Notes**
   - At the bottom of the window, there's a **Notes** text area
   - Use this to record any important observations, follow-ups, or comments for the day
   - Notes appear in your weekly reports

5. **Auto-Save**
   - The app automatically saves your data as you make changes
   - No need to click a "Save" button—your work is continuously preserved

6. **Switching Dates or Users**
   - Simply select a different date or user from the dropdowns at the top
   - The app will load that entry's data automatically

### **Generating Reports**

1. Click **Reports → Generate Report** from the menu bar
2. In the Report Dialog:
   - Select the **Start Date** and **End Date** for your report period
   - Click **Generate Report**
3. Review the report preview in the text area
4. To email the report:
   - The **Email To** field will be pre-filled with your default recipients (from Settings)
   - You can edit this field to change recipients for this specific report
   - Click **Send Report via Email**
   - Your default email client will open with the report pre-filled
   - Review and click Send in your email client

### **Window Controls**

- **Resize**: The window can be resized by dragging the edges or corners
- **Minimum Size**: The window has a minimum size of 320 x 1024 pixels
- **Remember Position**: Enable in Settings to have the app remember your preferred window size and position

---

## 6. Data Storage and Backup

- All your data is stored in the **data** folder inside the Touch-Point Tracker installation directory
- The main data file is **data/tally_data.json**
- Settings are stored in **data/app_settings.json**

**To backup your data:**
1. Close the Touch-Point Tracker application
2. Copy the entire **data** folder to a safe location (e.g., OneDrive, external drive)
3. Store dated backups regularly

**To restore from backup:**
1. Close the Touch-Point Tracker application
2. Replace the **data** folder with your backed-up version
3. Restart the application

---

## Troubleshooting

**The app won't start:**
- Ensure you've extracted the full zip file (don't run from inside the zip)
- Make sure you have the necessary permissions to run programs in the folder location

**My data disappeared:**
- Check that you're selecting the correct user and date
- Verify the data folder contains your `tally_data.json` file
- Restore from a recent backup if needed

**Reports aren't generating:**
- Make sure you have data entries for the selected date range
- Verify the selected user has entries in the database

**Email sending doesn't work:**
- The app opens your default email client (Outlook, Gmail app, etc.)
- Make sure you have an email client configured on your computer
- You can always copy the report text and paste it manually into your email

---

**You are now ready to use the Touch-Point Tracker!**

For questions or support, please contact your Validum Institute IT administrator.
