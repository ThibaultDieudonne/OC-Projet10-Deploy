# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Flight booking dialog."""

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory, BotTelemetryClient, NullTelemetryClient
from .cancel_and_help_dialog import CancelAndHelpDialog
from .start_date_dialog import StartDateDialog
from .end_date_dialog import EndDateDialog


class TripFindingDialog(CancelAndHelpDialog):
    def __init__(
        self,
        dialog_id: str = None,
        telemetry_client: BotTelemetryClient = NullTelemetryClient(),
    ):
        super(TripFindingDialog, self).__init__(
            dialog_id or TripFindingDialog.__name__, telemetry_client
        )
        self.telemetry_client = telemetry_client
        text_prompt = TextPrompt(TextPrompt.__name__)
        text_prompt.telemetry_client = telemetry_client

        waterfall_dialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.start_date_step,
                self.end_date_step,
                self.budget_step,
                self.final_step,
            ],
        )
        waterfall_dialog.telemetry_client = telemetry_client

        self.add_dialog(text_prompt)
        # self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            StartDateDialog(StartDateDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(
            EndDateDialog(EndDateDialog.__name__, self.telemetry_client)
        )
        self.add_dialog(waterfall_dialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for destination."""
        trip_details = step_context.options
        if trip_details.destination is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("To what city would you like to travel?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(trip_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Prompt for origin city."""
        trip_details = step_context.options

        # Capture the response to the previous step's prompt
        trip_details.destination = step_context.result
        if trip_details.origin is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("From what city will you be travelling?")
                ),
            )  # pylint: disable=line-too-long,bad-continuation

        return await step_context.next(trip_details.origin)

    async def start_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        trip_details = step_context.options

        trip_details.origin = step_context.result
        if not trip_details.start_date:
            return await step_context.begin_dialog(
                StartDateDialog.__name__, trip_details.start_date
            )

        return await step_context.next(trip_details.start_date)


    async def end_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        trip_details = step_context.options

        trip_details.start_date = step_context.result
        if not trip_details.end_date:
            return await step_context.begin_dialog(
                EndDateDialog.__name__, trip_details.end_date
            )

        return await step_context.next(trip_details.end_date)

    async def budget_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        trip_details = step_context.options
        trip_details.end_date = step_context.result
        if trip_details.budget is None:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("What is your maximum budget per person?")
                ),
            )

        return await step_context.next(trip_details.budget)


    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """Complete the interaction and end the dialog."""
        if step_context.result:
            trip_details = step_context.options
            trip_details.budget = step_context.result

            return await step_context.end_dialog(trip_details)

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        """Ensure time is correct."""
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
