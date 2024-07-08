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
        days_in_month = calendar.monthrange(year, month)[1]
        return days_in_month

    def update_value(self, cell, value):
        self.worksheet.update_value(cell, value)

    def get_earning_type(self, description):
        # Assume description might have some indicator of type
        if "Commission" in description:
            return "Commission"
        elif "Bonus" in description:
            return "Bonus"
        elif "Overtime" in description:
            return "Bonus"
        return None  # Default to None if no specific type is identified
    
    def populate_sheet(self, is_w2, data, general_cell_map=None, earnings_cell_map=None):
        if not is_w2:
            combined_earnings = 0
            first_earning_processed = False
            start_date, end_date, earnings_this_period, paydate = None, None, None, None

            for entity in data:
                if entity['Type'] in general_cell_map:
                    self.update_value(general_cell_map[entity['Type']], entity['Raw Value'])

                elif entity['Type'] == "earning_item":
                    parts = entity['Raw Value'].split()
                    if not first_earning_processed:
                        self.update_value(earnings_cell_map["Regular"]["rate"], parts[-4])
                        self.update_value(earnings_cell_map["Regular"]["hours"], parts[-3])
                        self.update_value(earnings_cell_map["Regular"]["ytd"], parts[-1])
                        first_earning_processed = True
                    else:
                        earning_type = self.get_earning_type(entity['Raw Value'])
                        if earning_type == "Commission":
                            self.update_value(earnings_cell_map["Commission"], parts[-1])
                        elif earning_type == "Bonus":
                            combined_earnings += float(parts[-1].replace(',', '').replace('$', ''))

                elif entity['Type'] in ["start_date", "end_date", "pay_date", "gross_earnings"]:
                    if entity['Type'] == "start_date":
                        start_date = entity['Raw Value']
                    elif entity['Type'] == "end_date":
                        end_date = entity['Raw Value']
                    elif entity['Type'] == "pay_date":
                        paydate = entity['Raw Value']
                    elif entity['Type'] == "gross_earnings":
                        earnings_this_period = entity['Raw Value']

                    if start_date and end_date and earnings_this_period and paydate:
                        period_cell, delta = self.determine_period_type(start_date, end_date)
                        cell_value = round(delta/self.get_number_of_days_in_this_month(paydate), 2)
                        self.update_value("G30", (cell_value))
                        self.update_value("G11", (cell_value))
                        self.update_value("G39", (cell_value))
                        self.update_value("G57", (cell_value))
                        self.update_value("G72", (cell_value))
                        self.update_value("C88", (cell_value))
                        self.update_value("C97", (cell_value))

                        if period_cell:
                            self.update_value(period_cell, earnings_this_period)
                            start_date, end_date, earnings_this_period = None, None, None  # Reset after processing

            if combined_earnings > 0:
                current_value = self.worksheet.get_value('C39').replace('$', '').replace(',', '')
                current_value = float(current_value) if current_value else 0
                new_total = current_value + combined_earnings
                self.update_value('C39', f"${new_total:,.2f}")

        else:
            wages_tips_other_compensation = 0

            for entity in data:
                if entity['Type'] == 'WagesTipsOtherCompensation':
                    wages_tips_other_compensation += float(entity['Raw Value'].replace(',', '').replace('$', ''))
                    #print(f"found value: {entity['Raw Value']} for {entity['Type']}")
                if entity['Type'] == 'FormYear':
                    cell = self.worksheet.cell("E12")
                    #print(f"cell value: {cell.value}")
                    if cell.value == "" or cell.value == "0":
                        self.update_value("E12", entity['Raw Value'])
                        self.update_value("E73", entity['Raw Value'])
                    else:
                        self.update_value("E13", entity['Raw Value'])
                        self.update_value("E74", entity['Raw Value'])
                    
            if self.worksheet.cell("C12").value == "" or self.worksheet.cell("C12").value == "0":
                self.update_value("C12", wages_tips_other_compensation)
                self.update_value("C31", wages_tips_other_compensation)
                self.update_value("C73", wages_tips_other_compensation)
            else:
                self.update_value("C13", wages_tips_other_compensation)
                self.update_value("C32", wages_tips_other_compensation)
                self.update_value("C74", wages_tips_other_compensation)


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