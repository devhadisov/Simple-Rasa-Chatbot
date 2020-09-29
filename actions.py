from typing import Dict, Text, Any, List, Union, Optional

from rasa_sdk import Tracker
from rasa_sdk.forms import FormAction
from rasa_sdk.forms import Action
from rasa_sdk.forms import REQUESTED_SLOT
from rasa_sdk.events import SlotSet
from rasa_sdk.events import ActionExecuted
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher

import requests
import logging
import json
import datetime

logger = logging.getLogger(__name__)


class get_data_form(FormAction):
    """Custom action for existing user queries"""

    def name(self) -> Text:
        """Unique identifier of the form"""
        return "new_project_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        return ["address"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """A dictionary to map required slots to
            - an extracted entity
            - intent: value pairs
            - a whole message
            or a list of them, where a first match will be picked"""
        return {
            "address": [
                self.from_text(),
            ],
        }

    def request_next_slot(self,
                          dispatcher,  # type: CollectingDispatcher
                          tracker,  # type: Tracker
                          domain  # type: Dict[Text, Any]
                          ):
        # type: (...) -> Optional[List[Dict]]
        """Request the next slot and utter template if needed,
            else return None"""

        # Check if request for restart
        if tracker.get_slot('address') == '/restart':
            # if so, then restart
            return [FollowupAction('action_restart')]
        else:
            for slot in self.required_slots(tracker):
                if self._should_request_slot(tracker, slot):
                    logger.debug("Request next slot '{}'".format(slot))
                    dispatcher.utter_template("utter_ask_{}".format(slot),
                                              tracker,
                                              silent_fail=False,
                                              **tracker.slots)
                    return [SlotSet(REQUESTED_SLOT, slot)]

            logger.debug("No slots left to request")
            return None

    def submit_data_form(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """use the slot values to access the database through api-gateway"""
        vAddress = tracker.get_slot('address')
        dispatcher.utter_message('Amazing, your address is: ' + vAddress)
        return [AllSlotsReset()]
