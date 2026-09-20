from pathlib import Path
import csv

from cumulusci.core.tasks import BaseTask, CCIOptions
from cumulusci.utils.options import Field

class ScanCSVTask(BaseTask):
    task_options = {
        "csv_file_path": {
            "description": "Path to the CSV file to scan",
            "required": True,
        },
        "value_to_scan": {
            "description": "The value to scan for in the CSV file",
            "required": True,
        },
    }

    def _run_task(self):
        csv_file_path = self.options["csv_file_path"]
        value_to_scan = self.options["value_to_scan"]

        found = False

        try:
            with open(csv_file_path, mode="r", newline="") as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if value_to_scan in row:
                        found = True
                        break

        except Exception as e:
            self.logger.error(f"Error while scanning CSV file: {str(e)}")
            self.exit_code = 1
            return

        self.return_values["found"] = str(found)
        self.org_config["found"] = str(found)

        if found:
            self.return_values["response"] = f"Found '{value_to_scan}' in the CSV file."
        else:
            self.return_values["response"] = f"'{value_to_scan}' not found in the CSV file."

        self.logger.info(self.return_values['response'])
