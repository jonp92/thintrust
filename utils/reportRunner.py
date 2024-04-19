from time import time
import json
import pandas as pd
import os
import platform
import pyarrow
from copy import copy
from io import BytesIO
import datetime
from utils.logger import Logger
from utils.singleton import Singleton


class reportRunner(Logger, Singleton):
    """
    A class to run reports on data and save them in different formats.
    
    This class provides functionality to run reports on data and save them in different formats such as CSV, JSON, and HTML.
    Due to code specialization, this class currently is designed to work with data from CAAR - Connected Automobile Analytics and Reporting.
    This limits the class to only work with data that has a timestamp and a value. Plus the current orientation modifiers are specific to the data from CAAR.
    However, the class can be modified to work with other data sources and orientations quite easily.
    A future PDF report generation functionality will be added to the class. This will be done using the weasyprint library. The intention is pretty display output for viewing though the CAAR web interface.
    The report data is filtered based on a given time period and query values, and the resulting report is saved to the specified output path.
    Additional modifiers can be added to modify the report data based on the given keys and values. 
    For example, to calculate the average of a certain value, or to filter the data based on a certain condition.
    Note, reportRunner
    
    Attributes:
    
    report_type (str): The type of report to be generated. Can be 'csv', 'json', or 'html'.
    name (str): The name of the report file.
    output_path (str): The path where the report file will be saved.
    time_period (int): The time period in hours for which the report data will be filtered.
    data (list): The data on which the report will be run. Should be a list of dictionaries.
    query_values (list): The keys for which the report data will be filtered.
    modifiers (dict): Additional modifiers to modify the report data based on the given keys and values. For example, to calculate the average of a certain value, or to filter the data based on a certain condition.
    to call a modifier, you add the orientation keyword and the value you want to calculate. I.e orientation='charging'. Other modifiers outside of orientations are not allowed but can be added in the future.
    
    Methods:
    
    run_report: Runs the report on the data and saves it in the specified format.
    create_df: Creates a pandas DataFrame from the given report data.
    to_csv: Converts the report data to a CSV file and saves it to the specified output path.
    to_json: Converts the given report data to a JSON string.
    to_html: Converts the given report data into an HTML table.
    
    Raises:
    
    ValueError: If the report type is invalid, or if no data is available for the given time period and query values.
    """
    def __init__(self) -> None:
        self.report_type = None
        self.name = None
        self.output_path = None
        self.time_period = None
        self.data = None
        self.query_values = None
        self.report = None
        self.logger = Logger('reportRunner', 'reportRunner.log', 'DEBUG').logger
        self.logger.debug("reportRunner class initialized")
        
    def run_report(self, report_type: str = None,  name: str = None, output_path: str = None, time_period: int = None, data: list = None, query_values: list = None, **modifiers):
        """
        Runs the report on the data and saves it in the specified format.
        
        This method filters the report data based on the given time period and query values, and saves the resulting report in the specified format.
        
        Args:
        
        report_type (str): The type of report to be generated. Can be 'csv', 'json', or 'html'.
        name (str): The name of the report file.
        output_path (str): The path where the report file will be saved.
        time_period (int): The time period in hours for which the report data will be filtered.
        data (list): The data on which the report will be run. Should be a list of dictionaries.
        query_values (list) or (str): The keys for which the report data will be filtered. Can be a list of strings or a comma-separated string. This allows GET requests to be passed as a string and then split into a list.
        
        Attributes:
        
        report_data (list): The filtered report data.
        
        Returns:
        
        report (list): The report data in the specified format.
        
        Raises:
        
        ValueError: If the report type is invalid, or if no data is available for the given time period and query values.
        """
        self.report_type = report_type
        self.name = name 
        self.output_path = output_path
        self.time_period = time_period if type(time_period) == int else int(time_period)
        self.data = data
        if query_values and type(query_values) != list: # check if query values is a string, if so, split it into a list
            self.query_values = query_values.split(',') if query_values else None 
        elif query_values and type(query_values) == list: # if query values is already a list, set it to query values
            self.query_values = query_values
        elif not query_values: # if query values is not provided, set it to None
            self.query_values = None
        self.query_values.append('timestamp')  # add timestamp to query values
        report_data = []  # list of dictionaries
        current_time = time()  # get current time in seconds
        time_to_report = (current_time - self.time_period * 60 * 60)  # convert hours to seconds
        for row in self.data:  # iterate through data
            for key, value in row.items():  # iterate through key value pairs
                if type(value) == str:
                    raise ValueError(f"{key, value} is an Invalid data type. Value must be an integer or float")
                if key == 'timestamp' and len(str(value)) > 10:  # check if timestamp is in milliseconds
                    value = int(value)  # convert to int
                    value = value // 1000  # convert to seconds
                if key =='driving_point_epoch_time' and len(str(value)) > 10:  # check if driving_point_epoch_time is in milliseconds
                    value = int(value)  # convert to int
                    value = value // 1000  # convert to seconds
                if key == 'timestamp' and value >= time_to_report and value <= current_time or key =='driving_point_epoch_time' and value >= time_to_report and value <= current_time: # check if timestamp is within the time period, first convert to seconds
                    # Adding additional condition to filter the data based on the value of the key can be done as follows:
                    #if 'value' in row and row['value'] > 100:  # additional condition
                        #report_data.append(row)
                        #break
                    report_data.append(row)
                    break
        if self.query_values:
            report_data = [{key: value for key, value in row.items() if key in self.query_values} for row in report_data]
        if not report_data:
            raise ValueError('No data available for the given time period and query values')
        if modifiers:
            # Add additional functionality to modify the report data based on the given modifiers
            # For example, to calculate the average of a certain value, or to filter the data based on a certain condition
            # Only values that are list in orientations are allowed
            orientations = ['efficiency', 'charging', 'discharging', 'distance', 'gps_coordinates', 'avg_speed', 'avg_efficiency', 'avg_charging', 'avg_discharging', 'avg_distance', 'avg_gps_coordinates', 'avg_cost', 'averages', 'trips', 'None']
            def time_elapsed():
                """
                Calculate the time elapsed between the first and last timestamps in the report data.
                
                This helper method calculates the time elapsed between the first and last timestamps in the report data and returns it in seconds and as a string.
                Returns:
                
                time_elapsed (int): The time elapsed in seconds.
                time_str (str): The time elapsed in days, hours, minutes, and seconds.
                """
                times = [row['timestamp'] for row in report_data]
                time_elapsed = (times[-1] - times[0]) // 1000 # convert to seconds from milliseconds
                total_seconds = copy(time_elapsed)
                days = time_elapsed // 86400
                time_elapsed %= 86400
                hours = time_elapsed // 3600
                time_elapsed %= 3600
                minutes = time_elapsed // 60
                time_elapsed %= 60
                seconds = time_elapsed
                time_str = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
                return total_seconds, time_str
            
            for key, value in modifiers.items():
                if key == 'orientation' and value in orientations:
                    self.logger.debug(f"A orientation modifier was found: {value}, Calculating...")
                    if value == 'averages':
                        self.logger.debug("Calculating averages...")
                        dp_groups = []
                        group = []
                        drive_start = False
                        drive_end = False
                        total_distance = 0
                        total_consumption = 0
                        total_elapsed = 0
                        total_cost = 0
                        for row in report_data:
                            if 'point_marker_type' in row and row['point_marker_type'] == 1:
                                if group:
                                    dp_groups.append(group)
                                drive_start = True
                                drive_end = False
                                group = [row]
                            elif 'point_marker_type' not in row:
                                drive_start = False
                                drive_end = False
                                group.append(row)
                            elif 'point_marker_type' in row and row['point_marker_type'] == 2:
                                drive_start = False
                                drive_end = True
                                group.append(row)
                        if group:
                            dp_groups.append(group)   
                        for group in dp_groups:
                            self.logger.debug(f'Calculating group: {group}')
                            distance = round(sum([point['distance_delta'] for point in group]) * 0.000621371, 2) # convert meters to miles
                            energy = sum([point['energy_delta'] for point in group])
                            trip_start = datetime.datetime.fromtimestamp(group[0]['driving_point_epoch_time'] / 1000)
                            trip_end = datetime.datetime.fromtimestamp(group[-1]['driving_point_epoch_time'] / 1000)
                            trip_total = (trip_end - trip_start).seconds
                            group.append({'consumption': energy, 'trip_start': trip_start, 'trip_end': trip_end, 'trip_total': trip_total})
                            total_distance += distance
                            total_consumption += energy
                            total_elapsed += trip_total
                            cost = (energy / 1000) * 0.10 # cost per kWh
                            total_cost += cost
                        
                        days = total_elapsed // 86400
                        hours = (total_elapsed % 86400) // 3600
                        minutes = (total_elapsed % 3600) // 60
                        seconds = total_elapsed % 60
                        total_elapsed = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
                        first_trip = dp_groups[0][-1]['trip_start']
                        last_trip = dp_groups[-1][-1]['trip_end']
                        total_consumption = total_consumption / 1000 # convert Wh to kWh
                        avg_consumption = total_consumption / total_distance # divide total consumption by total distance, to get average consumption per mile in kWh
                        total_cost = round(total_cost, 2)
                        cost_per_mile = round(total_cost / total_distance,2)
                        report_data.clear()
                        report_data.append({'first_trip': str(first_trip), 'last_trip': str(last_trip),'time_elapsed': total_elapsed, 'total_distance (mi)': total_distance, 'total_consumption (kWh)': total_consumption, 'avg_consumption_per_mi (kWh)': avg_consumption, 'cost ($)': total_cost, 'cost_per_mile ($)': cost_per_mile})
                    elif value == 'trips':
                        self.logger.debug("Calculating trips...")
                        dp_groups = []
                        group = []
                        drive_start = False
                        drive_end = False
                        total_distance = 0
                        total_consumption = 0
                        total_elapsed = 0
                        total_cost = 0
                        for row in report_data:
                            if 'point_marker_type' in row and row['point_marker_type'] == 1:
                                if group:
                                    dp_groups.append(group)
                                drive_start = True
                                drive_end = False
                                group = [row]
                            elif 'point_marker_type' not in row:
                                drive_start = False
                                drive_end = False
                                group.append(row)
                            elif 'point_marker_type' in row and row['point_marker_type'] == 2:
                                drive_start = False
                                drive_end = True
                                group.append(row)
                        if group:
                            dp_groups.append(group)
                        report_data.clear()   
                        for group in dp_groups:
                            distance = round(sum([point['distance_delta'] for point in group]) * 0.000621371, 2) # convert meters to miles
                            energy = round(sum([point['energy_delta'] for point in group]) / 1000, 2) # convert Wh to kWh and round to 2 decimal places
                            trip_start = datetime.datetime.fromtimestamp(group[0]['driving_point_epoch_time'] / 1000)
                            trip_end = datetime.datetime.fromtimestamp(group[-1]['driving_point_epoch_time'] / 1000)
                            trip_total = (trip_end - trip_start).seconds
                            #group.append({'distance': distance, 'consumption': energy, 'trip_start': trip_start, 'trip_end': trip_end, 'trip_total': trip_total})
                            cost = round((energy) * 0.10, 2) # cost per kWh
                            total_cost += cost
                            total_consumption += energy
                            total_distance += distance
                            total_elapsed += trip_total
                            trip_total = trip_total // 60 # convert seconds to minutes
                            report_data.append({'Trip Start': str(trip_start), 'Trip End': str(trip_end), 'Trip Time (Min)': trip_total, 'Distance (mi)': distance, 'Consumption (kwh)': energy, 'Cost ($)': cost})
                    elif value == 'efficiency':
                        # Add efficiency calculation here
                        pass
                    elif value == 'charging':
                        # Add charging calculation here
                        if 'power' in self.query_values and 'chargePortConnected' in self.query_values:
                            power_level = [row['power'] for row in report_data if row['chargePortConnected'] == True and row['power'] < 0] # charging
                            power_used = sum(power_level)
                            power_used = abs(power_used) // 1000000 # convert milliwatts to kilowatts and take absolute value
                            time_elapsed, time_str = time_elapsed()
                            report_data.clear()
                            report_data.append({'charging power usage': power_used, "time_elapsed": time_str})
                    elif value == 'discharging':
                        # Add discharging calculation here
                        if 'power' in self.query_values and 'chargePortConnected' in self.query_values:
                            # create a list of power values where chargePortConnected is False and power is greater than 0 (discharging)
                            power_level = [row['power'] for row in report_data if row['chargePortConnected'] == False and row['power'] > 0]
                            times = [row['timestamp'] for row in report_data if row['chargePortConnected'] == False and row['power'] > 0]
                            time_elapsed = (times[-1] - times[0]) // 1000 # convert to seconds from milliseconds
                            hours = time_elapsed / 3600
                            power_used = sum(power_level)
                            mW_to_kW = power_used / 1000000 # convert milliwatts to kilowatts
                            power_used = mW_to_kW * hours
                            report_data.clear()
                            report_data.append({'discharging power usage': power_used})
                    elif value == 'distance':
                        # Add distance calculation here
                        pass
                    elif value == 'gps_coordinates':
                        # Add GPS coordinates calculation here
                        pass
                    elif value == 'avg_speed':
                        # Add average speed calculation here
                        if 'speed' in self.query_values:
                            speed = [row['speed'] for row in report_data]
                            avg_speed = sum(speed) / len(speed)
                            avg_speed = round(avg_speed * 2.23694, 2) # convert from m/s to mph
                            report_data.clear()
                            report_data.append({'Average Speed': avg_speed})
                    elif value == 'avg_efficiency':
                        # Add average efficiency calculation here
                        pass
                    elif value == 'avg_charging':
                        # Add average charging calculation here
                        pass
                    elif value == 'avg_discharging':
                        # Add average discharging calculation here
                        pass
                    elif value == 'avg_distance':
                        # Add average distance calculation here
                        pass
                    elif value == 'avg_cost':
                        # Add average cost calculation here
                        if 'power' in self.query_values and 'chargePortConnected' in self.query_values:
                            power_level = [row['power'] for row in report_data if row['chargePortConnected'] == True and row['power'] < 0] # charging
                            power_used = sum(power_level)
                            power_used = abs(power_used) // 1000000 # convert milliwatts to kilowatts and take absolute value
                            cost = power_used * 0.10 # cost per kWh
                            time_elapsed, time_str = time_elapsed()
                            report_data.clear()
                            report_data.append({'Cost': cost, "time_elapsed": time_str})
                elif value not in orientations:
                    self.logger.debug(f"Invalid orientation: {value}")
                    # If the orientation is not valid, raise a ValueError
                    raise ValueError('Invalid orientation')
        if self.report_type == 'csv':
            self.report = self.to_csv(report_data)
        elif self.report_type == 'json':
            self.report = self.to_json(report_data)
        elif self.report_type == 'html':
            self.report = self.to_html(report_data)
        elif self.report_type == 'pdf':
            # Add PDF report generation functionality using the weasyprint library
            temp = BytesIO()
            html = self.to_html(report_data)
            if 'Windows' in platform.system():
                raise ValueError('PDF report generation is not supported on Windows')
            else:
                from weasyprint import HTML
                HTML(string=html).write_pdf(temp)
            temp.seek(0)
            self.report = temp.read()
            
        else:
            raise ValueError('Invalid report type')

        if self.output_path:
            if self.output_path != '_':
                self.logger.debug("Saving report...")
                if report_type in ['pdf', 'csv']:
                    with open(f"{self.output_path}/{self.name}.{self.report_type}", 'wb') as file:
                        file.write(self.report)
                    if report_type == 'pdf':
                        return self.report
                    elif report_type == 'csv':
                        return self.report.decode('utf-8')
                else:
                    with open(f"{self.output_path}/{self.name}.{self.report_type}", 'w') as file:
                        file.write(self.report)
                        return self.report
            else:
                self.logger.debug("Returning report...")
                return self.report
    
    def create_df(self, report_data):
        """
        Create a pandas DataFrame from the given report data.

        Args:
            report_data (list): A list of dictionaries representing the report data.

        Returns:
            pandas.DataFrame: The created DataFrame.
        """
        df = pd.DataFrame(report_data)
        return df
    
    def to_csv(self, report_data):
        """
        Converts the report data to a CSV file and saves it to the specified output path.

        Args:
            report_data (list): The report data to be converted to CSV.

        Returns:
            data (str): The CSV string representation of the report data for possible use in other functions.
        """
        df = self.create_df(report_data)
        temp = BytesIO()
        df.to_csv(temp, index=False)
        temp.seek(0)
        csv = temp.read()
        return csv
    
    def to_json(self, report_data):
        """
        Converts the given report data to a JSON string.

        Args:
            report_data (dict): The report data to be converted.

        Returns:
            str: The JSON string representation of the report data.
        """
        return json.dumps(report_data)
    
    def to_html(self, report_data):
        """
        Converts the given report data into an HTML table.

        Args:
            report_data (list): The data to be converted into an HTML table.

        Returns:
            str: The HTML representation of the data as a table.
        """
        df = self.create_df(report_data)
        html = df.to_html()
        return html

# Example usage. Ensure that the timestamps are within the time period, and the query values are present in the data.
# Otherwise, a ValueError will be raised.
# report = reportRunner()
# report.run_report(report_type='csv', name='report', output_path='.', time_period=72, data=[{'timestamp': 1607867000, 'value': 100}, {'timestamp': 1607867000, 'value': 200}], query_values=['value'])
