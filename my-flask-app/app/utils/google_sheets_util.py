import os
from ..config import get_config
import pygsheets
from datetime import datetime
import calendar
import pygsheets

# Get the current environment ('development', 'testing', 'production')
env = os.getenv('APP_ENV', 'default')

# Get the configuration for the current environment
config = get_config(env)

google_sheets_credentials_path = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
if google_sheets_credentials_path is None:
    raise ValueError("GOOGLE_SHEETS_CREDENTIALS is not set in the environment variables")



class SheetPopulator:
    def __init__(self, client_secret=None, sheet_url=None):
        if client_secret is None:
            client_secret = google_sheets_credentials_path
        if sheet_url is None:
            google_sheets_url = config.GOOGLE_SHEETS_URL_INCOME_ANALYSER
            sheet_url = google_sheets_url
        self.client = pygsheets.authorize(service_account_file=client_secret)
        self.spreadsheet = self.client.open_by_url(sheet_url)
        self.worksheet = self.spreadsheet.worksheet("title", "Income Calculation Worksheet")
    
    def parse_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%m/%d/%Y")
        except ValueError:
            print(f"Error parsing date: {date_str}")
            return None
        
    def determine_period_type(self, start_date_str, end_date_str):
        start_date = self.parse_date(start_date_str)
        end_date = self.parse_date(end_date_str)
        #print(f"Start date: {start_date}, End date: {end_date}")
        if start_date and end_date:
            delta = (end_date - start_date).days + 1  # including end date
            # print(f"Delta: {delta}")
            if delta == 7:
                return 'C25', delta  # Weekly
            elif delta == 14:
                return 'C26', delta  # Bi-weekly
            elif delta in [15, 16]:
                return 'C27', delta  # Semi-monthly
            elif 28 <= delta <= 31:
                return 'C28', delta  # Monthly
        return 'C28', delta  # Default to monthly if undetermined
    
    def get_number_of_days_in_this_month(self, date_str):
        date = datetime.strptime(date_str, "%m/%d/%Y")
        year = date.year
        month = date.month
        day = date.day
        days_in_month = calendar.monthrange(year, month)[1]
        return month, day, days_in_month

    def update_value(self, cell, value):
        self.worksheet.update_value(cell, value)

    def get_earning_type(description):
        # Assume description might have some indicator of type
        if "commission" in description:
            return "Commission"
        elif "bonus" in description:
            return "Bonus"
        elif "overtime" in description:
            return "Bonus"
        elif "regular" in description:
            return "Regular"
        elif "base" in description:
            return "Regular"
        elif "paid time off" in description:
            return "Regular"
        elif "pto" in description:
            return "Regular"
        elif "holiday" in description:
            return "Regular"
        elif "vacation" in description:
            return "Regular"
        elif "personal" in description:
            return "Regular"
        elif "sick" in description:
            return "Regular"
        
        return None  # Default to None if no specific type is identified
    
    def populate_sheet(self, is_w2, data, general_cell_map=None, earnings_cell_map=None):
        if not is_w2:
            combined_earnings = 0
            first_earning_processed = False
            start_date, end_date, earnings_this_period, paydate = None, None, None, None
            regular_earnings = 0
            is_salary = False
            eoy_paystub = False
            eoy_regular_earnings = 0

            # Find the first empty row
            row_offset = 0
            while self.worksheet.get_value(f"H{11 + row_offset}") != "":
                row_offset += 1
            if row_offset == 4:
                eoy_paystub = True # Check if all spaces for regular paystubs are taken, if it is, then this paystub is an End of Year Paystub

            for entity in data:
                type = entity['Type']
                value = entity['Raw Value']

                if not eoy_paystub:
                    if type in general_cell_map:
                        self.update_value(general_cell_map[type], value)

                    elif type == "earning_item":
                        parts = value.split()
                        earning_type = self.get_earning_type(value.lower())
                        
                        if earning_type == "Regular":
                            regular_earnings += float(parts[-1].replace(',', '').replace('$', ''))
                            if not first_earning_processed:
                                if len(parts) == 3:
                                    is_salary = True
                                else:
                                    self.worksheet.update_value(f"E{11+row_offset}", parts[-4]) # Rate
                                    self.worksheet.update_value(f"F{11+row_offset}", parts[-3]) # Hours
                                first_earning_processed = True
                        elif earning_type == "Commission":
                            # Update only YTD for Commission
                            self.worksheet.update_value("C62", parts[-1])
                        elif earning_type == "Bonus":
                            # Summation for Overtime and Bonus
                            combined_earnings += float(parts[-1].replace(',', '').replace('$', ''))
                    
                    elif type == "start_date":
                        start_date = value
                    elif type == "end_date":
                        end_date = value
                    elif type == "pay_date":
                        paydate = value
                    elif type == "gross_earnings_ytd":
                        gross_earnings_ytd = value
                    elif type == "gross_earnings":
                        gross_earnings = value
                
                # End of Year Paystub
                else:
                    if type == "earning_item":
                        parts = value.split()
                        earning_type = self.get_earning_type(value.lower())
                        if earning_type == "Regular":
                            eoy_regular_earnings += float(parts[-1].replace(',', '').replace('$', ''))
                    elif type == "pay_date":
                        eoy_paydate = value
                        eoy_month, eoy_day, eoy_month_days, eoy_year = self.get_number_of_days_in_this_month(eoy_paydate)
                        self.worksheet.update_value(f"F24", eoy_year)

            if start_date and end_date and paydate:
                period_cell, delta = self.determine_period_type(start_date, end_date)
                if is_salary:
                    if period_cell:
                        self.worksheet.update_value(period_cell, gross_earnings)
                        self.worksheet.update_value("C39", gross_earnings_ytd)
                else:
                    if delta == 7:
                        self.worksheet.update_value(f"G{11 + row_offset}", "TRUE" ) # Weekly
                    elif delta == 14:
                        self.worksheet.update_value(f"G{11 + row_offset}", "FALSE" ) # Bi-weekly
                    month, day, month_days = self.get_number_of_days_in_this_month(paydate)
                    cell_value = round(day/month_days, 2) + month - 1  # Normalize to a value between 0 and 1
                    self.worksheet.update_value(f"I{11 + row_offset}", cell_value)
                    self.worksheet.update_value(f"G39", cell_value)
                    self.worksheet.update_value(f"G49", cell_value)
                    self.worksheet.update_value(f"G67", cell_value)
                    self.worksheet.update_value(f"G82", cell_value)
        
            if regular_earnings > 0:
                self.worksheet.update_value(f"H{11 + row_offset}", f"${regular_earnings:,.2f}")
            if eoy_regular_earnings > 0:
                self.worksheet.update_value("C24", f"${eoy_regular_earnings:,.2f}")

            # if combined_earnings > 0:
            #     current_value = self.worksheet.get_value('C39').replace('$', '').replace(',', '')
            #     current_value = float(current_value) if current_value else 0
            #     new_total = current_value + combined_earnings
            #     self.update_value('C39', f"${new_total:,.2f}")

        else:
            wages_tips_other_compensation = 0

            for entity in data:
                if entity['Type'] == 'WagesTipsOtherCompensation':
                    wages_tips_other_compensation += float(entity['Raw Value'].replace(',', '').replace('$', ''))
                    #print(f"found value: {entity['Raw Value']} for {entity['Type']}")
                if entity['Type'] == 'FormYear':
                    cell = self.worksheet.cell("E19")
                    #print(f"cell value: {cell.value}")
                    if cell.value == "" or cell.value == "0":
                        self.worksheet.update_value("E19", entity['Raw Value'])
                        self.worksheet.update_value("E40", entity['Raw Value'])
                        self.worksheet.update_value("E83", entity['Raw Value'])
                    else:
                        self.worksheet.update_value("E20", entity['Raw Value'])
                        self.worksheet.update_value("E41", entity['Raw Value'])
                        self.worksheet.update_value("E84", entity['Raw Value'])
                    
                if self.worksheet.cell("C19").value == "" or self.worksheet.cell("C19").value == "0":
                    self.worksheet.update_value("C19", wages_tips_other_compensation)
                    self.worksheet.update_value("C40", wages_tips_other_compensation)
                    self.worksheet.update_value("C83", wages_tips_other_compensation)
                else:
                    self.worksheet.update_value("C20", wages_tips_other_compensation)
                    self.worksheet.update_value("C41", wages_tips_other_compensation)
                    self.worksheet.update_value("C84", wages_tips_other_compensation)


class SheetPopulatorWithoutAI:
    def __init__(self, client_secret=None, sheet_url=None):
        if client_secret is None:
            client_secret = google_sheets_credentials_path
        if sheet_url is None:
            google_sheets_url = config.GOOGLE_SHEETS_URL_FANNIE_MAE
            sheet_url = google_sheets_url
        self.client = pygsheets.authorize(service_account_file=client_secret)
        self.spreadsheet = self.client.open_by_url(sheet_url)
        self.worksheet = self.spreadsheet.worksheet("title", "Sheet1")

    def update_value(self, cell_name, value):
        cell = self.worksheet.cell(cell_name)
        cell.value = value

    def populate_sheet_without_ai(self, data, cell_map):
        for key, value in data.items():
            if key in cell_map and value is not None:
                self.update_value(cell_map[key], value)