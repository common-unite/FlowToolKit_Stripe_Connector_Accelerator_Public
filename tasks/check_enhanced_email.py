from cumulusci.tasks.salesforce import BaseSalesforceApiTask


class CheckEnhancedEmailEnabled(BaseSalesforceApiTask):
    """Preflight check: verifies Enhanced Email is enabled.

    Queries EmailAdministrationSettings.IsEnhancedEmailEnabledEnabled
    via the Tooling API. Enhanced Email is required for form confirmation
    email delivery to work correctly.

    Sets return_values["is_enabled"] to True/False.
    """

    task_docs = "Check if Enhanced Email is enabled in the target org."

    def _run_task(self):
        result = self.tooling.query(
            "SELECT IsEnhancedEmailEnabledEnabled FROM EmailAdministrationSettings"
        )
        if not result["records"]:
            self.return_values["is_enabled"] = False
            self.logger.warning(
                "Could not read EmailAdministrationSettings — assuming Enhanced Email is disabled."
            )
            return

        enabled = result["records"][0].get("IsEnhancedEmailEnabledEnabled", False)
        self.return_values["is_enabled"] = enabled

        if enabled:
            self.logger.info("Enhanced Email is ENABLED.")
        else:
            self.logger.warning("Enhanced Email is DISABLED.")
